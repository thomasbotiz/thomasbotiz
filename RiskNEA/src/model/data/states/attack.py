from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from ...utils.templates.state import State
from ...utils.templates.event import ImplicitEvent

from ..commands import *
from .recruitment import UnrecruitedUnitsEvent

if TYPE_CHECKING:
    from ..board import Continent, Territory
    from ..deck import Card
    from ...main import Game
    from ...utils import OffensiveFront, ExplicitEvent

class AttackState(State):
    def __init__(self, game: Game):
        """
        State representing the attack phase of Risk 

        Parameters
        ----------
        game : Game
            The game instance that owns State

        Attributes
        ----------
        front : OffensiveFront 
            Information about the focused on offensive front
        expecting_trade : bool
            True once the player has > 6 cards (by default)
            and False once player has < 5 cards (by default)
        has_captured_territory : bool
            True if at least one captured territory
            else False  
            
        Example
        -------
        >>> game.gamedata.state = AttackState(game)
        >>> game.gamedata.state.on_enter()
        Andrew's turn - Attack phase
        Andrew, pick a front to focus on or end your turn!
        >>> command = FocusOffensiveCommand(
                                "Eastern Europe", 
                                "Ukraine")
        >>> game.execute(command)
        Andrew is attacking Charlie's Ukraine with 3 troops from Eastern Europe with 4 troops!
        Andrew is using 3 dice!
        Charlie is using 2 dice!
        Change dice, battle, auto-resolve, or exit?
        >>> command = AttackManualCommand()
        >>> game.execute(command)
        Andrew rolls: 6 3 2
        Charlie rolls: 6 2
        Andrew loses 1 unit!
        Charlie loses 1 unit!
        Andrew's Eastern Europe now has 3 troops!
        Charlie's Ukraine now has 2 troops!
        Andrew is using 2 dice!
        Charlie is using 2 dice!
        Change dice, battle, auto-resolve, or exit?
        >>> game.execute(command)
        >>> command = EndTurn()
        >>> game.execute(command)
        Command not executed! You have 8 more units to place!
        """
        super().__init__(game)
        self.whitelisted_commands = {SaveCommand, LoadCommand, NextTurnCommand, 
                                     FocusOffensiveCommand, CancelFocusOffensiveCommand,
                                     AttackManualCommand, AttackSimulateCommand, ChangeAttackerDiceCommand,
                                     ChangeDefenderDiceCommand, ChangeLossThresholdCommand, 
                                     FortifyTerritoryCommand, TradeSetCommand, PlaceUnitCommand,
                                     ViewContinentsCommand, ViewTerritoriesCommand, ViewCardsCommand
                                    }
        
        self.front: Optional[OffensiveFront] = None
        self.expecting_trade = False
        self.has_captured_territory = False

    @property
    def attacks_left(self) -> bool:
        return self.game.board.get_attackable_territories(self.game.current_player)
    
    def on_enter(self):
        """
        Called directly after initialisation of AttackState

        Notes
        -----
        Checks if `current_player` has any available attacks,
        if not immediately skip to the player's fortification
        phase.
        
        Emitted Events
        --------------
        AttackPhaseStartedEvent
            When called
        NoAttacksLeftEvent
            If the player starts their turn with no attacks left 

        Example
        -------
        >>> Game.gamedata.state = AttackState()
        >>> Game.gamedata.state.on_enter() 
        Bert's turn - Attack phase
        Bert, pick a front to focus on or end your turn!
        Bert, you have no available more available attacks!
        Charlie's turn - Attack phase
        Charlie, pick a front to focus on or end your turn!
        """
        self.game.event_bus.emit(AttackPhaseStartedEvent(self.game.current_player))
        if not self.game.board.get_attackable_territories(self.game.current_player):
            self.game.event_bus.emit(NoAttacksLeftEvent(player = self.game.current_player))
            self._exit()
            return

    def _exit(self):
        """
        Gives cards to players if they've captured a territory

        Notes
        -----
        Gives one card to the attacking player if has_captured_territory 
        is True 

        Emitted Events
        --------------
        AttackPhaseEndedEvent
            When called
        CardReceivedEvent
            When a player receives a card at the end of their turn
        """
        self.game.event_bus.emit(AttackPhaseEndedEvent())
        if self.has_captured_territory:
            if self.game.deck.is_empty:
                self.game.deck.repopulate()
                self.game.deck.shuffle()
            card = self.game.deck.pop()
            self.game.current_player.cards.append(card)
            self.game.event_bus.emit(CardReceivedEvent(player = self.game.current_player, card = card))
        self.game.next_phase()
    
    def _dynamic_validate(self, command: Command) -> str:
        """
        Method that ensures command is of the correct class

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
        If front is not None then
        
        if status is expecting_transfer, only allow attack commands of 
        instance FortifyCapturedTerritoryCommand.

        If expecting_transfer is False and expecting_trade is True,
        only allow commands of instance TradeSet, Save and Load.

        If expecting_transfer is False and expecting_trade is false
        and unplaced_units is greater than zero only allow commands of 
        instance PlaceUnitAttackCommand

        The list of allowed commands are: Save, Load, TradeSet, PlaceUnit,
        FocusOffensive, CancelOffensive, AttackManualCommand, AttackAutoCommand,
        ChangeAttackerDice, ChangeDefenderDice, ChangeLossThreshold, 
        FortifyCapturedTerritory, NextTurn
        """
        error = ""

        if self.expecting_trade: 
            if not isinstance(command, (TradeSetCommand, SaveCommand, LoadCommand, ViewContinentsCommand, ViewTerritoriesCommand, ViewCardsCommand)):
                error += "You must trade in a set of cards before anything else!\n"

        elif self.game.current_player.units_to_place:
            if not isinstance(command, (TradeSetCommand, PlaceUnitCommand, SaveCommand, LoadCommand, ViewContinentsCommand, ViewTerritoriesCommand, ViewCardsCommand)):
                error += f"You have {self.game.current_player.units_to_place}, trade in a set or place units!\n"

        elif not self.front:
            if isinstance(command, (CancelFocusOffensiveCommand, AttackManualCommand,
                                    AttackSimulateCommand, ChangeAttackerDiceCommand, ChangeDefenderDiceCommand,
                                    ChangeLossThresholdCommand, FortifyTerritoryCommand)):
                error += "You must focus on a front first!\n"

        elif self.front.status == BattleStatus.EXPECTING_TRANSFER:
            if not isinstance(command, (FortifyTerritoryCommand, SaveCommand, LoadCommand, ViewContinentsCommand, ViewTerritoriesCommand, ViewCardsCommand)):
                error += f"Must fortify {self.front.territory_to.name} first!\n" 

            if isinstance(command, FortifyTerritoryCommand):
                if command.units_transferred < self.front.attacker_dice:
                    error += f"Must transfer at least {self.front.attacker_dice} units!\n"
                if command.territory_from != self.front.territory_from:
                    error += f"Must be transferring from {self.front.territory_from.name}!\n"
                if command.territory_to != self.front.territory_to:
                    error += f"Must be transferring from {self.front.territory_to.name}!\n"
        
        if isinstance(command, NextTurnCommand):
            if self.expecting_trade:
                error += "You must trade in a set to end your turn!\n"
            
            elif self.game.current_player.units_to_place:
                error += "You must place all units before ending your turn!\n"
        return error.strip()
                
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
        If front is not None then

        If status is repelled or cancelled, set front to None

        If status is just_captured, set expecting_transfer to true, 
        has_captured_territory to true, check if the defending player has 
        no more territories. If the defender was eliminated, check if there 
        is only one active player left. If true, switch to End phase. If false, 
        transfer all cards to the attacking player. If player has > 6 cards, 
        set expecting_trade to true 

        If expecting_trade is true but the player has less than five cards,
        set expecting_trade to false

        If the player has issued a command to proceed to the next phase,
        front must be None or expecting_transfer must be false and
        expecting_trade must be false 

        If the player has no more available attacks and 
        expecting_transfer and expecting_trade is false, 
        
        Issue to Game to transfer to the next phase if necessary & sufficient.

        Emitted Events
        --------------
        NoAttacksLeftEvent
            If there are no more valid attacks
        ActiveFrontEvent
            If front is not None 
        AttackSuccessfulEvent
            If status is just_captured
        AttackRepelledEvent
            If status is repelled
        ContinentCapturedEvent
            If a continent was fully captured
        PlayerEliminatedEvent
            If a player whose territory was captured
            now controls no more territories
        CardsTransferredEvent
            If a player obtains cards
        RequiredTradeEvent
            If expecting_trade is true
        LastPlayerLeftEvent
            If there is only player left in the game.
        """
        self.game.event_bus.emit(result)

        if isinstance(result, FocusOffensiveEvent):
            self.front = result.front

        elif isinstance(result, (CancelFocusOffensiveEvent, FortifyTerritoryEvent)):
            self.front = None
        
        elif isinstance(result, TradeSetEvent):
            if len(self.game.current_player.cards) <= 4:
                self.expecting_trade = False

        elif isinstance(result, (AttackManualEvent, AttackSimulateEvent)):
            if self.front.status == BattleStatus.JUST_CAPTURED:
                self.__handle_successful_attack()

            elif self.front.status == BattleStatus.REPELLED:
                self.game.event_bus.emit(AttackRepelledEvent(territory_from = self.front.territory_from,
                                                             territory_to = self.front.territory_to
                                                            ))
                self.front = None

            if isinstance(result, (AttackManualEvent)):
                self.game.stats.units_eliminated += result.attacker_units_lost
                self.game.stats.units_eliminated += result.defender_units_lost

            elif isinstance(result, AttackSimulateEvent):
                self.game.stats.units_eliminated += result.total_attacker_units_lost
                self.game.stats.units_eliminated += result.total_defender_units_lost

        if self.front and not isinstance(result, FocusOffensiveEvent) and not self.front.status == BattleStatus.EXPECTING_TRANSFER:
            self.game.event_bus.emit(ActiveFrontEvent(self.front))

        if not self.game.board.get_attackable_territories(self.game.current_player):
            self.game.event_bus.emit(NoAttacksLeftEvent(self.game.current_player))
        
        if self.expecting_trade:
            self.game.event_bus.emit(RequiredTradeEvent(self.game.current_player))
        
        if self.game.current_player.units_to_place:
            self.game.event_bus.emit(UnrecruitedUnitsEvent(units_to_place=self.game.current_player.units_to_place))

        if isinstance(result, NextTurnEvent) and not self.expecting_trade and not self.game.current_player.units_to_place:
            self._exit()

        if not self.expecting_trade and not self.attacks_left and not self.game.current_player.units_to_place:
            self._exit()
            return
    
    def __handle_successful_attack(self) -> None:
        attacking_player = self.front.territory_from.owner
        defending_player = self.front.territory_to.owner

        attacking_player.stats.total_territories_captured += 1
        defending_player.stats.total_territories_lost += 1
        self.game.stats.territory_captures += 1
        self.has_captured_territory = True
        self.game.event_bus.emit(AttackSuccessfulEvent(self.front))
        self.game.event_bus.emit(ExpectingTransferEvent(self.front))
        
        #If the player whose continent was captured has now lost it
        if self.game.board.get_continent_of_territory(self.front.territory_to).owner == defending_player:
            self.front.territory_to.owner.stats.total_continents_lost += 1

        #Check if the attacking player now controls a whole continent
        continent = self.game.board.get_continent_of_territory(self.front.territory_to)
        if continent.owner == self.game.current_player:
            self.game.event_bus.emit(ContinentCapturedEvent(player=self.game.current_player,continent=continent))
            
        self.front.status = BattleStatus.EXPECTING_TRANSFER
        self.front.territory_to.owner = attacking_player

        #Check if the defending player has now been eliminated
        if not self.game.board.get_friendly_territories(defending_player):
            self.game.event_bus.emit(PlayerEliminatedEvent(defending_player))
            self.game.stats.players_eliminated += 1
            self.game.eliminated_players.append(defending_player)
            self.game.players.remove(defending_player)

            if len(self.game.players) == 1:
                self.game.event_bus.emit(LastPlayerLeftEvent(self.game.current_player))
                self.game.set_end_phase()

            transferred_cards = defending_player.cards
            if transferred_cards:
                self.game.event_bus.emit(CardsTransferredEvent(player_from = defending_player,
                                                                player_to=attacking_player,
                                                                cards = transferred_cards
                                                                ))
                self.game.current_player.cards.extend(transferred_cards) 
                if len(self.game.current_player.cards) > AttackConfig.MAX_CARDS_AFTER_ELIMINATION:
                    self.expecting_trade = True

@dataclass
class AttackPhaseStartedEvent(ImplicitEvent):
    """
    Event emitted when the phase begins
    
    Attributes
    ----------
    player : Player
        The player whose turn it currently is
    """
    player : Player


@dataclass
class AttackPhaseEndedEvent(ImplicitEvent):
    """
    Event emitted when the phase ends
    """


@dataclass
class NoAttacksLeftEvent(ImplicitEvent):
    """
    Event emitted when there are no more 
    possible fronts 
    
    Attributes
    ----------
    player : Player
        The player who has no more fronts 
    """
    player : Player

@dataclass
class ActiveFrontEvent(ImplicitEvent):
    """
    Event emitted when there is an active
    front
    
    Attributes
    ----------
    front : OffensiveFront
        The focused on front 
        
    Notes
    -----
    This is designed to be emitted every turn.
    """
    front : OffensiveFront


@dataclass
class CardReceivedEvent(ImplicitEvent):
    """
    Event emitted when a card is received
    
    Attributes
    ----------
    player : Player
        The player receiving the card
    card : Card
        The received card
    """
    player : Player
    card : Card
    

@dataclass
class AttackSuccessfulEvent(ImplicitEvent):
    """
    Event emitted after a territory is captured
    
    Attributes
    ----------
    front: Offensive front
        The front that needs to be resolved
    """
    front: OffensiveFront

@dataclass
class ExpectingTransferEvent(ImplicitEvent):
    """
    Event emitted until a captured territory
    has been fortified

    Attributes
    ----------
    front : OffensiveFront
        The front that needs to be resolved
    """
    front: OffensiveFront

@dataclass
class AttackAutoChangeDiceEvent(ImplicitEvent):
    """
    Event emitted after the attacker/defender dice 
    changed due to a lack of units.

    Attributes
    ----------
    attacker_dice : int
        The new number of attacking dice
    defender_dice : int
        The new number of defending dice
    
    Notes
    -----
    It would be possible to make this into two separate events
    for attacking/defending dice, but they are highly coupled
    anyways and information about the other person's dice is 
    still relevant to the attacker/defender issuing the command.
    """
    attacker_dice : int
    defender_dice : int
    

@dataclass 
class AttackRepelledEvent(ImplicitEvent):
    """
    Event emitted after an attack is repelled
    
    Attributes
    ----------
    territory_from : Territory
        The territory the attack is commenced from
    territory_to : Territory
        The territory under attack 
    """
    territory_from : Territory 
    territory_to : Territory


@dataclass
class ContinentCapturedEvent(ImplicitEvent):
    """
    Event emitted when a continent is fully captured
    
    Attributes
    ----------
    player : Player
        The player who captured the continent
    continent : Continent
        The controlled continent
    """
    player : Player
    continent : Continent
    


@dataclass
class PlayerEliminatedEvent(ImplicitEvent):
    """
    Event emitted after a player is eliminated

    Attributes
    ----------
    player : Player
        The eliminated player
    """
    player : Player


@dataclass
class CardsTransferredEvent(ImplicitEvent):
    """
    Event emitted after a player seizes another 
    player's cards

    Attributes
    ----------
    player_from : Player
        The player transferring the cards
    player_to : Player
        The player receiving the cards
    cards : list[Card]
        The list of cards received
    """
    player_from : Player
    player_to : Player
    cards : list[Card]


@dataclass
class RequiredTradeEvent(ImplicitEvent):
    """
    Event emitted when the player is forced to
    trade in a set 

    Attributes
    ----------
    player : Player
        The player whose forced to trade in a set
    """
    player : Player



@dataclass
class LastPlayerLeftEvent(ImplicitEvent):
    """
    Event emitted when there is only one player left
    in the game

    Attributes
    ----------
    player : Player
        The player who is the last player left
    """
    player : Player









