from ...utils.templates import State, Command, ImplicitEvent, ExplicitEvent
from ...main.game import Game
from __future__ import annotations
from dataclasses import dataclass

class Territory():#dummy for typing
    pass
class Player():#dummy for typing
    pass

class PlacementState(State):
    def __init__(self, game: Game):
        """
        State representing the initial placement phase of Risk 

        Attributes
        ----------
        game : Game
            The game instance that owns State
        current_player : Player
            The player whose placement turn it is 
        units_left : int
            The number of units the player can place in their turn
        max_units_per_turn : int
            The max number of units that can be placed in a given turn
            after all territories have been assigned(default = 3)

        Example
        -------
        >>> game.gamedata.state = PlacementState(game)
        >>> game.gamedata.state.on_enter()
        Andrew's turn - Placement phase: 
        Andrew, You have 15 units in total and 3 units to place now!
        >>> command = PlaceUnitCommand("India", 3)
        >>> game.execute(command)
        Andrew transferred 3 units to India!
        Bert's turn - Placement phase: 
        Bert, You have 15 units in total and 3 units to place now!
        >>> command = PlaceUnitCommand("India", 1)
        >>> game.execute(command)
        Bert, that territory is claimed by someone else! 
        Bert, You have 15 units in total and 3 units to place now!
        """
        
    def on_enter(self):
        """
        Called directly after initialisation of PlacementState

        Notes
        -----
        Emits an Event that the placement phase has started. If 
        automatic placement is enabled in GameRules, then
        auto resolve placement and move to the next phase.

        Emitted Events
        --------------
        PlacementPhaseStartedEvent : ImplicitEvent
            Emitted on creation of PlacementState
        PlacementPhaseAutoSetupEvent : ImplicitEvent
            Emitted if placement phase is automatic 

        Example
        -------
        >>> Game.gamedata.state = PlacementState()
        >>> Game.gamedata.state.on_enter() 

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
        The passed command must be of a subclass of PlacementCommand or
        Command. 

        Example
        -------
        >>> state = PlacementState(game) 
        >>> command = PlaceUnitCommand(game.get_territory("India"), 1)
        >>> game.execute(command)

        See Also
        --------
        _validate(), _on_execute()
        """
        pass

    def _validate(self, command: Command) -> bool:
        """
        Method that ensures command is of the correct subclass 
        
        Parameters
        ----------
        command : Command
            The command being validated

        Returns
        -------
        bool
            True if valid command else False 

        Notes
        -----
        The passed command must be Save, Load, PlaceUnit
        """
        pass

    def _on_execute(self, result: ExplicitEvent) -> None:
        """
        Checks for side effects and emits events after a command is executed
        by scanning the data of what `Command` just edited
        
        Parameters
        ----------
        result : PlacementCommandResult
            Data returned by `Command` about what changed in `Game` 

        Notes
        -----
        The only receiveable result is PlaceUnitResult in this phase

        If territory_placed_on is specified and the territory is unowned and success
        is True, assign the territory to the player specified in result

        If `units_left` is zero, then roll to the next player in the player queue.

        If all territories have been claimed, set `units_left` to the lower number 
        between `max_units_per_turn` and the overall number of units left to place.

        If not all territories have been claimed, set `units_left` to one. 

        When all players have no more units to place, call `_on_exit()`
        
        Emitted Events
        --------------
        PlaceUnitSuccessEvent : ExplicitEvent
            When result is PlaceUnitCommandResult and `success` is true 
        PlaceUnitFailedEvent : ExplicitEvent
            When result is PlaceUnitCommandResult and `success` is false 
        PlacementPhaseNextPlayer : ImplicitEvent
            When `units_left` player is zero 
        PlacementPhaseFortifyingEvent : ImplicitEvent
            Once when there are no unclaimed territories left on the board
        PlacementPhaseEndedEvent : ImplicitEvent 
            Once when for all players have no more units to place 
        """
        pass
    
    def _on_exit(self) -> None:
        """
        Changes the state to the recruitment phase

        Emitted Events
        --------------
        PlacementPhaseEndedEvent : ImplicitEvent 
            Once when for all players have no more units to place 
        """
        pass
    
@dataclass
class PlacementPhaseNextPlayer(ImplicitEvent):
    """
    An event emitted when a new player begins 
    their placement turn
    """
    pass

@dataclass
class PlacementPhaseAutoSetupEvent(ImplicitEvent):
    """
    An event emitted when the Placement phase
    is automatically resolved
    """
    pass

@dataclass
class PlacementPhaseStartedEvent(ImplicitEvent):
    """
    An event emitted when the Placement phase
    begins
    """
    pass

@dataclass
class PlacementPhaseEndedEvent(ImplicitEvent):
    """
    An event emitted when the Placement phase
    ends
    """
    pass

@dataclass
class PlacementPhaseFortifyingEvent(ImplicitEvent):
    """
    An event emitted when the game switches
    from the claiming subphase to the fortifying
    subphase
    """
