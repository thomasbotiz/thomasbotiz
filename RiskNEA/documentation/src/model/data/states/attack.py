from ...utils.templates import State, Command, ImplicitEvent, ExplicitEvent
from ...main.game import Game
from __future__ import annotations
from enum import Enum
from utils.game_enums import BattleStatus
from dataclasses import dataclass

class Territory:
    pass

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
        game : Game
            The game instance that owns State
        current_player : Player
            The player whose attack turn it is 
        front : OffensiveFront 
            Information about the focused on offensive front
        expecting_trade : bool
            True once the player has > 6 cards (by default)
            and False once player has < 5 cards (by default)
        unplaced_units : int
            The number of unplaced units 
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
        pass

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
        pass

    def _validate(self, command: Command) -> str:
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
        only allow commands of instance TradeSetCommand

        If expecting_transfer is false and expecting_trade is false
        and unplaced_units is greater than zero only allow commands of 
        instance PlaceUnitAttackCommand

        The list of allowed commands are: Save, Load, TradeSet, PlaceUnit,
        FocusOffensive, CancelOffensive, AttackManualCommand, AttackAutoCommand,
        ChangeAttackerDice, ChangeDefenderDice, ChangeLossThreshold, 
        FortifyCapturedTerritory, NextTurn

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
        
        Issue to Game to transfer to the next phase if necessary.

        Emitted Events
        --------------
        FocusOffensiveEvent
            If a front was focused on
        CancelFocusOffensiveEvent
            If a front was cancelled
        AttackManualEvent
            If a manual attack occurred
        AttackSimulateEvent
            If a simulation attack occurred
        AttackChangeAttackerDiceEvent
            If the attacker dice was changed 
        AttackChangeDefenderDiceEvent
            If the attacker dice was changed
        AttackChangeLossThresholdEvent
            If the loss threshold was changed
        AttackAutoChangeDiceEvent
            If the defender/attacker no longer has 
            enough units to sustain that number
            of dice.
        PlaceUnitAttackEvent
            If the player placed a unit
        AttackTradeSetEvent
            If the player trades in a set
        FortifyCapturedTerritoryEvent
            If a territory was fortified after an attack
        NoAttacksLeftEvent
            If there are no more valid attacks
        IsActiveFrontEvent
            If front is not None 
        AttackSuccessfulEvent
            If status is just_captured
        AttackRepelledEvent
            If status is repelled
        ContinentCapturedEvent
            If a continent was fully captured
        PlayerEliminatedEvent
            If a player now has zero territories left
        CardsTransferredEvent
            If a player obtains cards
        RequiredTradeEvent
            If expecting_trade is true
        LastPlayerLeftEvent
            If there is only one not eliminated player
        """

    def on_exit(self):
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

@dataclass
class OffensiveFront:
    """
    Representation of the battle which the current player is 
    focusing on. 
    
    Attributes
    ---------
    territory_from : Territory
        The attacking territory
    territory_to : Territory
        The defending territory
    attacker_dice : int
        The number of dice the attacker is using
    defender_dice : int 
        The number of dice the defender is using 
    loss_threshold : int
        The instant the attacker has less units than this
        value, stop simulating the attack(default = 0)
    status : BattleStatus 
        Information about what is occuring in the current front

    Notes
    -----
    Ephemeral storage for when a player is focusing on a territory,
    necessary to remember loss_threshold, attacker_dice and defender_dice

    Dice and battle simulation commands can only be issued if OffensiveFront
    is not None.        
    """
    pass

@dataclass
class AttackPhaseStartedEvent(ImplicitEvent):
    """
    Event emitted when the phase begins
    
    Attributes
    ----------
    player : Player
        The player whose turn it is 
    """

@dataclass
class AttackPhaseEndedEvent(ImplicitEvent):
    """
    Event emitted when the phase ends
    
    Attributes
    ----------
    player : Player
        The player whose turn it was
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

@dataclass
class IsActiveFrontEvent(ImplicitEvent):
    """
    Event emitted when there is an active
    front
    
    Attributes
    ----------
    player_from : Player
        The player commencing the attack
    player_to : Player
        The player defending
    territory_from : Territory
        The territory the attack is commenced from
    territory_to : Territory
        The territory under attack 
    """

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

@dataclass
class AttackSuccessfulEvent(ImplicitEvent):
    """
    Event emitted after a territory is captured
    
    Attributes
    ----------
    player_from : Player
        The attacking player
    player_to : Player
        The player defending
    territory_from : Territory
        The territory the attack is commenced from
    territory_to : Territory
        The territory under attack 
    """

@dataclass
class AttackAutoChangeDice(ImplicitEvent):
    """
    Event emitted after the attacker/defender dice 
    changed due to a lack of units.

    Attributes
    ----------
    attacker_dice : int
        The new number of attacking dice
    defender_dice : int
        The new number of defending dice
    """

@dataclass 
class AttackRepelledEvent(ImplicitEvent):
    """
    Event emitted after an attack is repelled
    
    Attributes
    ----------
    player_from : Player
        The attacking player
    player_to : Player
        The player defending
    territory_from : Territory
        The territory the attack is commenced from
    territory_to : Territory
        The territory under attack 
    """

@dataclass
class ContinentCapturedEvent(ImplicitEvent):
    """
    Event emitted when a continent is fully captured
    
    Attributes
    ----------
    player : Player
        The player who controlls the continent
    continent : Continent
        The controlled continent
    """
@dataclass
class PlayerEliminatedEvent(ImplicitEvent):
    """
    Event emitted after a player is eliminated

    Attributes
    ----------
    player : Player
        The eliminated player
    """

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

@dataclass
class RequiredTradeEvent(ImplicitEvent):
    """
    Event emitted when the player is forced to
    trade in a set 
    """

@dataclass
class LastPlayerLeftEvent(ImplicitEvent):
    """
    Event emitted when there is only one player left
    in the game
    """









