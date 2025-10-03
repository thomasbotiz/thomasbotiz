import pygame
import random
import pathlib
import gymnasium as gym
import numpy as np
from dataclasses import dataclass

pygame.init()

class GameEnv(gym.Env):
    def __init__(self, game_type = "Human"):
        super().__init__()
        self.game_type = game_type
        self.game_state = "Start"
        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        pygame.display.set_caption(Config.WINDOW_NAME)
        self.player = Player(bird["frames"]["mid"], Config.PLAYER_X_POS, Config.PLAYER_Y_POS, 0, 0)
        self.background = Object(background_image, 0, 0)
        self.base = Base(base_image, 0, Config.WINDOW_HEIGHT*0.9, Config.SCROLL_SPEED, 0)
        self.pipe_cooldown = 0
        self.pipes = [] 
        self.score = 0
        self.previous_score = 0
        self.score_text = Text()

        if self.game_type == "Training":
            self.game_state = "Playing"
            self.observation_space = gym.spaces.Box(low = 0, high = Config.WINDOW_HEIGHT, shape=(7,), dtype=np.float32)
            self.action_space = gym.spaces.Discrete(2)

    def step(self, action):
        #user events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_type == "Human":
                        self.game_state = "Playing"
                        self.player.jump()
        #ai events
        if action == 1:
            if self.player.is_alive:
                self.player.jump()

        #if human is playing, have a "death animation"
        #if an AI is playing, train faster by restarting immediately
        if self.game_state == "Playing":
            if (self.game_type == "Training" and self.player.is_alive) or (self.game_type == "Human" and self.player.rect.right > 0):
                self.update_player()
                self.update_pipes()
                self.base.update()
            else:
                self.reset()

        self.clock.tick(Config.FPS)
        self.render()

        if self.game_type == "Training":
            obs = self.get_observation()
            reward = self.calculate_reward()
            done = not self.player.is_alive
            return obs, reward, done, False, {}

    def render(self) -> list:
        self.background.render(self.window)
        self.base.render(self.window) 

        for pipe in self.pipes:
            pipe.render(self.window)
        
        self.score_text.render(self.window, self.score)

        self.player.render(self.window)
        pygame.display.update()
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.score = 0
        self.player = Player(bird["frames"]["mid"], Config.PLAYER_X_POS, Config.PLAYER_Y_POS, 0, 0)
        self.pipes = []
        self.pipe_cooldown = Config.PIPE_COOLDOWN_TIMER
        self.score_text = Text()

        if self.game_type == "Human":
            self.game_state = "Start"
        
        return self.get_observation(), {}

    def get_observation(self):
        next_pipe = None
        previous_pipe = None
        for pipe in self.pipes:
            if pipe.rect.x > self.player.rect.x and not pipe.is_top:
                next_pipe = pipe
                break
            if pipe.rect.x <= self.player.rect.x and not pipe.is_top:
                previous_pipe = pipe
                break
        
        if previous_pipe:
            previous_pipe_dx = previous_pipe.rect.x - self.player.rect.x
            previous_pipe_dy = previous_pipe.rect.y - self.player.rect.y
        else:
            previous_pipe_dx = 999
            previous_pipe_dy = 0
        
        if next_pipe:
            next_pipe_dx = next_pipe.rect.x - self.player.rect.x
            next_pipe_dy = next_pipe.rect.y - self.player.rect.y
        else:
            next_pipe_dx = 999
            next_pipe_dy = 0
        
        return np.array([
            self.player.rect.y,
            self.player.yv,
            next_pipe_dx,
            next_pipe_dy,
            previous_pipe_dx,
            previous_pipe_dy,
            self.check_player_between_pipes()],
            dtype=np.float32
            )
    
    def calculate_reward(self):
        reward = 0.1
        if not self.player.is_alive:
            reward -= 100
        
        if self.player.rect.y < self.player.image.get_height():#discourage touching the ceiling
            reward -= 1
        
        if self.score > self.previous_score:
            self.previous_score = self.score
            reward += 10
            
        return reward

    def handle_pipe_generation(self):
        if self.check_to_spawn_pipes():
            self.generate_pipes()
            self.pipe_cooldown = Config.PIPE_COOLDOWN_TIMER
        else:
            self.pipe_cooldown -= 1

    def update_pipes(self):
        self.handle_pipe_generation()   
        for pipe in self.pipes:
            pipe.update()
            if not pipe.is_top and pipe.rect.x + pipe.image.get_width() < self.player.rect.x and not pipe.scored:
                self.score += 1
                pipe.scored = True
        self.pipes = [pipe for pipe in self.pipes if pipe.rect.x > -pipe.image.get_width()]

    def generate_pipes(self):
        gap_y = random.randint(Config.TOP_PIPE_MIN_DEPTH + Config.PIPE_GAP_HEIGHT, Config.TOP_PIPE_MAX_DEPTH)
        
        top_pipe = Pipe(pipe_image, Config.WINDOW_WIDTH, 
                        gap_y - Config.PIPE_GAP_HEIGHT - pipe_image.get_height(),
                        Config.SCROLL_SPEED, 0, is_top=True
                        )
 
        bottom_pipe = Pipe(pipe_image,
                    Config.WINDOW_WIDTH, gap_y,
                    Config.SCROLL_SPEED, 0, is_top=False
                    )
                
        self.pipes.extend([top_pipe, bottom_pipe])

    def check_to_spawn_pipes(self):
        if self.pipe_cooldown == 0:
            return True
        else:
            return False

    def check_player_between_pipes(self):
        for pipe in self.pipes:
            if pipe.rect.left <= self.player.rect.centerx <= pipe.rect.right:
                return True   
        return False
    
    def handle_player_collisions(self):
        if self.player.collides_with(self.base):
            self.handle_base_collision()
            return
        
        for pipe in self.pipes:
            if self.player.collides_with(pipe):
                self.handle_pipe_collision(pipe)
                break

    def update_player(self):
        self.player.update()
        self.handle_player_collisions()

    def handle_base_collision(self):
        self.player.yv = 0
        self.player.rect.bottom = self.base.rect.y
        self.player.is_alive = False    

    def handle_pipe_collision(self, pipe):
        self.player.is_alive = False
        
        if self.check_player_between_pipes():
            self.player.yv = 0
            if not pipe.is_top:
                self.player.rect.bottom = pipe.rect.y

class Object:
    def __init__(self, image, x, y):
        self.image = image
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())

    def render(self, window):
        window.blit(self.image, self.get_position())

    def translate(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def set_image(self, image):
        self.image = image
    
    def set_position(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def get_position(self):
        return (self.rect.x, self.rect.y)
 
    def collides_with(self, object):
        if self.rect.colliderect(object.rect):
            return True
        else:
            return False
    
    def update(self): 
        #Business logic gets polymorphed here
        pass    

class DynamicObject(Object): #Objects with velocity 
    def __init__(self, image, x, y, xv, yv):
        super().__init__(image, x, y)
        self.xv = xv
        self.yv = yv

    def move(self):
        self.rect.x += self.xv
        self.rect.y += self.yv

    def accelerate(self, xa, ya):
        self.xv += xa
        self.yv += ya

class Player(DynamicObject):
    def __init__(self, image, x, y, xv, yv):
        super().__init__(image, x, y, xv, yv)
        self.image =  image
        self.tilt = 0
        self.is_alive = True
        self.frame_timer = Config.FRAME_TIMER
        self.frame = 0

    def update(self): 
        """ 
        Handles internal physics and animation frames
        """
        if self.is_alive:
            if self.frame_timer == 0:
                self.frame_timer = Config.FRAME_TIMER
                self.next_frame()
            else:
                self.frame_timer -= 1

        if not self.is_alive:
            self.xv = Config.SCROLL_SPEED

        if self.rect.y < 0:
            self.rect.y = 0
            self.yv = Config.GRAVITY

        self.accelerate(0, Config.GRAVITY)
        self.yv = min(self.yv, Config.TERMINAL_VELOCITY)
        self.move()
        self.tilt = max(-self.yv * Config.TILT_SPEED, Config.MAX_DOWN_TILT)

    def next_frame(self):
        self.frame = (self.frame + 1) % 4
        self.image = bird["animation"][self.frame]

    def jump(self):
        if self.is_alive:
            self.yv = -Config.JUMP_FORCE
            self.tilt = Config.MAX_UP_TILT

    def render(self, window):
        window.blit(pygame.transform.rotate(self.image, self.tilt), self.get_position())

class Pipe(DynamicObject):
    def __init__(self, image, x, y, xv, yv, is_top):
        super().__init__(image, x, y, xv, yv)
        self.is_top = is_top
        self.scored = False  # Track if this pipe has been scored
        if is_top:
            self.image = pygame.transform.flip(self.image, False, True)

    def update(self):
        self.move()
    
class Base(DynamicObject):
    def __init__(self, image, x, y, xv, yv):
        super().__init__(image, x, y, xv, yv)

    def update(self):
        self.move()
        if self.rect.x <= -Config.WINDOW_WIDTH:
            self.rect.x = 0
    
class Text:
    def __init__(self):
        self.font = font

    def render(self, window, score):
        text_surface = self.font.render(str(score), True, ("black"))
        # Center the text horizontally at the top of the screen
        text_rect = text_surface.get_rect()
        text_rect.centerx = Config.WINDOW_WIDTH // 2
        text_rect.y = 50
        window.blit(text_surface, text_rect)

@dataclass
class Config:
    #all values in pixels
    #window
    WINDOW_NAME = "Flappy Bird"
    WINDOW_HEIGHT = 500
    WINDOW_WIDTH = 300
    FPS = 60 

    #pipes
    PIPE_WIDTH = 70
    PIPE_GAP_HEIGHT = 150
    TOP_PIPE_MIN_DEPTH = int(WINDOW_HEIGHT / 20)
    TOP_PIPE_MAX_DEPTH = int(WINDOW_HEIGHT * 0.8)
    PIPE_COOLDOWN_TIMER = 90 #spawns a pair every X frames
    
    #Scoreboard
    SCOREBOARD_X = 150
    SCOREBOARD_Y = 150
    FONT_SIZE = 30

    #base, pipe, dead players
    SCROLL_SPEED = -3

    #player/bird
    PLAYER_HEIGHT = 24
    PLAYER_WIDTH = 36
    PLAYER_X_POS = 130
    PLAYER_Y_POS = 175
    GRAVITY = 0.9
    JUMP_FORCE = 12
    TERMINAL_VELOCITY = 16
    FRAME_TIMER = 5 #switch animation frame every X frames
    MAX_UP_TILT = 15#degrees
    MAX_DOWN_TILT = -30#degrees
    TILT_SPEED = 1.5#degrees


script_dir = pathlib.Path(__file__).parent
sprites_dir = script_dir / "sprites"

try:
    background_image = pygame.transform.scale(pygame.image.load(sprites_dir / "background-day.png"), 
                                             (Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
                                             )
    
    game_over_image = pygame.image.load(sprites_dir / "gameover.png")
    game_over_image = pygame.transform.scale(game_over_image, (Config.WINDOW_WIDTH * 0.75, game_over_image.get_height()))
    
    base_image = pygame.image.load(sprites_dir / "base.png")
    base_image = pygame.transform.scale(
        base_image, 
        (Config.WINDOW_WIDTH * 2, base_image.get_height()))
    
    pipe_image = pygame.image.load(sprites_dir / "pipe-green.png")
    pipe_image = pygame.transform.scale(pipe_image, (Config.PIPE_WIDTH, pipe_image.get_height()))
   
    bird_frames = {
        "up": pygame.image.load(sprites_dir/ "yellowbird-upflap.png"),
        "mid": pygame.image.load(sprites_dir/ "yellowbird-midflap.png"),
        "down": pygame.image.load(sprites_dir/ "yellowbird-downflap.png")}
    
    scaled_frames = {}
    for frame_name, frame_img in bird_frames.items():
        scaled_frames[frame_name] = pygame.transform.scale(frame_img, (Config.PLAYER_WIDTH, Config.PLAYER_HEIGHT))
    
    bird = {
        "frames": scaled_frames,
        "animation": [
            scaled_frames["mid"],
            scaled_frames["down"],
            scaled_frames["mid"],
            scaled_frames["up"]]
            }

    font = pygame.font.Font((sprites_dir/ "minecraft_font.ttf"), Config.FONT_SIZE)

except:
    print("Error! One or more files failed to load!")

#If this file is ran, assume player is human
#If the AI file is ran, assume training
if __name__ == "__main__":
    env = GameEnv("Human")
    while True:
        env.step(0)

