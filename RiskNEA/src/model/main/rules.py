
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

@dataclass
class GameRules:
    """
    Container for the rules used for the game.
   
    Attributes
    ----------
    PLACEMENT : PlacementRules
        The rules on placement
    MAP : MapRules
        The rules on the map
    RECRUITMENT : RecruitmentRules
        The rules on recruitment
    FORTIFICATION : FortifyRules
        The rules on fortification
    WIN_CONDITION : WinConditionRules
        The rules on the win condition
   
    Notes
    -----
    Should be read-only after instantiation.
    """
    PLACEMENT : PlacementRules
    MAP : MapRules
    RECRUITMENT : RecruitmentRules
    FORTIFICATION : FortifyRules
    WIN_CONDITION : WinConditionRules

    def _save_data(self) -> dict:
        rules_data = {}
        rules_data["PLACEMENT"] = self.PLACEMENT.value
        rules_data["MAP"] = self.MAP.value
        rules_data["RECRUITMENT"] = self.RECRUITMENT.value
        rules_data["FORTIFICATION"] = self.FORTIFICATION.value
        rules_data["WIN_CONDITION"] = self.WIN_CONDITION.value
        return rules_data
    
class PlacementRules(Enum):
    """
    Attributes
    ----------
    MANUAL
        Placing manually at the start
    AUTOMATIC
        Placing automatically at the start
    """
    MANUAL_PLACEMENT = "Manual Placement"
    AUTOMATIC_PLACEMENT = "Automatic Placement"

class MapRules(Enum):
    """
    Attributes
    ----------
    TRADITIONAL
        The traditional map
    ANTIQUITY
        The antiquity map
    """
    TRADITIONAL = "Traditional"
    ANTIQUITY = "Antiquity"

class RecruitmentRules(Enum):
    """
    Attributes
    ----------
    PROGRESSIVE
        Progressive recruitment rules
    FIXED
        Fixed recruitment rules
    """
    PROGRESSIVE = "Progressive"
    FIXED = "Fixed"

class FortifyRules(Enum):
    """
    Attributes
    ----------
    CONTIGUOUS
        Two territories must be directly connected to fortify
    ADJACENT
        It must be possible to make a path of friendly territories 
    """
    CONTIGUOUS = "Contiguous"
    ADJACENT = "Adjacent"

class WinConditionRules(Enum):
    """
    Attributes
    ----------
    HUNDRED_PERCENT
        If 100% of territories are needed to transition to end phase
    SEVENTY_PERCENT
        If 70% of territories are needed to transition to end phase
    """
    HUNDRED_PERCENT = "100%"
    SEVENTY_PERCENT = "70%"


