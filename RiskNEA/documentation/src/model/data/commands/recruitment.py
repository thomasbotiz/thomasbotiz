from dataclasses import dataclass
from ...utils import Command, ExplicitEvent
from __future__ import annotations

class Game:
    pass

class RecruitmentCommand(Command):
    """
    The family of classes only allowed to execute during the Recruitment phase.
    """
    pass

@dataclass
class RecruitUnitEvent(ExplicitEvent):
    """
    Event emitted when the player place unit to a territory
    in their attack phase

    Attributes
    ----------
    success : bool
        Whether the command successfully executed
    error : str
        The error message that came with the failed command(None assumes success)
    player : Player
        The player who issued the recruitment command
    territory_placed_on : Territory
        The territory that a unit was recruited on
    units_placed : int
        The number of units placed on the territory
    """

class TradeSetCommand(Command):
    def __init__(self):
        """
        A command to trade in a set of cards
        
        Attributes
        ----------
        Cards : List[Card]
            The cards being traded in by the player
        """
        pass

    def execute(self, game: Game) -> TradeSetEvent:
        """
        Add the corresponding number of units to a player's
        `unplaced_units` if the cards are valid 

        Returns
        -------
        AttackTradeSetEvent
            Data representing the change made to `Game`
        
        success : bool
            True if cards were validated else false
        error : str
            Accompanying error message if success is False
        player : Player
            The player who issued the command to trade in the set
        set_traded_in : list[Card]
            The set that was just traded in 
        
        Notes
        -----
        Should use `Games` interface to calculate how many units
        the set is worth 
        """
        pass

    def _validate(self, game: Game) -> str:
        """
        Checks if it is legal to trade in the set of cards
        
        Returns
        -------
        str
            The accompanying error message(None assumes command is valid)

        Notes
        -----
        TradeSetAttackCommand would fully validate if: 

        There are three cards in `Cards`.

            AND 

        The current player owns all three of those cards.

            AND 

        The cards combine to form a valid set.
        """
        pass

@dataclass
class TradeSetEvent(ExplicitEvent):
    """
    An event emitted after AttackTradeSetCommand is called
    
    Attributes
    ----------
    success : bool
        Whether the command successfully executed
    error : str
        The error message that came with the failed command(None assumes success)
    player : Player
        The player who issued the recruitment command
    set_traded_in : list[Card]
        The cards that were traded in
    units_received : int
        The units received at the start of the turn/from trading in the set
    """
    pass