from typing import Self, Any
from dataclasses import dataclass
from __future__ import annotations
from ..utils import *
from data import *
from datetime import datetime

class Deck:
    pass

class Game:
    def __init__(self, 
                metadata: GameMetadata, 
                data: GameData, 
                stats: GameStats
                ):
        """
        The interface for the "Risk" board game. Orchestrates game flow and provides public methods.
            
        Parameters
        ----------
        metadata : GameMetadata
            Container for data specific to the instantiation of rhe Game object

        data : GameData
            Container for data about current state of the game components

        stats : GameStats
            Container for high-level statistics of the game

        Attributes
        ----------
        metadata : GameMetadata
            Container for data specific to the instantiation of rhe Game object

        data : GameData
            Container for data about current state of the game components

        stats : GameStats
            Container for high-level statistics of the game
        """

    def __repr__(self) -> str:
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

    
    @classmethod
    def create_game(self, metadata: GameMetadata) -> Self:
        """
        Factory method that creates a `Game` object 
        using information provided by `metadata`.

        Parameters
        ----------
        metadata : GameMetadata
            A Container for all revelant information to creating a `Game` object. 
        
        Returns
        -------
        Game
            An instantiated `Game` object with properties inherited from metadata.

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
        pass

    @classmethod
    def load_game(self, file_name: str) -> Self:
        """
        Factory method that creates a `Game` object by importing 
        the game data from file labelled `file_name` in `\saves` 

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
        This method loads from `\saves` as a side effect, and does not return anything.

        Example
        -------
        >>> game_object = Game.load_game("SavedGame1")
        >>> print(game_object)
        id = 1
        time_stamp = 2025-10-17 17:44:49.864053 
        rules = [Automatic, Fixed, Adjacent, 100%, Traditional]
        game_mode = LOCAL_PLAY
        """
        pass
    
    @property 
    def event_bus(self) -> EventBus:
        """
        Returns the Event Bus in data
        """

    @property 
    def state(self) -> State:
        """
        Returns the State in data
        """
    
    @property 
    def board(self) -> Board:
        """
        Returns the Board in data
        """
    
    @property 
    def players(self) -> list[Player]:
        """
        Returns the players in data
        """

    @property 
    def eliminated_players(self) -> list[Player]:
        """
        Returns the eliminated players in data
        """
    
    @property 
    def player_queue(self) -> Queue:
        """
        Returns the player queue in data
        """
    
    @property 
    def deck(self) -> Deck:
        """
        Returns the Deck in data
        """
    
    @property 
    def rules(self) -> GameRules:
        """
        Returns the Rules in data
        """

    def save_game(self, file_name: str) -> None:
        """
        Procedure that exports the game data into a new 
        file labelled `file_name` into `\saves`.
        
        Parameters
        ----------
        file_name : str
            The name of the file being exported

        Notes
        -----
        This method modifies `\saves` as a side effect, and does not return anything. 

        If another file with the same name is already in `\saves`, 
        ask  the user to confirm before overwriting the new file.
        """
        pass
    

    def execute(self, command: Command) -> None:
        """
        Executes the given command 
        
        Notes
        -----
        Acts as a handler which forwards the request
        to the State.
        """

    def get_territory(self, name: str) -> Territory:
        """
        Finds the territory associated with the given name

        Parameters
        ----------
        name : str
            The display name of the territory

        Returns
        -------
        Territory
            The associated territory

        Notes
        -----
        Should convert the string to its relevant enum, then lookup
        the enum in the game object.
        """
    
    def get_continent(self, name: str) -> Territory:
        """
        Finds the continent associated with the given name

        Parameters
        ----------
        name : str
            The display name of the continent

        Returns
        -------
        Territory
            The associated continent

        Notes
        -----
        Should convert the string to its relevant enum, then lookup
        the enum in the game object.
        """

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
        """

    def set_end_phase(self) -> None:
        """
        Immediately 
        transition to the end phase
        of the game.

        Notes
        -----
        Should immediately transfer to the next phase of the game
        """
    
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
    total_players : int
        The number of players at instantiation of the game
    rules : GameRules 
        The rules defined at the start of the game 

        """

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


