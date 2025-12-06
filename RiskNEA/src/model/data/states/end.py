from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...utils.templates.state import State
from ...utils.templates.event import ImplicitEvent
from ..commands import *


if TYPE_CHECKING:
    from ...data.player.player import PlayerStats, Player
    from ...main.game import Game, GameStats

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
        """
        self.game = game
        self.whitelisted_commands = {LoadCommand, NextTurnCommand, CloseGameCommand}
    
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
        self.game.event_bus.emit(EndPhaseStartedEvent(self.game.stats))
    
    def _dynamic_validate(self, command: Command) -> str:
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
        error = ""
        return error

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
        NextTurnEvent
            If the next player in the queue's statistics is shown
        GameExitedEvent
            If the user requests to exit the game
        """
        self.game.event_bus.emit(result)
    
    def on_exit(self) -> None:
        """
        Called on the game being exited
        
        Notes
        -----
        In the current state of the game, cannot
        be able to leave. Keeping this function to be 
        consistent to the other states.
        """


@dataclass
class PlayerCycledEvent(ImplicitEvent):
    """
    An event emitted when a player is cycled

    Attributes
    ----------
    player : Player
        The current player
    stats : PlayerStats
        The stats of the current player
    """
    player: Player
    stats: PlayerStats


@dataclass
class EndPhaseStartedEvent(ImplicitEvent):
    """
    An event emitted when the phase begins

    Attributes
    ----------
    stats : GameStats
        The game stats
    """
    stats: GameStats

