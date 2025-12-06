from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Self
from datetime import datetime
import pathlib
import random
import json

from ..utils import State, Command, EventBus, Queue
from .config import RecruitmentConfig
from .rules import *
from ..data import *

class Game:
    def __init__(self, 
                metadata: GameMetadata, 
                data: GameData, 
                stats: GameStats
                ):
        """
        The representation of an atomic game of Risk
            
        Parameters
        ----------
        metadata : GameMetadata
            Container for data specific to the instantiation of the Game object

        data : GameData
            Container for data about current state of the game components

        stats : GameStats
            Container for high-level statistics of the game

        Notes
        -----
        To begin the game, call game.start(). 
        """
        self.metadata = metadata
        self.data = data
        self.stats = stats

    @property 
    def current_player(self) -> Player:
        """
        Returns the first player in the queue
        """
        return self.data.player_queue.head

    @property 
    def event_bus(self) -> EventBus:
        """
        Returns the Event Bus in data
        """
        return self.data.event_bus

    @property 
    def state(self) -> State:
        """
        Returns the State in data
        """
        return self.data.state
    
    @state.setter
    def state(self, new_state: State):
        """
        Replaces the current State
        """
        self.data.state = new_state

    @property 
    def board(self) -> Board:
        """
        Returns the Board in data
        """
        return self.data.board
    
    @property 
    def players(self) -> list[Player]:
        """
        Returns the players in data
        """
        return self.data.players

    @property 
    def eliminated_players(self) -> list[Player]:
        """
        Returns the eliminated players in data
        """
        return self.data.eliminated_players
    
    @property 
    def player_queue(self) -> Queue:
        """
        Returns the player queue in data
        """
        return self.data.player_queue
    
    @property 
    def deck(self) -> Deck:
        """
        Returns the Deck in data
        """
        return self.data.deck
    
    @property 
    def rules(self) -> GameRules:
        """
        Returns the Rules in data
        """
        return self.data.rules
    
    def __str__(self) -> str:
        """
        Returns information about the game

        Returns
        -------
        str     
            A representation of the game's metalevel details
        
        Notes
        -----
        the string should contain:
        the game_id, timestamp, rules, game_mode, current_phase, current_player
        """
        message = ""
        message += f"Game ID: {self.metadata.game_id}\n"
        message += f"Timestamp: {self.metadata.timestamp}\n" 
        for rule in self.metadata.rules:
            message += f"{rule.value}\n"
        message += f"Game Mode: {self.metadata.gamemode}\n"
        message += f"Current Phase: {type(self.data.state).__name__}\n"
        message += f"Current Player: {self.current_player.name}"
        return message
            
    @classmethod
    def create(cls, metadata: GameMetadata) -> Self:
        """
        Factory method that creates a Game object 
        using information provided by metadata.

        Parameters
        ----------
        metadata : GameMetadata
            An encapsulation of all data required to create a Game object. 
        
        Returns
        -------
        Game
            An instantiated Game object with properties inherited from metadata.

        Notes
        -----
        Game should have the data injected into it after creation so the State
        knows the correct reference to Game.

        Example
        -------
        metadata = GameMetadata() 
        >>> game_object = Game.create_game(game_id = 1, 
                                            timestamp = datetime.time.now(),
                                            ...etc.
                                            )
        >>> print(game_object)
        id = 1
        timestamp = 2025-10-17 17:44:49.864053 
        rules = [Automatic, Fixed, Adjacent, 100%, Traditional]
        game_mode = LOCAL_PLAY
        """
        stats = GameStats()
        game = Game(metadata=metadata, data=None, stats=stats)
        rules = metadata.rules

        #Defining data
        event_bus = EventBus()
        starting_state: State = PlacementState(game)

        initial_board = Board.create(rules)

        players = metadata.players
        eliminated_players = []
        player_queue = Queue()
        turn_order = players.copy()
        starting_units = game.__get_initial_placement_units()

        random.shuffle(turn_order)
        for player in turn_order:
            player_queue.enqueue(player)
            player.units_to_place = starting_units
        
        deck = Deck()
        deck.initialise_cards()
        deck.shuffle()

        data = GameData(event_bus=event_bus,
                        state=starting_state,
                        board=initial_board,
                        players=players,
                        eliminated_players=eliminated_players,
                        player_queue=player_queue,
                        deck=deck,
                        rules=rules)
        
        game.data = data#Dependency Injection
        return game

    @classmethod
    def load(cls, file_name: str) -> Self:
        """
        Factory method that creates a `Game` object by importing 
        the game data from file labelled `file_name` in `/saves` 

        Parameters
        ----------
        file_name : str
            The name of the file being imported
        
        Returns
        -------
        Game
            An instantiated new Game object with the properties of the loaded file 

        Notes
        -----
        This method constructs Game by taking JSON data from a file. 

        Example
        -------
        >>> game_object = Game.load_game("SavedGame1")
        >>> print(game_object)
        id = 1
        time_stamp = 2025-10-17 17:44:49.864053 
        rules = [Automatic, Fixed, Adjacent, 100%, Traditional]
        game_mode = LOCAL_PLAY
        """

        directory = pathlib.Path(__file__).parent
        file_location = directory / "cards.json"

        file_location: str = f"../../../../saves/{file_name}.json"
        try:
            with open(file_location, "r") as json_data:
                save_data = json.load(json_data)
            game = cls(**save_data)
            return game
        
        except Exception as e:
            print(e)

    def execute(self, command: Command) -> None:
        """
        Executes the given command 
        
        Notes
        -----
        Acts as a handler which forwards the request
        to the State.
        """
        self.state.execute(command)

    def save_game(self, file_name: str) -> None:
        """
        Procedure that exports the game data into a new 
        file labelled `file_name` into `/saves`.
        
        Parameters
        ----------
        file_name : str
            The name of the file being exported

        Notes
        -----
        This method modifies `/saves` as a side effect, and does not return anything. 

        If another file with the same name is already in `/saves`, 
        ask  the user to confirm before overwriting the new file.
        """
        try:
            save_directory = f"../../../../saves/{file_name}.json" 
            json_data = json.dumps(self, default=lambda x: x.__dict__, indent=4)
            with open(save_directory, "w") as save_file:
                save_file.write(json_data)

        except Exception as e:
            print(e)

    def start(self) -> None:
        """
        Starts the logic of the game

        Notes
        -----
        There must be a pause between creating the Game 
        and starting the logic to allow for objects
        to hook into Game.
        """
        self.state.on_enter()

    def next_phase(self) -> None:
        """
        Creates the next phase object and calls
        on_start()
        
        Notes
        -----
        Should replace the State object in gamedata
        with the next applicable game state. 
        
        Note that this does not cover the end phase.
        AttackPhase should handle this separately

        Placement -> [Recruitment -> Attack
        -> Fortify -> Recruitment] LOOP 

        Should also call appropiate end phase methods
        """
        followup_state = {
            PlacementState: RecruitmentState,
            RecruitmentState: AttackState,
            AttackState: FortificationState,
            FortificationState: RecruitmentState
        }
        if isinstance(self.state, FortificationState):
            self.stats.turns_played += 1
            self.player_queue.cycle()
            while self.current_player in self.eliminated_players:
                self.player_queue.cycle()

        self.state = followup_state[type(self.state)](self)
        self.state.on_enter()
        
    def set_end_phase(self) -> None:
        """
        Immediately 
        transition to the end phase
        of the game.
        """
        self.state = EndState(self)
        self.state.on_enter()
    
    def get_territory_from_id(self, id: str) -> Continent:
        """
        Lookup any continent with the specified name

        Parameters
        ----------
        name : ContinentName
            The name of the continent being looked up
        
        Returns
        -------

        Territory
            The continent object associated with the name
        """
        try:
            return self.board.get_territory_from_id(id)
        except:
            return None
        
    def get_set_value(self, cards: list[Card]) -> int:
        """
        Calculates how many units would be returned from trading 
        in a set

        Parameters
        ----------
        cards : list[Card]
            The cards that are being traded in 
        
        Returns
        -------
        int
            The number of units solely from recruitment

        Notes
        -----
        This function does not account for gaining units
        from cards of a player-owned territory.

        Returns 0 if the set is untradeable.
        """
        if len(cards) != RecruitmentConfig.CARDS_IN_SET:
            return 0
        
        total_wildcards = 0
        for card in cards:
            if card.is_wildcard:
                total_wildcards += 1
        non_wildcards = [card for card in cards if not card.is_wildcard]

        if self.rules.RECRUITMENT == RecruitmentRules.FIXED:
            if total_wildcards >= 2:
                return RecruitmentConfig.FIXED_MIXED_SET

            if total_wildcards == 1: 
                if non_wildcards[0] == non_wildcards[1] == "Infantry": 
                    return RecruitmentConfig.FIXED_INFANTRY_ONLY
                elif non_wildcards[0] == non_wildcards[1] == "Cavalry": 
                    return RecruitmentConfig.FIXED_CAVALRY_ONLY
                elif non_wildcards[0] == non_wildcards[1] == "Artillery": 
                    return RecruitmentConfig.FIXED_ARTILLERY_ONLY
                else:
                    return RecruitmentConfig.FIXED_MIXED_SET
            
            else:
                if non_wildcards[0] == non_wildcards[1] == non_wildcards[2] == "Infantry":
                    return RecruitmentConfig.FIXED_INFANTRY_ONLY
                if non_wildcards[0] == non_wildcards[1] == non_wildcards[2] == "Cavalry":
                    return RecruitmentConfig.FIXED_CAVALRY_ONLY
                if non_wildcards[0] == non_wildcards[1] == non_wildcards[2] == "Artillery":
                    return RecruitmentConfig.FIXED_ARTILLERY_ONLY
                if len(set(non_wildcards)) == RecruitmentConfig.CARDS_IN_SET:
                    return RecruitmentConfig.FIXED_MIXED_SET
                else:
                    return 0
            
        elif self.rules.RECRUITMENT == RecruitmentRules.PROGRESSIVE:
            if total_wildcards >= 1: 
                return self.__get_set_value_progressive()
            elif non_wildcards[0] == non_wildcards[1] == non_wildcards[2]:
                return self.__get_set_value_progressive()
            elif non_wildcards[0] != non_wildcards[1] != non_wildcards[2] != non_wildcards[0]:
                return self.__get_set_value_progressive()
            else:
                return 0
    
    def __get_set_value_progressive(self) -> int:
        """
        Calculates how many units should be awarded from a set
        if progressive rules are enabled
        
        Returns
            int

        Notes
        -----
        The values are hardcoded from 1-6, 7+ uses a formula.
        """
        
        if self.stats.traded_in_sets <= 6:
            return RecruitmentConfig.PROGRESSIVE_BASE_RECRUITMENT[self.stats.traded_in_sets]
        
        else:
            return 15 + (self.stats.traded_in_sets - 6) * RecruitmentConfig.PROGRESSIVE_EXTRA_UNITS_PER_SET
    
    def __get_initial_placement_units(self) -> int:
        """
        Finds the units a player starts with 
        
        Returns
        -------
        int
            The number of units at the start of the placement turn  

        Notes
        -----
        The formula for the traditional map:

        50 - 5n
        Where n is the total number of players.
        Clamp at 10, in case of additional players being
        added after 6. 

        The formula for the antiquity map
        18 - 2n 
        Where n is the total number of players.
        Clamp at 5, in case of additional players being
        added after 4.
        """
        total_players = len(self.metadata.players)
        if self.metadata.rules.MAP == MapRules.TRADITIONAL:
            return PlacementConfig.TRADITIONAL_BASE_UNITS - PlacementConfig.TRADITIONAL_EXTRA_PLAY_PENALTY*total_players
        elif self.metadata.rules.MAP == MapRules.ANTIQUITY:
            return PlacementConfig.ANTIQUITY_BASE_UNITS - PlacementConfig.ANTIQUITY_EXTRA_PLAY_PENALTY*total_players
        
@dataclass(frozen=True)
class GameMetadata:
    """
    Container for data about the Game object.
    
    Attributes
    ----------
    game_id : int
        Unique identifier for the game object
    timestamp : datetime
        The datetime when the object was last edited or created
    gamemode : GameMode
        The type of game the object was used for: Local Play, Simulation or Training
    players : int
        The read only information about players at instantiation of the game
    rules : GameRules 
        The rules defined at the start of the game 

    Notes
    -----
    Should only be handled at construction or by external components.
        """
    game_id: int
    timestamp: datetime
    gamemode: GameMode
    players: list[Player]
    rules: GameRules

@dataclass
class GameData:
    """
    Container for data relating to the game components.
    
    Attributes
    ----------
    event_bus : EventBus
        An event bus for the events emitted. 
    state : State
        Ephemeral container for data about the current turn including player and turn phase
    board : Board
        Container for data about the board, continents and territories
    players : list[Player]
        Container for properties of each player 
    eliminated_players : list[Player]
        Container for properties of each eliminated player in turn order
        (earliest at front)
    player_queue : Queue[Player]
        The order in which players will play their turn
    deck : Deck
        A stack containing the cards not yet drawn
    rules : GameRules 
        The rules defined at the start of the game 
    """
    event_bus: EventBus
    state: State
    board: Board
    players: list[Player]
    eliminated_players: list[Player]
    player_queue : Queue[Player]
    deck: Deck
    rules: GameRules

@dataclass
class GameStats:
    """
    Container for data relating to the overall perfomance of players

    Attributes
    ----------
    turns_played : int
        The number of times the queue has returned to the first player
    units_recruited : int
        The number of units recruited from all sources by all players
    traded_in_sets : int
        The number of sets traded in throughout the game
    units_eliminated : int
        The total number of units that have been eliminated
    territory_captures : int
        The total number of times a territory has changed owner(after placement)
    players_eliminated : int
        The total number of players eliminated from a game
    """
    turns_played: int = 0
    units_recruited: int = 0
    traded_in_sets: int = 0
    units_eliminated: int = 0
    territory_captures: int = 0
    players_eliminated: int = 0


class GameMode(Enum):
    """
    The gamemodes Game can be created in
    
    Attributes
    ----------
    LOCAL_PLAY
        Local play
    TRAINING
        Training
    SIMULATION
        Simulation
    """
    LOCAL_PLAY = "Local Play"
    TRAINING = "Training"
    SIMULATION = "Simulation"
