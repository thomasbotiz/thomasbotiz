from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import random

from ...main.config import PlacementConfig
from ...main.rules import PlacementRules
from ...utils import State, ImplicitEvent
from ..commands import *

if TYPE_CHECKING:
    from ...utils.templates import Command
    from ...main.game import Game


class PlacementState(State):
    def __init__(self, game: Game):
        """
        State representing the initial placement phase of Risk 

        Parameters
        ----------
        game : Game
            The game instance that owns State

        Attributes
        ----------
        units_left : int
            The number of units the player can place in their turn
            before the next players placement turn
        whitelisted_commands : set
            The commands that will not be immediately caught upon
            being executed
        fortifying : bool
            Whether we are claiming territories or fortifying 
            already claimed territories
        
        Example
        -------
        >>> game.gamedata.state = PlacementState(game)
        >>> game.gamedata.state.on_enter()
        Andrews turn - Placement phase: 
        Andrew, You have 15 units in total and 3 units to place now!
        >>> command = PlaceUnitCommand("India", 3)
        >>> game.execute(command)
        Andrew transferred 3 units to India!
        Berts turn - Placement phase: 
        Bert, You have 15 units in total and 3 units to place now!
        >>> command = PlaceUnitCommand("India", 1)
        >>> game.execute(command)
        Bert, that territory is claimed by someone else! 
        Bert, You have 15 units in total and 3 units to place now!
        """
        super().__init__(game)
        self.units_left_in_pass = 1#As there are unclaimed territories
        self.whitelisted_commands = {PlaceUnitCommand, SaveCommand, LoadCommand, 
                                     CloseGameCommand, ViewContinentsCommand, ViewTerritoriesCommand,
                                     ViewCardsCommand}
        self.fortifying = False

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
        self.game.event_bus.emit(PlacementPhaseStartedEvent(self.game.current_player))

        if self.game.rules.PLACEMENT == PlacementRules.AUTOMATIC_PLACEMENT:
            self.game.event_bus.emit(PlacementPhaseAutoSetupEvent())
            self.__auto_resolve()
            self._exit()
            return
    
    def _exit(self) -> None:
        """
        Changes the state to the recruitment phase

        Emitted Events
        --------------
        PlacementPhaseEndedEvent : ImplicitEvent 
            Once when for all players have no more units to place 
        """
        self.game.event_bus.emit(PlacementPhaseEndedEvent())
        self.game.next_phase()
    
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
        
        Notes
        -----
        This is just a dummy, because there is no scenario
        in which commands are dynamically rejected/accepted
        in the placement phase.
        """
        error = ""
        if isinstance(command, PlaceUnitCommand):
            if command.units_placed > self.units_left_in_pass:
                error += "Cannot place more units than the turn limit!\n"
            if self.game.board.all_territories_claimed:
                if command.territory.owner != self.game.current_player:
                    error += "Cannot place another player's territory!"
            else:
                if command.territory.owner: 
                    error += "This territory has already been claimed!"
        return error.strip()
    
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
        If territory_placed_on is specified and the territory is unowned,
         assign the territory to the player specified in result

        If `units_left` is zero, then roll to the next player in the player queue.

        If all territories have been claimed, set `units_left` to the lower number 
        between `max_units_per_turn` and the overall number of units left to place.

        If not all territories have been claimed, set `units_left` to one. 

        If the next player starts with zero units, call `_exit()`
        
        Emitted Events
        --------------
        PlaceUnitEvent : ExplicitEvent
            When result is PlaceUnitCommandEvent
        PlacementPhaseNextPlayer : ImplicitEvent
            When the current player runs out of units in their pass 
        PlacementPhaseFortifyingEvent : ImplicitEvent
            Once when there are no unclaimed territories left on the board
        """
        self.game.event_bus.emit(result)

        if isinstance(result, PlaceUnitEvent):
            self.units_left_in_pass -= result.units_placed
            if self.units_left_in_pass == 0:
                if not self.fortifying and self.game.board.all_territories_claimed:
                    self.fortifying = True
                    self.game.event_bus.emit(PlacementPhaseFortifyingEvent())

                if self.fortifying:
                    self.units_left_in_pass = min(self.game.current_player.units_to_place, PlacementConfig.UNITS_PER_PASS)
                else:
                    self.units_left_in_pass = 1

                self.game.player_queue.cycle()
                self.game.event_bus.emit(PlacementPhaseNextPlayer(self.game.current_player, self.units_left_in_pass))
                #If you cycle to a player who already has zero units, then all players have zero units left.
                if self.game.current_player.units_to_place <= 0:
                    self._exit()
            self.game.event_bus.emit(UnplacedUnitsEvent(self.game.current_player, self.game.current_player.units_to_place))

    def __auto_resolve(self):
        """
        Method that automates the rest of the placement phase 

        Notes
        -----
        If there are unclaimed territories, assign each player
        a random unselected territory in turn order.

        If all territories are claimed, assign each players 
        remaining unit to a random territory separately until
        their turn is over and in turn order.
        """
        #Claiming phase of placement
        while not self.game.board.all_territories_claimed:
            random_territory = random.choice(self.game.board.unclaimed_territories)
            random_territory.owner = self.game.current_player
            random_territory.units += 1
            self.game.current_player.units_to_place -= 1
            self.game.player_queue.cycle()
        
        #Fortifying phase of placement
        for player in self.game.players:
            while player.units_to_place > 0:
                random_territory = random.choice(self.game.board.get_friendly_territories(player))
                random_territory.units += 1
                player.units_to_place -= 1
            self.game.player_queue.cycle()
    
@dataclass
class PlacementPhaseNextPlayer(ImplicitEvent):
    """
    An event emitted when a new player begins 
    their placement turn

    Attributes
    ----------
    player : Player
        The player whose turn it now is 
    units_to_place : int
        The number of units to be placed
    """
    player: Player
    units_to_place: int

@dataclass
class PlacementPhaseAutoSetupEvent(ImplicitEvent):
    """
    An event emitted when the Placement phase
    is automatically resolved
    """
    
@dataclass
class PlacementPhaseStartedEvent(ImplicitEvent):
    """
    An event emitted when the Placement phase
    begins

    Attributes
    ----------
    The player who the placement turn starts on
    """
    player: Player

@dataclass
class UnplacedUnitsEvent(ImplicitEvent):
    """
    An event emitted when the player still has units to place

    Attributes
    ----------
    player : Player
        The player who has unplaced units
    units_left : int
        The number of units left
    
    """
    player: Player
    units_left : int


@dataclass
class PlacementPhaseEndedEvent(ImplicitEvent):
    """
    An event emitted when the Placement phase
    ends
    """

@dataclass
class PlacementPhaseFortifyingEvent(ImplicitEvent):
    """
    An event emitted when the game switches
    from the claiming subphase to the fortifying
    subphase
    """
