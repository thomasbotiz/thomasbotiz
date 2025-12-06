from ...utils.templates import State, Command, ImplicitEvent, ExplicitEvent
from ...main.game import Game
from __future__ import annotations
from dataclasses import dataclass

class Territory:
    pass

class Card:
    pass

class RecruitmentState(State):
    def __init__(self, game: Game):
        """
        State representing the recruitment phase of Risk 

        Attributes
        ----------
        game : Game
            The game instance that owns State
        current_player : Player
            The player whose recruitment turn it is 
        units_left : int
            The number of units the player can recruit in their turn

        Example
        -------
        >>> game.gamedata.state = RecruitmentState(game)
        >>> game.gamedata.state.on_enter()
        Andrew's turn - Recruitment phase
        Andrew, you have received 15 units from continent and territory bonuses!
        Andrew, you must trade in a set before the phase ends. 
        >>> command = TradeSet(
                                ["Madagascar", 
                                "Ukraine", 
                                "Japan"])
        >>> game.execute(command)
        >>> command = RecruitUnits("Greenland", 14)
        >>> game.execute(command)
        >>> command = EndTurn()
        >>> game.execute(command)
        Command not executed! You have 8 more units to place!
        """
        pass

    def on_enter(self):
        """
        Called directly after initialisation of RecruitmentState

        Notes
        -----
        Emits an Event that the recruitment phase has started,
        checks if the player must trade in a set and calculates
        how many units the player receives from continent and 
        territory bonuses

        Emitted Events
        --------------
        RecruitmentUnitsRecruited : ImplicitEvent
            Emitted on creation of PlacementState
        RecruitmentPhaseStartedEvent : ImplicitEvent
            Emitted on creation of PlacementState
        PlacementPhaseForcedCardTradeEvent : ImplicitEvent
            Emitted if the player holds too many cards

        Example
        -------
        >>> Game.gamedata.state = PlacementState()
        >>> Game.gamedata.state.on_enter() 
        Andrew's turn - Recruitment phase
        Andrew, you have received 15 units from continent and territory bonuses!
        Andrew, you must trade in a set before the phase ends.
        """
    
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
        The passed command must be of a subclass of RecruitmentCommand or
        Command. 

        Example
        -------
        >>> state = RecruitmentState(game) 
        >>> command = RecruitUnitCommand("Ontario", 10)
        >>> game.execute(command)

        See Also
        --------
        _validate(), _on_execute()
        """
        pass

    def _validate(self, command: Command) -> str:
        """
        Method that ensures command is of the correct subclass 
        
        Parameters
        ----------
        command : Command
            The command being validated

        Returns
        -------
        str
            Any accompanying error message(None assumes success)

        Notes
        -----
        The allow commands are: TradeSet, RecruitUnit, NextTurn,
        Save, Load

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
        If RecruitUnitCommand is called:

        If `units_left` is zero and the player has no available sets,
        automatically proceed to the next turn. 

        If EndTurnCommand is called:

        If `units_left` is zero and the player does not have to trade
        in a set, proceed to the attack phase.

        Emitted Events
        --------------

        """
        pass

    def _on_exit(self) -> None:
        """
        Emits the phase was ended

        Emitted Events
        --------------
        FortifyPhaseEndedEvent
        """
        pass

@dataclass
class RecruitmentPhaseStartedEvent(ImplicitEvent):
    """
    Event emitted when the phase begins
    
    Attributes
    ----------
    player : Player
        The player whose turn it is 
    units_left : int
        The number of the units the player
        starts the recruitment phase with
    """

@dataclass
class RecruitmentPhaseEndedEvent(ImplicitEvent):
    """
    Event emitted when the phase ends
    
    Attributes
    ----------
    player : Player
        The player whose turn it was
    """

@dataclass
class NoRecruitmentLeftEvent(ImplicitEvent):
    """
    Event emitted when there are no more 
    possible recruitments 
    
    Attributes
    ----------
    player : Player
        The player who has no more territories
        to recruit
    """