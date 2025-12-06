from dataclasses import dataclass

@dataclass
class RecruitmentConfig:
    """
    The constants that govern the recruitment phase
    
    Attributes
    ----------
    MAX_CARDS : int
        The player must have this number or more cards
        to be forced to trade in a set
    CARDS_IN_SET : int
        The number of cards in a tradeable set
    FIXED_INFANTRY_ONLY : int
        The number of units granted from three
        infantry cards while fixed rules are enabled
    FIXED_CAVALRY_ONLY : int
        The number of units granted from three
        cavalry cards while fixed rules are enabled
    FIXED_ARTILLERY_ONLY : int
        The number of units granted from three
        artillery cards while fixed rules are enabled
    FIXED_MIX_SET : int
        The number of units granted from
        one of all cards while fixed rules are enabled
    PROGRESSIVE_BASE_RECRUITMENT : dict[int : int]
        While progressive is enabled, trading in 
        set gives an escalating predefined number of
        units up to 6. 
    PROGRESSIVE_EXTRA_UNITS_PER_SET : int
        The number of extra units granted for every
        additional set after after 6 sets
    MIN_UNITS_RECRUITED : int
        The minimum number of units a player gets 
        passively at the start of their recruitment 
        turn
    """
    MAX_CARDS = 5
    CARDS_IN_SET = 3
    FIXED_INFANTRY_ONLY = 4
    FIXED_CAVALRY_ONLY = 6
    FIXED_ARTILLERY_ONLY = 8
    FIXED_MIXED_SET = 10
    PROGRESSIVE_BASE_RECRUITMENT = {1: 4,
                                    2: 6,
                                    3: 8,
                                    4: 10,
                                    5: 12,
                                    6: 15
                                        }
    PROGRESSIVE_EXTRA_UNITS_PER_SET = 5
    MIN_UNITS_RECRUITED = 3


@dataclass
class PlacementConfig:
    """
    The constants that govern the placement phase

    Attributes
    ----------
    UNITS_PER_PASS : int
        After all territories have been claimed, the placement
        phase reaches the "recruitment" phase where instead of capturing
        a new territory players instead fortify a territory they own.
        After this number is reached, pass to the next player.
    TRADITIONAL_BASE_UNITS : int
        The number of units granted when 0 players
        are playing on the traditional map
    TRADITIONAL_EXTRA_PLAY_PENALTY : int
        The number of units subtracted for every extra player
        on the traditional map
    ANTIQUITY_BASE_UNITS : int
        The number of units granted when 0 players
        are playing on the antiquity map
    ANTIQUITY_EXTRA_PLAY_PENALTY : int
        The number of units subtracted for every extra player
        on the antiquity map
    """
    UNITS_PER_PASS = 3
    TRADITIONAL_BASE_UNITS = 50
    TRADITIONAL_EXTRA_PLAY_PENALTY = 5
    ANTIQUITY_BASE_UNITS = 18
    ANTIQUITY_EXTRA_PLAY_PENALTY = 2

@dataclass
class AttackConfig:
    """
    The constants that govern the attack phase
    
    Attributes
    ----------
    MAX_ATTACKER_DICE : int
        The number of dice the attacker is capped at
    MAX_DEFENDER_DICE : int
        The number of dice the defender is capped at
    MAX_CARDS_AFTER_ELIMINATION : int
        The threshold to which the player is considered
        as needing to trade in cards after eliminating
        a player and taking their cards
    """
    MAX_ATTACKER_DICE = 3
    MAX_DEFENDER_DICE = 2
    MAX_CARDS_AFTER_ELIMINATION = 7
