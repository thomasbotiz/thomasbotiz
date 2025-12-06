from ...utils.templates import State, Command, ImplicitEvent, ExplicitEvent
from ...main.game import Game
from __future__ import annotations
from dataclasses import dataclass

class Territory():#dummy for typing
    pass

class Player():#dummy for typing
    pass

class FortificationState(State):
    def __init__(self, game: Game):
        """
        State representing the fortifying phase of Risk 

        Attributes
        ----------
        game : Game
            The game instance that owns State
        current_player : Player
            The player whose fortifying turn it is 

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
        pass

    def on_enter(self):
        """
        Called dirctly after initialisation of FortificationState

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
        The allowed commands are: Load, Save, FortifyTerritory, NextTurn
        """
        pass

    def execute(self, command: Command) -> None:
        """
        Public interface that orchestrates the validation, execution and 
        side effect checking of passed commands

        Parameters
        ----------
        command : Command
            The command attempted to being executed

        Notes
        -----
        The passed command must be of a direct subclass of FortifyCommand or
        Command. 

        Example
        -------
        >>> command = FortifyCommand("Brazil", "India", 3)
        >>> game.execute(command)
        Andrew transferred 3 units to India from Brazil!

        See Also
        --------
        _validate(), _on_execute()
        """
        pass

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

        If 
        
        FortifyTerritoryCommand AND success = true 
        
            OR 
        
        EndTurnCommand AND success = true 

        Proceed to the next turn

        Emitted Events
        --------------
        FortifyTerritoryEvent
            When a territory is fortified
        """
        pass
    
    def on_exit(self):
        """
        Emitted Events
        --------------
        FortifyPhaseEndedEvent
            When on_exit is called
        """

@dataclass
class FortifyPhaseStartedEvent(ImplicitEvent):
    """
    Event emitted when the phase begins
    
    Attributes
    ----------
    player : Player
        The player whose turn it is 
    """


@dataclass
class NoFortifyLeftEvent(ImplicitEvent):
    """
    Event emitted when there are no valid 
    fortifies
    
    Attributes
    ----------
    player : Player
        The player whose turn it was
    """

@dataclass
class FortifyPhaseEndedEvent(ImplicitEvent):
    """
    Event emitted when the phase ends
    
    Attributes
    ----------
    player : Player
        The player whose turn it was
    """