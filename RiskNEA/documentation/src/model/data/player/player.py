from enum import Enum
from dataclasses import dataclass
from __future__ import annotations
from utils.game_enums import PlayerColour

class Card:
    pass

class Player:
    def __init__(self,
                player_id: int,
                name: str,
                colour: PlayerColour,
                cards: list[Card],
                ):
        """
        An object representing a unique end user

        Parameters
        ----------
        player_id : int
            The unique identifier of a player
        name : str
            The display name of the plyer
        colour : PlayerColour
            The colour of the player's territories

        Attributes
        ----------
        player_id : int
            The unique identifier of a player
        name : str
            The display name of the plyer
        colour : PlayerColour
            The colour of the player's territories
        cards : list[Card]
            The cards the player has 
        stats : PlayerStats
            Statistics relevant to only that player
            through the course of the game .
        units_to_place : int
            The number of units avilable to place
            (relevant in Recruitment, Attack, Placement)
        """
        pass

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
        The number of battles (not dice) used offensively
    defensive_battles : int
        The number of battles (not dice) used defensively
    offensive_rolls : int
        The number of dice rolled while defending
    defensive_rolls : int
        The number of dice rolled while defending
    avg_attacking_dice_used : int
        The average number of dice used while attacking
    avg_defending_dice_used : int
        The average number of dice used while defending 
    avg_dice_value : float
        The average value of a dice roll across all dice
        rolls
    """
