from enum import Enum

class GameMode(Enum):
    """
    The gamemodes Game can be created in
    
    Attributes
    ----------
    LOCAL_PLAY
        Local play
    TRAINING
        Training
    SIMULATION
        Simulation
    """

class PlayerColour(Enum):
    """
    The list of colours that can represent
    a player in the View

    Attributes
    ----------
    RED
        Red
    BLUE
        Blue
    YELLOW
        Yellow
    GREEN
        Green
    PURPLE
        Purple
    ORANGE
        Orange
    """

class ContinentName(Enum):
    """
    The names of all game continents

    Attributes
    ----------
    NORTH_AMERICA
        North America
    SOUTH_AMERICA
        South America
    ...
    AUSTRALIA
        Australia
    """

class TerritoryName(Enum):
    """
    The names of all territories
    
    Attributes
    ----------
    ALASKA
        Alaska
    ...
    EASTERN_AUSTRALIA
        Eastern Australia
    """
    
class ContinentColour(Enum):
    """
    The list of colours a continent can take
    
    Attributes
    ----------
    RED
        red
    BLUE
        blue
    YELLOW
        yellow
    GREEN
        green
    ORANGE
        orange
    PURPLE
        purple
    """

class CardType(Enum):
    """
    The unit shown on a standard card. 
    Attributes
    ----------
    INFANTRY
        An infantry unit
    CAVALRY
        A cavalry unit
    ARTILLERY
        An artillery unit 
    """

class BattleStatus(Enum):
    """
    A representation of the front during the attack state

    Attributes
    ----------
    ongoing 
        If combat between the two territories is possible
    repelled
        If the attacking territory has one unit left
    just_captured
        If the defending territory has zero units left but
        expecting_transfer is false 
    expecting_transfer
        True once just_captured turns true 
    cancelled
        Failsafe if front was abandoned 
    """

class PlacementRules(Enum):
    """
    Attributes
    ----------
    MANUAL_PLACEMENT
        Placing manually at the start
    AUTOMATIC_PLACEMENT
        Placing automatically at the start
    """

class MapRules(Enum):
    """
    Attributes
    ----------
    TRADITIONAL_MAP
        The traditional map
    ANTIQUITY_MAP
        The antiquity map
    """

class RecruitmentRules(Enum):
    """
    Attributes
    ----------
    PROGRESSIVE_RECRUITMENT
        Progressive recruitment rules
    FIXED_RECRUITMENT
        Fixed recruitment rules
    """

class FortifyRules(Enum):
    """
    Attributes
    ----------
    CONTIGUOUS_FORTIFY
        Contiguous fortification
    ADJCENT_FORTIFY
        Adjacent Fortification
    """

class WinConditionRules(Enum):
    """
    Attributes
    ----------
    100%_WIN_CONDITION
        If 100% of territories are needed to win
    70%_WIN_CONDITION
        If 70% of territories are needed to win
    """

