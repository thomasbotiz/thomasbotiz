from __future__ import annotations
import math

from model import *

class AIController:
    def __init__(self, 
                player: Player, 
                game: Game,
                chromosome: AIChromosome,
                difficulty: str
                ):
        self.player = player
        self.game = game
        self.chromosome = chromosome
        self.difficulty = difficulty
        self.territories_captured_in_turn = 0
        self.place_commands_to_execute = Queue() 

        self.game.event_bus.subscribe(AttackPhaseStartedEvent, self.attack)
        self.game.event_bus.subscribe(AttackCommandCompletedEvent, self.attack)
        self.game.event_bus.subscribe(RecruitmentPhaseStartedEvent, self.recruit)
        self.game.event_bus.subscribe(UnitsRecruitedEvent, self.recruit)
        self.game.event_bus.subscribe(RequiredTradeEvent, self.recruit)
        self.game.event_bus.subscribe(RecruitmentCommandCompletedEvent, self.recruit)
        self.game.event_bus.subscribe(FortifyPhaseStartedEvent, self.fortify)

    def recruit(self, event: UnitsRecruitedEvent|RequiredTradeEvent|RecruitmentCommandCompletedEvent) -> None:
        if self.game.current_player == self.player:
            best_set = self.__get_best_set()
            if best_set:
                self.game.execute(TradeSetCommand(best_set))
            if self.player.units_to_place:
                self.__distribute_units(self.chromosome.recruitment_softmax_temp)

    def attack(self, event: AttackPhaseStartedEvent|AttackCommandCompletedEvent) -> None:
        if self.game.current_player == self.player:  
            if self.player.units_to_place:
                    self.__distribute_units(self.chromosome.recruitment_softmax_temp)
            if self.game.front and self.game.front.status == BattleStatus.EXPECTING_TRANSFER:
                self.territories_captured_in_turn += 1
                territory_from = self.game.front.territory_from
                territory_to = self.game.front.territory_to
                units_transferred = max(self.game.front.attacker_dice, self.__get_optimal_distribution([territory_from, territory_to], territory_from.units - 1, self.chromosome.attack_softmax_temp)[1])
                self.game.execute(FortifyTerritoryCommand(territory_from, territory_to, units_transferred))  

            elif self.game.front:
                self.game.execute(AttackSimulateCommand())
            
            best_front = self.__get_optimal_offensive_front()
            if best_front: 
                if not self.game.front:
                    self.game.execute(FocusOffensiveCommand(best_front[0], best_front[1]))
            else:
                self.territories_captured_in_turn = 0
                self.game.execute(NextTurnCommand())
            
    def fortify(self, event: FortifyPhaseStartedEvent) -> None:
        if self.game.current_player == self.player:
            fortifying_territories = sorted([territory for territory in self.game.board.get_friendly_territories(self.player) if territory.units >= 2 and len(territory.connected_enemy_territories) == 0],
                                            key=lambda territory: territory.units, 
                                            reverse=True
                                           )
            if not fortifying_territories: 
                self.game.execute(NextTurnCommand())
                return
            border_territories = sorted([territory for territory in self.game.board.get_friendly_territories(self.player) if len(territory.connected_enemy_territories) > 0],
                                        key=lambda territory: self.__get_priority_score(territory, fortifying_territories[0].units), 
                                        reverse=True
                                        )
            for high_priority_territory in border_territories:
                for high_unit_core_territory in fortifying_territories:
                    if self.game.board.has_adjacency(high_unit_core_territory, high_priority_territory):
                        self.game.execute(FortifyTerritoryCommand(high_unit_core_territory, high_priority_territory, high_unit_core_territory.units-1))
            self.game.execute(NextTurnCommand())

    @staticmethod
    def __softmax(scores: list[float], temperature) -> list[float]:
        max_score = max(scores)
        exponents = [math.exp((score-max_score)*temperature) for score in scores]
        total = sum(exponents)
        return [exponent_score/total for exponent_score in exponents]
    
    def __scale_chromosome(self, raw_score: float, k: float=7.5) -> float:
        return k*((raw_score/k) + ((raw_score/k)**3)/6 + ((raw_score/k)**5)/120 + ((raw_score/k)**7)/5040)
            
    def __get_offensive_front_score(self, territory_from: Territory, territory_to: Territory) -> float:
        affected_continent = self.game.board.get_continent_of_territory(territory_to)
        affected_continent_num_territories = len(affected_continent.territories)
        attacker_player = territory_from.owner
        defender_player = territory_to.owner
        attacker_territories = self.game.board.get_friendly_territories(attacker_player)
        defender_territories = self.game.board.get_friendly_territories(defender_player)
        attacker_total_units = sum([territory.units for territory in attacker_territories])
        defender_total_units = sum([territory.units for territory in defender_territories])
        attacker_passive_recruitment = self.game.board.get_passive_recruitment(attacker_player)
        defender_passive_recruitment = self.game.board.get_passive_recruitment(defender_player)
        continent_attacker_territories_num = len([territory for territory in affected_continent.territories if territory.owner == attacker_player])
        continent_defender_territories_num = len([territory for territory in affected_continent.territories if territory.owner == defender_player])
        attacker_units_density = attacker_total_units/len(attacker_territories)
        defender_units_density = defender_total_units/len(defender_territories)
        attacker_bonus_density = affected_continent.bonus/(affected_continent_num_territories-continent_attacker_territories_num) if not affected_continent.owner == attacker_player else 0
        defender_bonus_density = affected_continent.bonus/(affected_continent_num_territories-continent_defender_territories_num) if not affected_continent.owner == defender_player else 0
        attacker_cards_awarded = (1 if not self.territories_captured_in_turn else 0) + (len(defender_player.cards) if len(defender_territories) == 1 else 0)
        defender_recruitment_denied = (1 if len(defender_territories) % 3 == 0 else 0) + (affected_continent.bonus if affected_continent.owner == defender_player else 0)
        card_bonus_awarded = (1 if any(card.territory == territory_to.id for card in attacker_player.cards) else 0)
        attacker_territory_unique_connected_players = len(set([territory.owner for territory in territory_from.connected_territories if territory.owner != attacker_player]))
        defender_territory_unique_connected_players = len(set([territory.owner for territory in territory_to.connected_territories if territory.owner != defender_player]))
        attacker_territory_connected_friendly_units = sum([territory.units for territory in territory_from.connected_territories if territory.owner == attacker_player])
        defender_territory_connected_friendly_units = sum([territory.units for territory in territory_to.connected_territories if territory.owner == defender_player])

        score = 0
        score += (territory_from.units - 1) * self.__scale_chromosome(self.chromosome.bonus_attacking_units)
        score += territory_to.units * self.__scale_chromosome(self.chromosome.bonus_defending_units)
        score += attacker_total_units * self.__scale_chromosome(self.chromosome.bonus_attacker_total_units)
        score += defender_total_units * self.__scale_chromosome(self.chromosome.bonus_defender_total_units)
        score += len(attacker_territories) * self.__scale_chromosome(self.chromosome.bonus_attacker_total_territories)
        score += len(defender_territories) * self.__scale_chromosome(self.chromosome.bonus_defender_total_territories)
        score += attacker_units_density * self.__scale_chromosome(self.chromosome.bonus_attacker_unit_density)
        score += defender_units_density * self.__scale_chromosome(self.chromosome.bonus_defender_unit_density)
        score += attacker_passive_recruitment * self.__scale_chromosome(self.chromosome.bonus_passive_attacker_recruitment)
        score += defender_passive_recruitment * self.__scale_chromosome(self.chromosome.bonus_passive_defender_recruitment)
        score += attacker_bonus_density * self.__scale_chromosome(self.chromosome.bonus_continent_capture_attacker)
        score += defender_bonus_density * self.__scale_chromosome(self.chromosome.bonus_continent_capture_defender)
        score += defender_recruitment_denied * self.__scale_chromosome(self.chromosome.bonus_recruitment_denied)
        score += attacker_cards_awarded * self.__scale_chromosome(self.chromosome.bonus_per_card_gained)
        score += card_bonus_awarded * self.__scale_chromosome(self.chromosome.bonus_attacker_has_matching_card)
        score += territory_to.turn_last_captured * self.__scale_chromosome(self.chromosome.bonus_turns_since_last_capture_territory)
        score += len(territory_from.connected_territories) * self.__scale_chromosome(self.chromosome.bonus_attacker_connected_total)
        score += len(territory_from.connected_friendly_territories) * self.__scale_chromosome(self.chromosome.bonus_attacker_connected_friendly)
        score += len(territory_from.connected_enemy_territories) * self.__scale_chromosome(self.chromosome.bonus_attacker_connected_enemy)
        score += attacker_territory_connected_friendly_units * self.__scale_chromosome(self.chromosome.bonus_attacker_connected_friendly_units)
        score += len(territory_to.connected_territories) * self.__scale_chromosome(self.chromosome.bonus_defender_connected_total)
        score += len(territory_to.connected_friendly_territories) * self.__scale_chromosome(self.chromosome.bonus_defender_connected_friendly)
        score += len(territory_to.connected_enemy_territories) * self.__scale_chromosome(self.chromosome.bonus_defender_connected_enemy)
        score += defender_territory_connected_friendly_units * self.__scale_chromosome(self.chromosome.bonus_defender_connected_friendly_units)
        score += attacker_territory_unique_connected_players * self.__scale_chromosome(self.chromosome.bonus_unique_players_connected_attacker)
        score += defender_territory_unique_connected_players * self.__scale_chromosome(self.chromosome.bonus_unique_players_connected_defender)
        score += self.territories_captured_in_turn * self.__scale_chromosome(self.chromosome.bonus_total_captured_this_turn)
        score += len(self.game.players) * self.__scale_chromosome(self.chromosome.bonus_active_players)

        if self.difficulty == "Easy":
            return score * random.uniform(0.6, 1.4)
        elif self.difficulty == "Medium":
            return score * random.uniform(0.8, 1.2)
        else:
            return score  
    
    def __get_priority_score(self, territory: Territory, available_units: int) -> float:
        defensive_priority = sum([self.__get_offensive_front_score(enemy_territory, territory) for enemy_territory in territory.connected_enemy_territories])
        territory.units += available_units
        offensive_priority = max([self.__get_offensive_front_score(territory, enemy_territory) for enemy_territory in territory.connected_enemy_territories], default=0)
        territory.units -= available_units
        return defensive_priority * self.chromosome.priority_defense_multiplier + offensive_priority * self.chromosome.priority_attack_multiplier

    def __get_optimal_distribution(self, territories: list[Territory], available_units: int, softmax_temp: float) -> list[int]:
        proportions = self.__softmax([self.__get_priority_score(territory, available_units) for territory in territories], softmax_temp)
        if not proportions:
            self.game.execute(NextTurnCommand())
            return
        units_allocated = [math.floor(available_units * proportion) for proportion in proportions]
        rounding_error = available_units - sum(units_allocated)
        sorted_proportions = sorted(proportions, reverse=True)
        for i in range(rounding_error):
            index_of_territory_to_have_extra_unit = proportions.index(sorted_proportions[i])
            units_allocated[index_of_territory_to_have_extra_unit] += 1
            proportions[index_of_territory_to_have_extra_unit] = 0#So it can then check the next item in the list
        return units_allocated
    
    def __distribute_units(self, softmax_temp: float) -> None:
        if self.place_commands_to_execute.is_empty:
            territories = self.game.board.get_friendly_territories(self.player)
            units_allocated = self.__get_optimal_distribution(territories, self.player.units_to_place, softmax_temp)
            for territory, units in zip(territories, units_allocated):
                if units > 0:
                    self.place_commands_to_execute.enqueue(PlaceUnitCommand(territory, units))
        self.game.execute(self.place_commands_to_execute.dequeue())

    def __get_best_set(self) -> Optional[tuple[Card]]:
        best_set = None
        best_set_value = 0
        n = len(self.player.cards)
        for i in range(n-2):
            for j in range(i+1, n-1):
                for k in range(j+1, n):
                    card_set = (self.player.cards[i],self.player.cards[j],self.player.cards[k])
                    set_value = self.game.get_set_value(card_set)
                    if any(territory for territory in self.game.board.get_friendly_territories(self.player) if territory.id in [card.territory for card in card_set]) and set_value != 0:
                        set_value += 2
                    if set_value > best_set_value:
                        best_set_value = set_value
                        best_set = card_set
        return best_set

    def __get_optimal_offensive_front(self) -> Optional[list[Territory, Territory]]:
        fronts = [[friendly_territory, enemy_territory]
                   for friendly_territory in self.game.board.get_friendly_territories(self.player) if friendly_territory.units > 1
                   for enemy_territory in friendly_territory.connected_attackable_territories]

        best_front = max(fronts, key=lambda front: self.__get_offensive_front_score(front[0], front[1]), default = None)
        return best_front if best_front and self.__get_offensive_front_score(best_front[0], best_front[1]) > self.chromosome.min_attack_threshold else None

@dataclass
class AIChromosome:
    fitness: float = 0.0
    games_played: int = 0

    recruitment_softmax_temp: float  = 0.0
    attack_softmax_temp: float = 0.0

    min_attack_threshold: float = 0.0
    priority_attack_multiplier: float  = 0.0
    priority_defense_multiplier: float = 0.0

    bonus_attacking_units: float = 0.0
    bonus_defending_units: float = 0.0
    bonus_attacker_total_units: float = 0.0
    bonus_defender_total_units: float = 0.0
    bonus_attacker_total_territories: float = 0.0
    bonus_defender_total_territories: float = 0.0
    bonus_attacker_unit_density: float = 0.0 
    bonus_defender_unit_density: float = 0.0

    bonus_passive_attacker_recruitment: float = 0.0
    bonus_passive_defender_recruitment: float = 0.0
    bonus_continent_capture_attacker: float = 0.0
    bonus_continent_capture_defender: float = 0.0
    bonus_recruitment_denied: float = 0.0
    bonus_per_card_gained: float = 0.0
    bonus_attacker_has_matching_card: float = 0.0
    bonus_turns_since_last_capture_territory: float = 0.0

    bonus_attacker_connected_total: float = 0.0
    bonus_attacker_connected_friendly: float = 0.0
    bonus_attacker_connected_enemy: float = 0.0
    bonus_attacker_connected_friendly_units: float = 0.0

    bonus_defender_connected_total: float = 0.0
    bonus_defender_connected_friendly: float = 0.0
    bonus_defender_connected_enemy: float = 0.0
    bonus_defender_connected_friendly_units: float = 0.0

    bonus_unique_players_connected_attacker: float = 0.0
    bonus_unique_players_connected_defender: float = 0.0
    bonus_captured_previously_this_turn: float = 0.0
    bonus_total_captured_this_turn: float = 0.0
    bonus_active_players: float = 0.0

    @property
    def average_fitness(self) -> float:
        if self.games_played:
            return self.fitness/self.games_played
        return 0
    
    @classmethod
    def create_from_crossover(cls, parent1: Self, parent2: Self) -> Self:
        new_chromosome = cls()
        for gene in new_chromosome.__dict__:
            if gene == "fitness" or gene == "games_played":
                continue
            alpha = random.random()
            parent1_gene = getattr(parent1, gene)
            parent2_gene = getattr(parent2, gene)
            crossed_gene = parent1_gene + alpha*(parent2_gene-parent1_gene)
            setattr(new_chromosome, gene, crossed_gene)
        return new_chromosome
        
    def mutate(self, mutation_chance=0.1, standard_deviation=1.0) -> None:
        for gene in self.__dict__: 
            if gene == "fitness" or gene == "games_played":
                continue
            elif mutation_chance > random.random():
                new_value = getattr(self, gene) + random.gauss(0, standard_deviation)
                if gene in ["recruitment_softmax_temp",
                            "attack_softmax_temp",
                            "priority_attack_multiplier", 
                            "priority_defense_multiplier"]:
                    new_value = max(new_value, 0)
                setattr(self, gene, new_value)

        
                      
        
        
            
        



                
