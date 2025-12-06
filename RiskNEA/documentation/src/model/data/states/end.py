from ...utils.templates import State, Command, ImplicitEvent, ExplicitEvent
from ...main.game import Game
from __future__ import annotations
from enum import Enum
from utils.game_enums import BattleStatus
from dataclasses import dataclass

class EndState(State):
    def __init__(self, game: Game):
        """
        State representing the end of game stat display screen

        Parameters
        ----------
            game : Game
                The game instance that owns State

        Attributes
        ----------
        game : Game
            The game instance that owns State
        current_player : Player
            The player whose stats are currently
            displayed
        """
    
    def on_enter(self):
        """
        Called directly after instantiation of EndState

        Notes
        -----
        Should emit the winning player and end game statistics.
        Note that there should be no way to exit the end
        phase for now, and all players can do is cycle through
        all the players. 

        Emitted Events
        --------------
        EndPhaseStartedEvent
            When called
        """
    
    def _validate(self, command: Command) -> str:
        """
        Method that ensures command is of the correct subclass

        Parameters
        ----------
        command : Command
            The command being validated
        
        Returns
        -------
        bool 
            The accompanying error message from all failed checks
        
        Notes
        -----
        The commands that should be accepted are: Save, Load, 
        CyclePlayer
        """
    
    def _on_execute(self, result: ExplicitEvent) -> None:
        """
        Checks for side effects and emits events after a command is executed
        by scanning the data of what `Command` just edited 

        Parameters
        ----------
        result : ExplicitEvent
            Data returned by `Command` about what changed in `Game` 

        Notes
        -----
        If the player issues a request to quit the game, stop all further
        function.

        Emitted Events
        --------------
        CyclePlayerEvent
            If the next player in the queue's statistics is shown
        GameExitedEvent
            If the user requests to exit the game
        """
    
    def on_exit(self) -> None:
        """
        Called on the game being exited

        Emitted Events
        -------------
        EndPhaseEndedEvent
            When called
        """

@dataclass
class EndPhaseStartedEvent(ImplicitEvent):
    """
    An event emitted when the phase begins

    Attributes
    ----------
    stats : GameStats
        The game stats
    """

@dataclass
class EndPhaseEndedEvent(ImplicitEvent):
    """
    An event emitted when the phase ends
    via quitting the game
    """
