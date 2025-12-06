from utils.stack import Stack
from utils.game_enums import CardType

from board import board
from enum import Enum
from __future__ import annotations

class TerritoryName:
    pass

class Deck(Stack):
    def __init__(self):
        """
        Stack data structure for the cards in the game.

        Attributes
        ----------
        cards : Stack[Card]
            The list of cards in the game
        number_of_wildcards : int
            The number of wildcards present(default = 2)
        """
    
    @property 
    def is_empty(self) -> None:
        """
        Returns if the deck is empty
        """
        
    def populate_deck(self) -> None:
        """
        Adds every card in the game back to the deck
        and shuffles it 

        Notes
        -----
        Should use the card data from card_data.py
        """
    
class Card:
    def __init__(self,
                territory_shown : TerritoryName = None,
                unit_shown : CardType = None
                ):
        """
        Either a standard card or a wildcard
        
        Parameters
        ----------
        territory_shown : TerritoryName
            The territory displayed(None assumes wildcard)
        unit_shown : CardType
            The unit shown on the card(None assumes wildcard)
        """

    @property
    def is_wildcard(self):
        """
        Checks if the card specifies a territory or a unit
        """
