from dataclasses import *

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
    WIN_CONDITION
        The rules on the win condition
   
    Notes
    -----
    Should be read-only after instantiation.
    """
