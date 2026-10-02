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
    
    def _save_data(self) -> dict:
        return {"body": [card.__dict__ for card in self.body],
                "traded_in_cards":  [card.__dict__ for card in self.traded_in_cards]
               }
    
    def _load_data(self, deck_data: dict, card_lookup: dict):
        self.body = [card_lookup[card_data["id"]] for card_data in deck_data["body"]]
        self.traded_in_cards = [card_lookup[card_data["id"]] for card_data in deck_data["traded_in_cards"]]

    def initialise_cards(self) -> dict:
        """
        Initialises every card from the text file

        Notes
        -----
        Should use the card data from card_data.py.
        Note that the card_data.json MUST be structured
        to have the same attributes as the Card object itself,
        otherwise **kwargs returns an error.

        Returns
        -------
        dict
            The lookup table of the Cards ID to Card object
        """
        file_location = pathlib.Path(__file__).parent / "cards.json"
        try:
            with open(file_location, "r") as json_file:
                card_data = json.load(json_file)
            
            card_lookup = {}
            for card in card_data.values():
                new_card = Card(**card)
                self.body.append(new_card)
                card_lookup[new_card.id] = new_card

            return card_lookup
        
        except Exception as e:
            print("Error loading the card data!")
            print(e)
    
    def draw_card(self) -> Card:
        if self.is_empty:
            self.repopulate()
            self.shuffle()
        
        card = self.body.pop()
        return card
    
    def repopulate(self) -> None:
        """
        Adds every traded in card back to the deck.
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
                id : int,
                territory : str = None,
                unit : str = None
                ):
        """
        Either a standard card or a wildcard
        
        Parameters
        ----------
        id : int
            The identifier of the Card
        territory_shown : str
            The id of the territory displayed(None assumes wildcard)
        unit_shown : CardType
            The unit shown on the card(None assumes wildcard)
        """
        self.id = id
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

