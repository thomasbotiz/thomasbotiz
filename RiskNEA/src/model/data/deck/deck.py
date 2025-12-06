from __future__ import annotations
import pathlib
import random
import json

from ...utils.stack import Stack

class Deck(Stack):
    def __init__(self, body: list[Card] = None):
        """
        Parameters
        ----------
        body : list[Card]
            The list of cards in the game

        Stack data structure for the cards in the game.

        Attributes
        ----------
        body : list[Card]
            The list of cards in the game
        """
        super().__init__(body)
        self.traded_in_cards = []
    
    def initialise_cards(self) -> None:
        """
        Initialises every card from the text file

        Notes
        -----
        Should use the card data from card_data.py.
        Note that the card_data.json MUST be structured
        to have the same attributes as the Card object itself,
        otherwise **kwargs returns an error.
        """
        directory = pathlib.Path(__file__).parent
        file_location = directory / "cards.json"
        try:
            with open(file_location, "r") as json_file:
                card_data = json.load(json_file)
            
            for card_attributes in card_data.values():
                self.body.append(Card(**card_attributes))

        except Exception as e:
            print(e)

    def repopulate(self) -> None:
        """
        Adds every traded in card back to the deck.
        
        :param self: Description
        """
        for i in range(len(self.traded_in_cards)):
            self.push(self.traded_in_cards[i])
        self.traded_in_cards = []
    
    def shuffle(self) -> None:
        """
        Reorders the cards in the deck randomly

        Notes
        -----
        It is possible to shuffle the body immediately,
        but I want to respect how the stack is structured.
        """
        cards = []
        while not self.is_empty:
            cards.append(self.pop())
        random.shuffle(cards)
        
        for i in range(len(cards)):
            self.push(cards[i])
    
    def clear_deck(self) -> None:
        """
        Removes all cards from the deck
        """
        self.body = []   

class Card:
    def __init__(self,
                territory : str = None,
                unit : str = None
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
        self.territory = territory
        self.unit = unit

    @property
    def is_wildcard(self):
        """
        Checks if the card specifies a territory or a unit

        Notes
        -----
        It is implicitly applied that a card is a wildcard if it has either
        no territory or no unit or both.
        """
        return not(self.territory and self.unit)

