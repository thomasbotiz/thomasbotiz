from __future__ import annotations
from dataclasses import dataclass, field

from ...main.config import RecruitmentConfig

class Player:
    def __init__(self,
                id: int,
                name: str,
                colour: str,
                ):
        """
        An object representing a unique end user

        Parameters
        ----------
        id : int
            The unique identifier of a player
        name : str
            The display name of the plyer
        colour : PlayerColour
            The colour of the player's territories

        Attributes
        ----------
        cards : list[Card]
            The cards the player has 
        stats : PlayerStats
            Statistics relevant to only that player
            through the course of the game .
        units_to_place : int
            The number of units avilable to place
            (relevant in Recruitment, Attack, Placement)
        """
        self.id = id
        self.name = name
        self.colour = colour
        self.cards = []
        self.stats = PlayerStats()
        self.units_to_place = 0

    @property
    def can_trade_set(self) -> bool:
        """
        Checks if the player is able to return a set
        """
        if len(self.cards) < RecruitmentConfig.CARDS_IN_SET:
            return False
        
        num_infantry = 0
        num_cavalry = 0
        num_artillery = 0
        num_wildcards = 0
        for card in self.cards:
            if card.is_wildcard:
                num_wildcards += 1
            elif card.unit == "Infantry":
                num_infantry += 1
            elif card.unit == "Cavalry":
                num_cavalry += 1
            elif card.unit == "Artillery":
                num_artillery += 1
        
        #The player must have three cards at this point,  two other cards can create a valid set if a wildcard present
        if num_wildcards >= 1:
            return True
        
        if num_artillery >= 3 or num_cavalry >= 3 or num_infantry >= 3:
            return True
        
        if num_artillery >= 1 and num_cavalry >= 1 and num_infantry >= 1:
            return True

        return False
    
@dataclass
class PlayerStats:
    """
    Statistics of a player over the course of the whole game

    Attributes
    ----------
    total_territories_captured : int
        Total number of times a territory became owned by the player
    total_territories_lost : int
        Total number of times a friendly territory was captured
    total_continents_captured : int
        Total number of times a continent was captured
    total_continents_lost : int
        Total number of times a friendly continent was captured
    total_units_recruited : int
        Total number of units recruited 
    total_enemy_units_eliminated : int
        Total number of successful dice comparisons
    total_friendly_units_eliminated : int
        Total number of unsuccessful dice comparisons
    offensive_battles : int
        The number of atomic battles (not dice) occured offensively
    defensive_battles : int
        The number of atomic battles (not dice) occured defensively
    offensive_rolls : int
        The number of dice rolled while defending
    defensive_rolls : int
        The number of dice rolled while defending
    avg_attacking_dice_used : int
        The average number of dice used while attacking
    avg_defending_dice_used : int
        The average number of dice used while defending 
    total_dice_value : int
        The total of all values from the player's dice rolls
    avg_dice_value : float
        The average value of a dice roll across all dice
        rolls
    """
    total_territories_captured: int  = 0
    total_territories_lost: int = 0
    total_continents_captured: int = 0
    total_continents_lost: int = 0
    total_units_recruited: int = 0
    total_enemy_units_eliminated: int = 0 
    total_friendly_units_eliminated: int = 0
    offensive_battles: int = 0
    defensive_battles: int = 0
    offensive_rolls: int = 0
    defensive_rolls: int = 0
    total_dice_value : int = 0

    @property
    def avg_attacking_dice_used(self):
        return self.offensive_rolls/self.offensive_battles

    @property
    def avg_defending_dice_used(self):
        return self.defensive_rolls/self.defensive_battles

    @property
    def avg_dice_value(self):
        return self.total_dice_value / (self.offensive_rolls + self.defensive_rolls)
