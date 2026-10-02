from __future__ import annotations
from dataclasses import dataclass

from ...utils.templates.state import State
from ...utils.templates.command import Command
from ...utils.templates.event import ImplicitEvent, ExplicitEvent
from ..commands import *

class FortificationState(State):
    def __init__(self, game: Game):
        """
        State representing the fortifying phase of Risk 

        Attributes
        ----------
        game : Game
            The game instance that owns State
        whitelisted_commands : set[Command]
            The static list of accepted commands

        Example
        -------
        >>> game.gamedata.state = FortificationState(game)
        >>> game.gamedata.state.on_enter()
        Andrew's turn - Fortify phase: 
        Andrew, you may now fortify any territory.
        >>> command = FortifyCommand("Brazil", "India", 3)
        >>> game.execute(command)
        Andrew transferred 3 units to India from Brazil!
        Bert's turn - Fortify phase: 
        Bert, you may now fortify any territory.
        >>> command = FortifyCommand("Japan", "India", 1)
        >>> game.execute(command)
        Bert, that territory is claimed by someone else! 
        """
        super().__init__(game)
        self.whitelisted_commands = {SaveCommand, LoadCommand, CloseGameCommand, NextTurnCommand, 
                                    FortifyTerritoryCommand, ViewContinentsCommand, ViewTerritoriesCommand,
                                    ViewCardsCommand
                                    }

    def _save_data(self) -> dict:
        state_data = {}
        state_data["phase"] = "Fortification"
        return state_data
    
    def _load_data(self, state_data: dict, territory_lookup: dict, player_lookup: dict) -> None:
        pass
        #Nothing to load 

    def on_enter(self):
        """
        Called directly after initialisation of FortificationState

        Notes
        -----
        Checks if any fortifications
        are possible. If not, skip the fortification phase and 
        switch to the next player in the queue's recruitment phase.

        Emitted Events
        --------------
        FortificationPhaseStartedEvent : ImplicitEvent
            Emitted on creation on FortificationState
        NoFortifyLeftEvent : ImplicitEvent
            Emitted if the player starts the turn with no valid fortifications
        
        >>> game.gamedata.state = FortificationState(game)
        >>> game.gamedata.state.on_enter()
        Andrew's turn - Fortify phase:
        Andrew, you may now fortify any territory.
        """
        self.game.event_bus.emit(FortifyPhaseStartedEvent(self.game.current_player))
        owned_territories = self.game.board.get_friendly_territories(self.game.current_player)
        valid_fortifies = [territory for territory in owned_territories if territory.units >= 2]

        if not valid_fortifies or len(owned_territories) <= 1:
            self.game.event_bus.emit(NoFortifyLeftEvent())
            self._exit()
            return
    
    def _dynamic_validate(self, command: Command) -> str:
        """
        Checks if the command is legal in
        the context of the game state 

        Emitted Events
        --------------
        command : Command 
            The command being executed 
        
        Returns
        -------
        str 
            Empty if validation successful else the error 
        """
        error = ""
        if isinstance(command, FortifyTerritoryCommand):
            if self.game.rules.FORTIFICATION == FortifyRules.ADJACENT:
                if not self.game.board.has_adjacency(command.territory_from, command.territory_to):
                    error += "The territories must be adjacent to fortify!\n"
            elif self.game.rules.FORTIFICATION == FortifyRules.CONTIGUOUS:
                if command.territory_from not in command.territory_to.connected_territories:
                    error += "The territories must be directly connected to fortify!\n"
        return error.strip()

    def _on_execute(self, result: ExplicitEvent) -> None:
        """
        Checks for side effects and emits events after a command is executed
        by scanning the data of what `Command` just edited
        
        Parameters
        ----------
        result : ExplicitEvent
            Data returned by `Command` about what changed in `Game` 

        Emitted Events
        --------------
        FortifyTerritoryEvent
            When a territory is fortified
        """
        self.game.event_bus.emit(result)

        if isinstance(result, LoadGameEvent):
            return 
        
        if isinstance(result, (FortifyTerritoryEvent, NextTurnEvent)) and not result.error:
            self._exit()
            return
    
    def _exit(self):
        """
        Emitted Events
        --------------
        FortifyPhaseEndedEvent
            When on_exit is called
        """
        self.game.event_bus.emit(FortifyPhaseEndedEvent())
        self.game.next_phase()

@dataclass
class FortifyPhaseStartedEvent(ImplicitEvent):
    """
    Event emitted when the phase begins
    
    Attributes
    ----------
    player : Player
        The player whose turn it is 
    """
    player: Player

@dataclass
class NoFortifyLeftEvent(ImplicitEvent):
    """
    Event emitted when there are no valid 
    fortifies
    """

@dataclass
class FortifyPhaseEndedEvent(ImplicitEvent):
    """
    Event emitted when the phase ends
    """

