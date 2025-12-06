from __future__ import annotations
from dataclasses import dataclass

from ...main.config import RecruitmentConfig
from ...utils.templates.state import State
from ...utils.templates.event import ImplicitEvent
from ..commands import *

class RecruitmentState(State):
    def __init__(self, game: Game):
        """
        State representing the recruitment phase of Risk 

        Attributes
        ----------
        game : Game
            The game instance that owns State
        whitelisted_commands : set[Command]
            The static list of commands that are not immediately filtered
        territory_bonus_received : bool
            False until a territory is granted 2 units by virtue of having
            it's face shown on a traded card.

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
        super().__init__(game)
        self.whitelisted_commands = {SaveCommand, LoadCommand, NextTurnCommand, TradeSetCommand, 
                                     PlaceUnitCommand, CloseGameCommand, ViewContinentsCommand, 
                                     ViewTerritoriesCommand, ViewCardsCommand
                                     }
        self.territory_bonus_received = False

    @property
    def expecting_trade(self):
        """
        Whether the current player must trade in a set during their recruitment turn
        """
        return (len(self.game.current_player.cards) >= RecruitmentConfig.MAX_CARDS)

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
        self.game.event_bus.emit(RecruitmentPhaseStartedEvent(self.game.current_player))
        units_recruited = self.game.board.get_passive_recruitment(self.game.current_player)
        self.game.current_player.units_to_place += units_recruited
        self.game.current_player.stats.total_units_recruited += units_recruited
        self.game.event_bus.emit(UnitsRecruitedEvent(self.game.current_player, units_recruited))
        self.game.event_bus.emit(UnrecruitedUnitsEvent(self.game.current_player, self.game.current_player.units_to_place))
        if self.expecting_trade:
            self.game.event_bus.emit(ForcedCardTradeEvent(player = self.game.current_player,
                                        number_of_cards = len(self.game.current_player.cards),
                                        card_limit = RecruitmentConfig.MAX_CARDS))

    def _dynamic_validate(self, command: Command) -> str:
        """
        Method to check if the Command is legal 
        within the context of the Recruitment state.

        Parameters
        ----------
        command : Command
            The command attempting to be executed
        
        Returns
        -------
        str
            The error message if validation was unsuccessful
        
        Notes
        -----
        Only allow the player to trade in a set if it is 
        mandatory.
        """
        error = ""
        if isinstance(command, PlaceUnitCommand):
            if command.territory.owner is not self.game.current_player:
                error += "You can only recruit to territories you control!\n"

        if isinstance(command, NextTurnCommand):
            if self.expecting_trade:
                error += "Must trade in a set before ending the phase!\n"
            if self.game.current_player.units_to_place > 0:
                error += "Must place all units before ending the phase!\n"
        return error.strip()

    def _on_execute(self, result: ExplicitEvent) -> None:
        """
        Checks for side effects and emits events after a command is executed
        by scanning the data of what Command just edited

        Parameters
        ----------
        result : ExplicitEvent
            Data returned by Command about what changed in Game 

        Notes
        -----
        If RecruitUnitCommand is called:

        If units_left is zero and the player has no available sets,
        automatically proceed to the next turn. 

        If EndTurnCommand is called:

        If units_left is zero and the player does not have to trade
        in a set, proceed to the attack phase.

        Emitted Events
        --------------
        NoRecruitmentLeftEvent : ImplicitEvent
            If there are no more valid territories
        ForcedCardTradeEvent : ImplicitEvent
            If the player must trade in a set
        RecruitmentPhaseEndedEvent : ImplicitEvent
            If the phase was ended
        """
        self.game.event_bus.emit(result)
        
        if isinstance(result, TradeSetEvent):
            owned_territories = self.game.board.get_friendly_territories(self.game.current_player)
            for card in result.cards:
                territory = self.game.board.territory_lookup[card.territory]
                if territory in owned_territories and not self.territory_bonus_received:
                    territory.units += 2
                    self.territory_bonus_received = True
                    break
        
        if isinstance(result, PlaceUnitEvent):
            if self.game.current_player.units_to_place == 0 and not self.game.current_player.can_trade_set:
                self.game.event_bus.emit(NoRecruitmentLeftEvent(self.game.current_player))
                self._exit()
                return

        if self.expecting_trade:
            self.game.event_bus.emit(ForcedCardTradeEvent(player = self.game.current_player,
                                                         number_of_cards = len(self.game.current_player.cards),
                                                         card_limit = RecruitmentConfig.MAX_CARDS
                                                         ))
        self.game.event_bus.emit(UnrecruitedUnitsEvent(self.game.current_player, self.game.current_player.units_to_place))

    def _exit(self) -> None:
        """
        Emits that the phase was ended

        Emitted Events
        --------------
        RecruitmentPhaseEndedEvent
        """
        self.game.event_bus.emit(RecruitmentPhaseEndedEvent())
        self.game.next_phase()
    
@dataclass
class RecruitmentPhaseStartedEvent(ImplicitEvent):
    """
    Event emitted when the phase begins
    
    Attributes
    ----------
    player : Player
        The player whose turn it is 
    """
    player: Player


@dataclass
class RecruitmentPhaseEndedEvent(ImplicitEvent):
    """
    Event emitted when the phase ends
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
        to recruit to
    """
    player: Player

@dataclass
class UnitsRecruitedEvent(ImplicitEvent):
    """
    Event emitted which relays how many units
    the player has at the start of their turn
    
    Attributes
    ----------
    player : Player
        The player whose turn it is
    units_recruited : int
        The number of units granted
    """
    player : Player
    units_recruited : int

@dataclass
class ForcedCardTradeEvent(ImplicitEvent):
    """
    Event emitted when the player must trade in a set
    
    Attributes
    ----------
    player : Player 
        The current turn player
    number_of_cards : int
        The number of cards the player has
    card_limit : int
        The max number of cards allowed
    """
    player: Player
    number_of_cards: int
    card_limit : int


@dataclass
class UnrecruitedUnitsEvent(ImplicitEvent):
    """
    Event emitted when the player has units to place

    Attributes
    ----------
    player : Player 
        The current turn player
    units_to_recruit : int
        The number of units that must be placed by the end of the turn
    """
    player: Player
    units_to_recruit: int