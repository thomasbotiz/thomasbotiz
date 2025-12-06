from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
    from ..data.board import Territory
    
class BattleStatus(Enum):
    """
    A representation of the front during the attack state

    Attributes
    ----------
    ONGOING 
        If combat between the two territories is possible
    REPELLED
        If the attacking territory has one unit left
    JUST_CAPTURED
        If the defending territory has zero units left but
        expecting_transfer is false 
    EXPECTING_TRANSFER
        True once just_captured turns true 

    """
    ONGOING = "Ongoing"
    REPELLED = "Repelled"
    JUST_CAPTURED = "Just Captured"
    EXPECTING_TRANSFER = "Expecting Transfer"


@dataclass
class OffensiveFront:
    """
    Representation of the battle which the current player is 
    focusing on. 
    
    Attributes
    ---------
    territory_from : Territory
        The attacking territory
    territory_to : Territory
        The defending territory
    attacker_dice : int
        The number of dice the attacker is using
    defender_dice : int 
        The number of dice the defender is using 
    loss_threshold : int
        The instant the attacker has less units than this
        value, stop simulating the attack(default = 0)
    status : BattleStatus 
        Information about what is occuring in the current front

    Notes
    -----
    Ephemeral storage for when a player is focusing on a territory,
    necessary to remember loss_threshold, attacker_dice and defender_dice

    Dice and battle simulation commands can only be issued if OffensiveFront
    is not None.        
    """
    territory_from: Territory
    territory_to: Territory
    attacker_dice: int
    defender_dice: int
    loss_threshold: int
    status: BattleStatus

    def manual_attack(self):
        attacker_rolls = self.__roll_dice(self.attacker_dice)
        defender_rolls = self.__roll_dice(self.defender_dice)

        attacker_units_lost = 0
        defender_units_lost = 0
        for attacker_roll, defender_roll in zip(attacker_rolls, defender_rolls):
            if attacker_roll > defender_roll:
                defender_units_lost += 1
            elif defender_roll >= attacker_roll:
                attacker_units_lost += 1

        self.territory_from.units -= attacker_units_lost
        self.territory_to.units -= defender_units_lost

        self.territory_from.owner.stats.offensive_battles += 1
        self.territory_from.owner.stats.offensive_rolls += len(attacker_rolls)
        self.territory_from.owner.stats.total_friendly_units_eliminated += attacker_units_lost
        self.territory_from.owner.stats.total_enemy_units_eliminated += defender_units_lost
        self.territory_from.owner.stats.total_dice_value += sum(attacker_rolls)

        self.territory_to.owner.stats.defensive_battles += 1
        self.territory_to.owner.stats.defensive_rolls += len(defender_rolls)
        self.territory_to.owner.stats.total_friendly_units_eliminated += defender_units_lost
        self.territory_to.owner.stats.total_enemy_units_eliminated += attacker_units_lost
        self.territory_to.owner.stats.total_dice_value += sum(defender_rolls)

        self.__resolve_losses()
        self.__update_status()

        return ManualBattleResult(front = self,
                                 attacker_rolls=attacker_rolls,
                                 defender_rolls=defender_rolls,
                                 attacker_units_lost=attacker_units_lost,
                                 defender_units_lost=defender_units_lost
                                 )

    def simulate_attack(self):
        total_attacking_units_lost = 0
        total_defending_units_lost = 0

        while self.status == BattleStatus.ONGOING and self.territory_from.units > self.loss_threshold:
            result = self.manual_attack()
            total_attacking_units_lost += result.attacker_units_lost
            total_defending_units_lost += result.defender_units_lost
        
        return SimulateBattleResult(front=self,
                                    total_attacker_units_lost=total_attacking_units_lost,
                                    total_defender_units_lost=total_defending_units_lost
                                    )
    
    @property 
    def max_attacker_dice(self):
        return min(3, self.territory_from.units - 1)
    
    @property
    def max_defender_dice(self):
        return min(2, self.territory_to.units)
    
    def __update_status(self):
        if self.status == BattleStatus.ONGOING:
            if self.territory_from.units <= 1:
                self.status = BattleStatus.REPELLED
            elif self.territory_to.units <= 0:
                self.status = BattleStatus.JUST_CAPTURED
            
    def __resolve_losses(self):
        """
        An attacker or defender could have more dice
        than allowed because it loses too many units. 
        This clamps the number of dice used to the max allowed.
        """
        self.attacker_dice = min(self.max_attacker_dice, self.attacker_dice)
        self.defender_dice = min(self.max_defender_dice, self.defender_dice)

    def __roll_dice(self, num_dice: int):
        rolls = []
        for i in range(num_dice):
            rolls.append(random.randint(1,6))
        rolls.sort(reverse=True)
        return rolls

@dataclass
class ManualBattleResult:
    front: OffensiveFront
    attacker_rolls: list[int]
    defender_rolls: list[int]
    attacker_units_lost: int
    defender_units_lost: int  

@dataclass
class SimulateBattleResult: 
    front: OffensiveFront
    total_attacker_units_lost: int
    total_defender_units_lost: int