from __future__ import annotations
from typing import TYPE_CHECKING, Self, Optional
import pathlib
import json

from ...main.config import *
from ...utils.stack import Stack
from ...main.rules import GameRules, MapRules

if TYPE_CHECKING:
    from ..player.player import Player

class Board:
    def __init__(self, rules: GameRules, continents: list[Continent], continent_lookup: dict[Continent], territory_lookup: dict[Territory]):
        """
        A container for the continents of the game.
        
        Parameters
        ----------
        continents : list[Continent]
            The list of continents in the game
        _rules : GameRules
            The rules the board is operating under

        Attributes
        ----------
        continents : list[Continent]
            All continents in the game. 

        Notes
        -----
        Holds responsibility for game-wide territory
        related methods, such as calculating the
        troop bonus at the start of the turn, whether
        two territories are adjacent etc. 

        Note that it should create itself from startup
        using the data from antiquity_map.py, 
        traditional_map.py if necessary. 
        """
        self.rules = rules
        self.continents = continents
        self.territory_lookup = territory_lookup if territory_lookup else {}
        self.continent_lookup = continent_lookup if continent_lookup else {}

    @classmethod
    def create(cls, rules: GameRules) -> Self:
        """
        Returns an initialised board
        with the board data of the antiquity map.

        Notes
        -----
        After importing all the files, each territory only has a
        reference to a string instead of an object, so we need to
        pass through twice to replace string references with object
        references.
        """
        continents = []
        continent_lookup = {}
        territory_lookup = {}
         
        directory = pathlib.Path(__file__).parent
        if rules.MAP == MapRules.TRADITIONAL:
            file_location = directory / "traditional.json"

        elif rules.MAP == MapRules.ANTIQUITY:
            file_location = directory / "antiquity.json"

        try:
            with open(file_location, "r") as json_data:
                board_data = json.load(json_data)

            imported_continents = board_data["board"]["continents"]
            imported_territories = board_data["board"]["territories"]

            for continent_data in imported_continents:
                continent = Continent(**continent_data)
                continent_lookup[continent.id] = continent
                continents.append(continent)
            
            for territory_data in imported_territories:
                territory = Territory(**territory_data)
                territory_lookup[territory.id] = territory

            #Revisit continents and territories to replace references
            #with real objects

            for continent in continent_lookup.values():
                territories = [territory_lookup[territory_id] for territory_id in continent.territories]
                continent.territories = territories
            
            for territory in territory_lookup.values():
                connected_territories = [territory_lookup[territory_id] for territory_id in territory.connected_territories]
                territory.connected_territories = connected_territories

            board = cls(rules=rules,
                        continents = continents,
                        territory_lookup = territory_lookup,
                        continent_lookup = continent_lookup)
            
            return board
        
        except Exception as e:
            print(e)
            return None

    @property
    def territories(self) -> list[Territory]:
        """
        Get a list of every territory in the game
        
        Returns
        -------
        list[Territory]
            A list of all territories on the board
        """
        territories = []
        for continent in self.continents:
            for territory in continent.territories:
                territories.append(territory)
        return territories

    @property
    def all_territories_claimed(self) -> bool:
        """
        Checks if all territories are owned by a player
        
        Returns
        -------
        bool
            True if no territories with no owner else False
        """
        for continent in self.continents:
            for territory in continent.territories:
                if not territory.owner:
                    return False
        return True
    
    @property
    def unclaimed_territories(self) -> list[Territory]:
        """
        Returns a list of all unclaimed territories
        """
        unclaimed_territories = []
        for continent in self.continents:
            for territory in continent.territories:
                if not territory.owner:
                    unclaimed_territories.append(territory)
        return unclaimed_territories
    
    def _save_data(self) -> dict:
        board_data = {}
        board_data["continents"] = [continent._save_data() for continent in self.continents]
        return board_data

    def _load_data(self, board_data: dict, continent_lookup: dict, territory_lookup: dict, player_lookup: dict) -> None:
        self.territory_lookup = territory_lookup
        self.continent_lookup = continent_lookup
        for continent_data in board_data["continents"]:
            continent = self.continent_lookup[continent_data["id"]]
            continent._load_data(continent_data, territory_lookup, player_lookup)

    def get_continent_from_name(self, id: str) -> Continent:
        """
        Lookup any continent with the specified name

        Parameters
        ----------
        name : ContinentName
            The name of the continent being looked up
        
        Returns
        -------

        Territory
            The continent object associated with the name
        """
        try:
            return self.continent_lookup[id]
        except:
            return None
    
    def get_territory_from_id(self, id: str) -> Territory:
        """
        Lookup any continent with the specified name

        Parameters
        ----------
        name : ContinentName
            The name of the continent being looked up
        
        Returns
        -------

        Territory
            The continent object associated with the name
        """
        try:
            return self.territory_lookup[id]
        except:
            return None

    def get_friendly_territories(self, player: Player) -> list[Territory]:
        """
        Return all territories owned by a player
        
        Parameters
        ----------
        player : Player
            The player whose friendly territories are being checked
        
        Returns
        -------
        list[Territory]
            The list of all friendly territories on the board.

        Notes
        -----
        Iterate through every territory in every continent. Add to list if
        owned by the player.
        """
        return [territory for continent in self.continents for territory in continent.territories if territory.owner == player]

    def get_continent_of_territory(self, territory: Territory) -> Continent:
        for continent in self.continents:
            if territory in continent.territories:
                return continent
                
    def get_captured_continents(self, player: Player) -> list[Continent]:
        """
        Return all continents owned by a player
        
        Parameters
        ----------
        player : Player
            The player whose continents are being checked
        
        Returns
        -------
        list[Continent]
            The list of all friendly continents on the board.

        Notes
        -----
        Iterate through every territory in every continent. Add to list if
        all territories are owned by the player.
        """
        owned_continents = []
        for continent in self.continents:
            if continent.owner == player:
                owned_continents.append(continent)
        return owned_continents

    def get_attackable_territories(self, player: Player) -> list[Territory]:
        """
        Return all attackable players that a player can access.

        Parameters
        ----------
        player : Player
            The player whose attackable territories are being checked
        
        Returns
        -------
        list[Territory]
            The list of all attackable territories on the board.

        Notes
        -----
        Create a set. Use get_connected_attackable_territories
        on all territories and add any missing territories to 
        the set. Return the list
        """
        attackable_territories = set()
        for territory in self.get_friendly_territories(player):
            for attackable_territory in territory.connected_attackable_territories:
                attackable_territories.add(attackable_territory)
        return list(attackable_territories)
        
    def get_passive_recruitment(self, player: Player) -> int:
        """
        Calculates how many units the player gets
        at the start of their turn.

        Parameters
        ----------
        player : Player
            The player whose recruitment is being calculated

        Returns
        -------
        int 
            The number of units the player will obtain at
            the start of their turn
        
        Notes
        -----
        For every fully owned continent of that player,
        add the continent bonus.

        Add the floor of the number of territories
        owned by the playe divided by three.
        """
        units = 0
        for continent in self.get_captured_continents(player):
            units += continent.bonus
        
        captured_territory_count = len(self.get_friendly_territories(player))
        units += (captured_territory_count // 3)
        return max(units, RecruitmentConfig.MIN_UNITS_RECRUITED)
    
    def has_adjacency(self, territory_from: Territory, territory_to: Territory) -> bool:
        """
        Returns True if two territories are indirectly connected
        
        Parameters
        ----------
        territory_from : Territory
            The first territory
        territory_to : Territory
            The second territory

        Returns
        -------
        bool
            True if a path can be made else False

        Notes
        -----
        Should use depth first search using a stack. 

        Create a list of visited territories and start from territory_from. 
        For territories in connected_friendly_territories, add an unvisited 
        territory to the top of the stack and iterate until the top of the stackdf
        is territory_to, remove from stack if no unvisited territories, if the stack
        is empty return false.
        """
        visited_territories = set()
        visited_territories.add(territory_from)

        stack = Stack()
        stack.push(territory_from)
        
        while not stack.is_empty:
            current_territory = stack.pop()

            if current_territory == territory_to:
                return True
            
            for territory in current_territory.connected_territories:
                if territory not in visited_territories and territory.owner == current_territory.owner:
                    stack.push(territory)
                    visited_territories.add(territory)
        return False

class Continent:
    def __init__(self, 
                id: str,
                name: str, 
                colour : str,
                bonus: int = 0,
                territories: list[Territory] = None
                ):
        """
        A collection of territories. 

        Parameters
        ----------
        name : ContinentName
            The display name of the territory 
        colour : ContinentColour
            The display name of the territory
        bonus : int
            The number of units awarded at the start of
            the turn for controlling all territories
        territories : list[Territory]
            The territories which compose a continent
        """
        self.id = id
        self.name = name
        self.colour = colour
        self.bonus = bonus
        self.territories = territories if territories else []
        

    @property
    def owner(self) -> Player|None:
        """
        Returns the player that owns every territory in the continent else None
        """
        first_player = self.territories[0].owner

        for territory in self.territories[1:]:
            if territory.owner != first_player:
                return None
        return first_player
    
    def _save_data(self) -> dict:
        continent_data = {}
        for attribute, value in self.__dict__.items():
            if attribute == "territories":
                continent_data["territories"] = [territory._save_data() for territory in self.territories]
            elif attribute in ["id", "name", "colour", "bonus"]:
                continent_data[attribute] = value
        return continent_data
    
    def _load_data(self, continent_data: dict, territory_lookup: dict, player_lookup: dict) -> None:
        for attribute, value in continent_data.items():
            if attribute == "territories":
                self.territories = [territory_lookup[territory_data["id"]] for territory_data in continent_data["territories"]]
                for territory in self.territories:
                    for territory_data in continent_data["territories"]:
                        if territory.id == territory_data["id"]:
                            territory._load_data(territory_data, player_lookup)
            
            elif attribute in ["name", "colour", "bonus"]:
                setattr(self, attribute, value)

class Territory:
    def __init__(self, 
                id: str,
                name: str, 
                owner: Player = None, 
                units: int = 0,
                connected_territories: Optional[list[Territory]] = None, 
                turn_last_captured: int = 0 
                ):
        """
        An atomic territory that can be owned by a player
         
        Parameters
        ----------
        name : TerritoryName
            The name of the territory
        owner : Player
            The player which controls the territory
        units : int
            The number of units deployed on the territory
        connected_territories : list[Territory]
            The contiguous territories
        turn_last_captured : int
            The turn number the territory was last captured
        """
        self.id = id
        self.name = name
        self.owner = owner
        self.units = units
        self.connected_territories = connected_territories
        self.turn_last_captured = turn_last_captured

    @property 
    def connected_friendly_territories(self) -> list[Territory]:
        """
        Returns a list of territories owned by the friendly player
        """
        return [territory for territory in self.connected_territories if territory.owner == self.owner]
    
    @property 
    def connected_enemy_territories(self) -> list[Territory]:
        """
        Returns a list of connected territories owned by any enemy player
        """
        return [territory for territory in self.connected_territories if territory.owner != self.owner]

    @property
    def connected_attackable_territories(self) -> list[Territory]:
        """
        Returns a list of connected territories owned by any enemy
        player AND has at least 2 units """
        return [territory for territory in self.connected_territories if territory.owner != self.owner and self.units >= 2]

    def _save_data(self) -> dict:
        territory_data = {}
        for attribute, value in self.__dict__.items():
            if attribute == "owner":
                territory_data["owner_id"] = self.owner.id if self.owner else None#During the Placement Phase, a territory can have no owner.
            elif attribute in ["id", "name", "units", "turn_last_captured"]:
                territory_data[attribute] = value
        return territory_data
    
    def _load_data(self, territory_data: dict, player_lookup: dict) -> None:
        for attribute, value in territory_data.items():
            if attribute == "owner_id":
                self.owner = player_lookup[territory_data["owner_id"]] if territory_data["owner_id"] else None
            elif attribute in ["id", "name", "units", "turn_last_captured"]:
                setattr(self, attribute, value)
