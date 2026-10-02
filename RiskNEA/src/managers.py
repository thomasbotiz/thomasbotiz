import random
import pathlib
import json
import copy 
import time

from model import *
from ai_controller import *
from console import *
from gui import *

class Manager:
    def __init__(self):
        pass

    def _is_compatible_with_ai(self, game: Game) -> bool:
        return (game.metadata.rules.FORTIFICATION == FortifyRules.ADJACENT and
                game.metadata.rules.MAP == MapRules.TRADITIONAL and
                game.metadata.rules.RECRUITMENT == RecruitmentRules.PROGRESSIVE and
                game.metadata.rules.PLACEMENT == PlacementRules.AUTOMATIC_PLACEMENT and
                game.metadata.rules.WIN_CONDITION == WinConditionRules.HUNDRED_PERCENT
               )
    
    def _get_ai_only_rules(self) -> GameRules:
        return GameRules(
                        PLACEMENT=PlacementRules.AUTOMATIC_PLACEMENT,
                        MAP=MapRules.TRADITIONAL,
                        RECRUITMENT=RecruitmentRules.PROGRESSIVE,
                        FORTIFICATION=FortifyRules.ADJACENT, 
                        WIN_CONDITION=WinConditionRules.HUNDRED_PERCENT
                        )

    def _create_ai_only_game(self, id: int, game_mode: GameMode, player_count: int) -> Game:
        return Game.create(GameMetadata(
                                        id, 
                                        datetime.now().isoformat(),
                                        game_mode,
                                        [Player(i, f"ai_{i}", "") for i in range(player_count)],
                                        self._get_ai_only_rules()
                                       )
                           )
    
    def _get_latest_generation_index(self) -> int:
        generations_files = self._get_all_generation_files()
        ids = [int(generation_file.name[10:-5]) for generation_file in generations_files]#generationXX.json[10:-5] = XX for any XX 
        return max(ids, default=-1)

    def _get_generation_from_index(self, id: int) -> Optional[list[AIChromosome]]:
        """
        Method to get the AI Chromosomes from a generation
        with a specified index

        Parameters
        ----------
        id : int
            The index of the requested generation

        Returns
        Optional[list[AIChromosome]]
            If there is a file corresponding to the index, return the 
            generation chromosomes associated else None
        
        Notes
        -----
        "Generation" is 10 digits long, .json at the end is 5 digits long, so the number resides
        between the splice segment 10:-5.
        """
        generations_files = self._get_all_generation_files()
        for file in generations_files:
            if int(file.name[10:-5]) == id:
                generation = self._parse_generation_file(file)
                return generation   
        
    def _get_best_performing_chromosome(self) -> AIChromosome:
        """
        Gets the best performing chromosome
        from the most recent generation
        
        Returns
        -------
        AIChromosome
            The best performing AI
        """
        latest_index = self._get_latest_generation_index()
        generation = self._get_generation_from_index(latest_index)
        return max(generation, key=lambda chromosome: chromosome.average_fitness)

    def _get_all_generation_files(self) -> list[pathlib.Path]:
        directory = pathlib.Path(__file__).parent.parent / "generations"
        directory.mkdir(exist_ok=True)
        generation_files = list(directory.glob("generation*.json"))
        return generation_files
    
    def _parse_generation_file(self, generation_file: pathlib.Path) -> list[AIChromosome]:
        with open(generation_file, "r") as generation:
            return [AIChromosome(**chromosome_data) for chromosome_data in json.load(generation)]
    
    def _save_generation(self, generation: list[AIChromosome]) -> list[AIChromosome]:
        file_index = self._get_latest_generation_index() + 1
        new_file = pathlib.Path(__file__).parent.parent / "generations" / f"generation{file_index}.json"
        serialised_generation = [chromosome.__dict__ for chromosome in generation]
        with open(new_file, "x") as json_file:
            json.dump(serialised_generation, json_file, indent=4)

    def _initialise_generation(self) -> list[AIChromosome]:
        hyperparameters_path = pathlib.Path(__file__).parent.parent / "hyperparameters.json"
        with open(hyperparameters_path, "r") as json_data:
            num_ai = json.load(json_data)["POPULATION_SIZE"]
        generation = [AIChromosome() for _ in range(num_ai)]
        self._save_generation(generation)
        return generation

class LocalPlayManager(Manager):
    def __init__(self):
        super().__init__()
        self.available_colours = set()
        self.ai_controllers = []
    
    def play(self) -> None:
        user_inp = input("Would you like to load a save file or start from a new save file? (NEW/LOAD/RETURN) ").lower()
        if user_inp == "new":
            num_players, num_ai = self.get_player_and_ai_count()

            generation_index = self._get_latest_generation_index()
            if generation_index == -1:#No generations present
                print("Warning! No AIs could be located. You must train an AI first to play with them!")
                num_ai = 0

            num_humans = num_players - num_ai
            ai_names = ["Andrew", "Bert", "Charles", "Dennis", "Elias"]
            colours = ["crimson", "salmon", "brown", "yellow", "cyan", "green"]
            players = self.create_players(num_players, num_humans, colours, ai_names)
            if num_ai > 0: 
                num_easy, num_medium, num_hard = self.get_ai_difficulties(num_ai)
                best_chromosome = self._get_best_performing_chromosome()
                print("Warning! Cannot use special rules if playing with at least one AI player. ")
                print("""
                        Warning! Loading a different save file during a game with AI enabled is not actively supported.
                        To safely load from a save file restart the program and load from the starting menu.  
                      """
                    )
                rules = self._get_ai_only_rules()
            else:
                while True:
                    inp = input("You are playing with no AI. Would you like to play with custom settings? (Y/N)").lower()
                    if inp == "y":
                        rules = self.create_rules(num_players)
                        break
                    elif inp == "n":
                        rules = self._get_ai_only_rules()
                        break
                    else:
                        print("Invalid input!")
            metadata = GameMetadata(0, datetime.now().isoformat(), GameMode.LOCAL_PLAY, players, rules)
            self.game = Game.create(metadata)
            if num_ai > 0:
                for i in range(num_humans+1, num_players+1):
                        if num_easy:
                            num_easy -= 1
                            self.ai_controllers.append(AIController(players[i-1], self.game, best_chromosome, "Easy"))
                        elif num_medium: 
                            num_medium -= 1
                            self.ai_controllers.append(AIController(players[i-1], self.game, best_chromosome, "Medium"))
                        elif num_hard:
                            num_hard -= 1
                            self.ai_controllers.append(AIController(players[i-1], self.game, best_chromosome, "Hard"))
        elif user_inp == "load":
            while True:
                try:
                    save_file = input("Enter save file name: ")
                    self.game = Game.load(save_file)
                    metadata = self.game.metadata
                    rules = metadata.rules
                    break
                except Exception as e: 
                    print("Invalid file inputted!")
                    print(e)
            
            if self._is_compatible_with_ai(self.game):
                best_chromosome = self._get_best_performing_chromosome()
                
                num_ai = len(self.game.players)
                while num_ai == len(self.game.players):
                    num_ai = 0
                    for player in self.game.players:
                        while True:
                            print(f"Player: {player.name}")
                            inp = input("Is this player AI or human?(AI/HUMAN) ").lower()
                            if inp == "ai":
                                num_ai += 1
                                while True:
                                    difficulty = input("Input AI difficulty: (Easy/Medium/Hard) ").capitalize()
                                    if difficulty not in ["Easy", "Medium", "Hard"]:
                                        print("Invalid input!")
                                    else:
                                        self.ai_controllers.append(AIController(player, self.game, best_chromosome, difficulty))
                                        break
                                break
                            elif inp != "human":
                                print("Invalid input!")
                            else:
                                break

                    if num_ai == len(self.game.players):
                        print("Cannot play with all players being AI!")
            else:
                print("This game is not compatible with AI!")
        else:
            return 
        self.game.event_bus.subscribe(LoadGameEvent, self._on_load_game_event)

        while True:
            inp = input("Would you like a short tutorial (Y/N)? ").lower()
            if inp == "y":
                self.__display_tutorial(rules)
                break
            elif inp == "n":
                break
            else:
                print("Invalid input!")

        while True:
            inp = input("Would you like to play using the console or GUI? (DEBUG/GUI) ").lower()
            if inp == "debug":
                self.controller = ConsoleController(self.game)
                self.view = ConsoleView(self.game)
                break
            elif inp == "gui":
                self.controller = LocalPlayGUI(self.game, self.ai_controllers)
                break
            else:
                print("Invalid input!")
        self.main()
    
    def _on_load_game_event(self, event: LoadGameEvent) -> None:
        if not event.error:
            self.ai_controllers = []

    def main(self) -> None:
        self.game.start()
        if isinstance(self.controller, LocalPlayGUI):
            self.controller.start()
        elif isinstance(self.controller, ConsoleController):
            while True: 
                try:
                    if self.game.current_player in [ai_controller.player for ai_controller in self.ai_controllers]: 
                        print("The AI is thinking!")
                        time.sleep(2)
                    else:
                        self.controller.parse_request(input())
                    self.game.step()
                except Exception as e:
                    print(e)
    
    def __display_tutorial(self, game_rules: GameRules):
        print("""
                In the classic World Domination RISK® game of military strategy, you are
                battling to conquer the world. To win, you must launch daring attacks,
                defend yourself on all fronts, and sweep across vast continents with
                boldness and cunning. But remember, the dangers, as well as the rewards,
                are high. Just when the world is within your grasp, your opponent might
                strike and take it all away!
              
                Each of your turns consists of three steps, in this order:
                1. Getting and placing new armies;
                2. Attacking, if you choose to, by rolling the dice;
                3. Fortifying your position
              
                Each continent gives a number of extra units per turn:
                Australia - 2 units
                South America, Africa - 3 units
                Europe, North America - 5 units
                Asia - 7 units
              
                To Attack. First click the territory you are attacking from and the
                territory you would like to attack.
                Before rolling, both you and your opponent must announce the number
                of dice you intend to roll, and you both must roll at the same time.
                You, the attacker, will roll 1,2 or 3 red dice: You must have at least one
                more army in your territory than the number of dice you roll. Hint: The
                more dice you roll, the greater your odds of winning. Yet the more dice
                you roll, the more armies you may lose, or be required to move into a
                captured territory.
                The defender will roll either 1 or 2 white dice: To roll 2 dice, he or she
                must have at least 2 armies on the territory under attack. Hint: The more
                dice the defender rolls, the greater his or her odds of winning-but the
                more armies he or she may lose.
              
                As soon as you defeat the last opposing army on
                a territory, you capture that territory and must occupy it immediately. To
                do so, move in at least as many armies as the number of dice you rolled in
                your last battle
              
                You may end your attack(s) at any time. If you have
                captured at least one territory, you get a Risk Card.
              
                Eliminating an opponent. If during your turn you eliminate an
                opponent by defeating his or her last army on the game board, you win any
                RISK cards that player has collected.
                If winning them gives you 6 or more cards, you must immediately trade
                in enough sets to reduce your hand to 4 or fewer cards, but once your
                hand is reduced to 4,3, or 2 cards, you must stop trading.
                But if winning them gives you fewer than 6, you must wait until the
                beginning of your next turn to trade in a set.
                Note: When you draw a card from the deck at the end of your turn (for
                having won a battle), if this brings your total to 6, you must wait until
                your next turn to trade in.
              
                No matter what you've done on your turn, you may, if you wish, end your
                turn by fortifying your position. You are not required to win a battle or even
                to try an attack to do so. Some players refer to this as the “free move.”
                To fortify your position, move as many armies as you'd like from one (and
                only one) of your territories into one (and only one) of your adjacent
                territories. Remember to move troops towards borders where they can help
                in an attack
              """
              )
        
        if game_rules.PLACEMENT == PlacementRules.AUTOMATIC_PLACEMENT:
            print("""
                  You are playing with automatic placement rules!

                  You will begin the game with a random selection
                  of territories and units. Make careful decisions 
                  to choose which territories you want to cling onto
                  most!
                  """
                  )
        
        elif game_rules.PLACEMENT == PlacementRules.MANUAL_PLACEMENT:
            print("""
                You are playing with manual placement rules!
                  
                You will place units on a territory in your turn order,
                one at a time. At first, you may only place on an
                uncaptured territory, but once all territories have
                been claimed you must place on a previously owned
                territory. 
                  """)
        
        if game_rules.RECRUITMENT == RecruitmentRules.FIXED:
            print("""
                You are playing with fixed recruitment rules!
                When you trade in a set, you get a different
                number of units depending on the types of cards
                traded in. 
                  
                Three infantry - 4 units
                Three cavalry - 6 units
                Three artillery- 8 units
                One infantry, one cavalry and one artillery - 10 units
                """)
            
        elif game_rules.RECRUITMENT == RecruitmentRules.PROGRESSIVE:
            print("""
                You are playing with progressive recruitment rules!
                Trading in sets of cards will reward you with an increasing
                number of bonus units as the game goes on. 
                
                Set 1 - 4 units
                Set 2 - 6 units
                Set 3 - 8 units
                Set 4 - 10 units
                Set 5 - 12 units
                Set 6 - 15 units
                Set 7+ 5 units from the last trade e.g. 7 - 20 units, 8 - 25 units...
                """)

        if game_rules.MAP == MapRules.TRADITIONAL:
            print("""
                You are playing on the Traditional map!
                The classic world map divides the globe into 42 territories
                across 6 continents.
                """)
            
        elif game_rules.MAP == MapRules.ANTIQUITY:
            print("""
                You are playing on the Antiquity map!
                
                This gamemode features a smaller map of 12 territories
                for smaller games. Set in ancient Roman times!
                """)

        if game_rules.WIN_CONDITION == WinConditionRules.HUNDRED_PERCENT:
            print("""
                You are playing with the 100% win condition!

                To claim victory, you must conquer every single territory
                on the map. 
                """)
            
        elif game_rules.WIN_CONDITION == WinConditionRules.SEVENTY_PERCENT:
            print("""
                You are playing with the 70% win condition!
                  
                Control 70% of the territories on the map to win the game.
                """)

        if game_rules.FORTIFICATION == FortifyRules.ADJACENT:
            print("""
                You are playing with adjacent fortification rules!
                At the end of your turn, you may move units between any
                two of your territories that are connected through a
                chain of friendly territories. 
                """)
            
        elif game_rules.FORTIFICATION == FortifyRules.CONTIGUOUS:
            print("""
                You are playing with contiguous fortification rules!
                At the end of your turn, you may move units between any
                two of your territories that share a direct border.
                """)

    def get_player_and_ai_count(self) -> tuple[int, int]:
        while True:
            player_count = input("Input total number of players playing between 2 and 6: ")
            if not player_count.isdigit():
                print("Input an integer!")
                continue
            player_count = int(player_count)
            if not 2 <= player_count <= 6:
                print("The number of total players must be between 0 and 6!")
                continue
            break
        while True:
            ai_count = input("Input total number of AI players between 0 and 5: ")
            if not ai_count.isdigit():
                print("Input an integer!") 
                continue
            ai_count = int(ai_count)
            if ai_count >= player_count: 
                print("Must have less AI than total players!")
                continue
            elif not 0 <= ai_count <= 5: 
                print("Number of AI must be between 0 and 5!")
                continue
            return (player_count, ai_count)

    def create_players(self, num_players: int, num_humans: int, available_colours: set[str], available_ai_names: list[str]) -> list[Player]:
        players = []
        for i in range(1, num_players+1):
            if i <= num_humans:
                name = self.get_player_name()
                colour = self.get_valid_player_colour(available_colours)
            elif i > num_humans: 
                name = random.choice(available_ai_names)
                available_ai_names.remove(name)
                colour = random.choice(available_colours)
            available_colours.remove(colour)
            players.append(Player(i, name, colour))
        return players

    def get_ai_difficulties(self, num_ai: int) -> tuple[int, int, int]:#Easy, Medium, Hard
        while True: 
            num_easy = input("Input number of easy AI: ")
            num_medium = input("Input number of medium AI: ")
            num_hard = input("Input number of hard AI: ")
            if any([not ai_difficulty.isdigit() for ai_difficulty in [num_easy, num_medium, num_hard]]):
                print("At least one value inputted is not an integer!")
                continue
            num_easy = int(num_easy)
            num_medium = int(num_medium)
            num_hard = int(num_hard)
            
            if num_easy + num_medium + num_hard != num_ai:
                print(f"Number of easy, medium and hard AI must be equal to {num_ai}!")
            else:
                return (num_easy, num_medium, num_hard) 

    def get_player_name(self) -> str: 
        while True:
            name = input("Input your name(between 1 and 12 characters long): ")
            if 1 <= len(name) <= 12:
                return name
            else:
                print("Name is of an invalid length!")
    
    def get_valid_player_colour(self, available_colours: set[str]) -> str:
        while True:
            print(f"Available colours: ")
            print(*available_colours)
            colour = input("Input your colour from the list above: ")
            if colour not in available_colours:
                print("You cannot choose that colour because it is invalid!")
            else:
                return colour

    def create_rules(self, num_players: int) -> GameRules:
        while True:
            placement_rules = input("Input placement rules: (AUTOMATIC/MANUAL) ").lower()
            if placement_rules == "automatic":
                placement = PlacementRules.AUTOMATIC_PLACEMENT
            elif placement_rules == "manual":
                placement = PlacementRules.MANUAL_PLACEMENT
            else:
                print("Invalid input!")
                continue
            
            if num_players > 4:
                print("Cannot play with the antiquity map because there are too many players!")
                print("Defaulting to Traditional map. To avoid this, play with 4 or less people.")
                map_type = MapRules.TRADITIONAL
            else:
                map_type_rules = input("Input map type (TRADITIONAL/ANTIQUITY): ").lower()
                if map_type_rules == "traditional":
                    map_type = MapRules.TRADITIONAL
                elif map_type_rules == "antiquity":
                    map_type = MapRules.ANTIQUITY
                else:
                    print("Invalid input!")
                    continue

            recruitment_rules = input("Input recruitment rules (PROGRESSIVE/FIXED): ").lower()
            if recruitment_rules == "fixed":
                recruitment = RecruitmentRules.FIXED
            elif recruitment_rules == "progressive":
                recruitment = RecruitmentRules.PROGRESSIVE
            else:
                print("Invalid input!")
                continue

            fortification_rules = input("Input fortification rules (ADJACENT/CONTIGUOUS): ").lower()
            if fortification_rules == "adjacent":
                fortification = FortifyRules.ADJACENT
            elif fortification_rules == "contiguous":
                fortification = FortifyRules.CONTIGUOUS
            else:
                print("Invalid input!")
                continue

            win_condition_rules = input("Input win condition (100%/70%):  ")
            if win_condition_rules == "100%":
                win_condition = WinConditionRules.HUNDRED_PERCENT
            elif win_condition_rules == "70%":
                win_condition = WinConditionRules.SEVENTY_PERCENT
            else:
                print("Invalid input!")
                continue
            return GameRules(PLACEMENT=placement,
                            MAP=map_type,
                            RECRUITMENT=recruitment,
                            FORTIFICATION=fortification,
                            WIN_CONDITION=win_condition
                            )

class TrainingManager(Manager):
    def __init__(self):
        super().__init__()
        hyperparameters_path = pathlib.Path(__file__).parent.parent / "hyperparameters.json"
        with open(hyperparameters_path, "r") as json_data:
            parameters = json.load(json_data)

        self.POPULATION_SIZE = parameters["POPULATION_SIZE"]
        self.EPISODES_PER_GENERATION = parameters["EPISODES_PER_GENERATION"]
        self.TOURNAMENT_SIZE = parameters["TOURNAMENT_SIZE"]
        self.ELITISM = parameters["ELITISM"]
        self.CROSSOVER_RATE = parameters["CROSSOVER_RATE"]
        self.MUTATION_RATE = parameters["MUTATION_RATE"]
        self.MUTATION_STANDARD_DEVIATION = parameters["MUTATION_STANDARD_DEVIATION"]
        self.MAX_TURNS_UNTIL_TIMEOUT = parameters["MAX_TURNS_UNTIL_TIMEOUT"]
        self.TIMEOUT_PENALTY = parameters["TIMEOUT_PENALTY"]
        self.REWARD_FOR_POSITION = parameters["REWARD_FOR_POSITION"]
        self.PLAYERS_PER_GAME = 6

        generation_index = self._get_latest_generation_index()
        if generation_index == -1:#No generations present
            self.generation = self._initialise_generation()
        else:
            self.generation = self._get_generation_from_index(generation_index)

    def learn(self) -> None:
        #If a user restarts the program, it will be restarting training
        #from an already trained generation. If it is already trained, then
        #create the next generation
        try:
            generations_simulated = int(input("How many generations would you like to simulate?"))
        except Exception as e:
            print("Invalid input!")
            print(e)
            return
    
        if any(chromosome.average_fitness for chromosome in self.generation):
            self.generation = self.__create_next_generation(self.generation)

        for _ in range(generations_simulated):
            for i in range(self.EPISODES_PER_GENERATION): 
                self.__simulate_episode(i)
                print("Episode completed!")

            self._save_generation(self.generation)
            self.generation = self.__create_next_generation(self.generation)

    def __create_next_generation(self, previous_generation) -> list[AIChromosome]:
        print(f"Generation completed!")
        print("Current Generation details:")
        print(f"Number of AI: {len(previous_generation)}")
        for gene in previous_generation[0].__dict__:
            if gene != "fitness" and gene != "games_played":
                print(f"Gene {gene} average value: {sum(getattr(chromosome, gene) for chromosome in previous_generation)/len(previous_generation)}")
            else:
                print(f"{gene} average value: {sum(getattr(chromosome, gene) for chromosome in previous_generation)/len(previous_generation)}")

        next_generation = []
        self.__perform_elitism(previous_generation, next_generation)
        self.__perform_tournament_crossover(previous_generation, next_generation)
        return next_generation
            
    def __simulate_episode(self, i: int):
        training_game = self._create_ai_only_game(i, GameMode.TRAINING, self.PLAYERS_PER_GAME)
        chromosomes_in_play = random.sample(self.generation, self.PLAYERS_PER_GAME)

        ai_controllers = [AIController(training_game.players[i], training_game, chromosomes_in_play[i], "Hard") for i in range(self.PLAYERS_PER_GAME)]
        training_game.start()
        while (not training_game.finished and training_game.stats.turns_played <= self.MAX_TURNS_UNTIL_TIMEOUT):
            training_game.step()
        print(f"Turns played: {training_game.stats.turns_played}")

        for ai_controller in ai_controllers:
            self.__apply_fitness_function_to_chromosome(ai_controller)

    def __perform_elitism(self, completed_generation: list[AIChromosome], new_generation: list[AIChromosome]) -> None:
        elites = sorted(completed_generation, key=lambda chromosome: chromosome.average_fitness, reverse=True)[:self.ELITISM]
        for elite in elites:
            elite.fitness = 0
            elite.games_played = 0
        new_generation.extend(sorted(completed_generation, key=lambda chromosome: chromosome.average_fitness, reverse=True)[:self.ELITISM])

    def __perform_tournament_crossover(self, previous_generation: list[AIChromosome], new_generation: list[AIChromosome]) -> None:
        while(len(new_generation) < self.POPULATION_SIZE):
            parents = [max(random.sample(previous_generation, self.TOURNAMENT_SIZE), key=lambda chromosome: chromosome.average_fitness) for _ in range(2)]
            children = [AIChromosome.create_from_crossover(parents[0], parents[1]) if self.CROSSOVER_RATE > random.random() else AIChromosome(**parents[i].__dict__) for i in range(2)]
            for child in children:
                child.mutate(self.MUTATION_RATE, self.MUTATION_STANDARD_DEVIATION)
                child.fitness = 0
                child.games_played = 0

            if len(new_generation) + 1 == self.POPULATION_SIZE:
                new_generation.append(children[0])
            else:
                new_generation.extend(children)

    def __apply_fitness_function_to_chromosome(self, ai_controller: AIController) -> None:
        if ai_controller.game.stats.turns_played > self.MAX_TURNS_UNTIL_TIMEOUT:
            ai_controller.chromosome.fitness += self.TIMEOUT_PENALTY
        elif ai_controller.game.players[0] == ai_controller.player:
            ai_controller.chromosome.fitness += self.REWARD_FOR_POSITION["1"]
        else:
            #Players who lose first are at the first index of the eliminated_players list, this algorithm calculats the correct position
            #Of each player
            position = str(len(ai_controller.game.eliminated_players) + 1 - ai_controller.game.eliminated_players.index(ai_controller.player))
            ai_controller.chromosome.fitness += self.REWARD_FOR_POSITION[position]
        ai_controller.chromosome.games_played += 1   

class SimulationManager(Manager):
    def __init__(self):
        super().__init__()
        
    def simulate(self) -> None:
        num_wins_tracker = {}
        while True:
            try:
                file_name = input("Input the name of the file for the simulated game: ")
                game_being_simulated = Game.load(file_name)
                break
            except Exception as e:
                print("An error arose while trying to parse the save file!")
                print(e)

        num_simulations = int(input("How many games would you like to simulate? \n More games takes longer to process but give more accurate results. "))
        if num_simulations == 0:
            print("Must simulate at least one game!")
            return
        
        if not self._is_compatible_with_ai(game_being_simulated):
            print("Cannot simulate this game! The rules are incompatible with the AI!")
            return
        
        generation_index = self._get_latest_generation_index()
        if generation_index == -1:#No generations present
            print("Cannot simulate this game! No AIs are present! You must train an AI first!")
            return

        for player in game_being_simulated.players:#only currently active players
            num_wins_tracker[player.id] = 0

        best_chromosome = self._get_best_performing_chromosome()
        for i in range(num_simulations):
            simulation = copy.deepcopy(game_being_simulated)  
            ai_controllers = [AIController(player, simulation, best_chromosome, "Hard") for player in simulation.players]
            simulation.start()
            while (not simulation.finished and simulation.stats.turns_played < 1000):#Games automatically timeout after 1000 moves
                simulation.step()
            
            if simulation.stats.turns_played < 1000:
                if len(simulation.players) == 1:
                    winning_player = simulation.players[0]
                    print(f"{i+1}: Winner - {winning_player.name}")
                    num_wins_tracker[winning_player.id] += 1
            else:
                print("Game took too long to finish, timed out!")
        total_games_played = sum(num_wins_tracker.values())
        if total_games_played == 0:
            print("Warning! Not one game managed to complete. This is most likely because the AI was not trained for long enough. Train the AI for longer!")
        else:
            for player_id in num_wins_tracker:
                player = game_being_simulated.data.player_lookup[player_id]
                print(f"Player {player.name} win chances: {str(100*num_wins_tracker[player.id]/total_games_played)[:4]}%")#2dp
