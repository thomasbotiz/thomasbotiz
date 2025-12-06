from __future__ import annotations
from enum import Enum
from ....utils.game_enums import *
from typing import Self

class Player:
    pass

class GameRules:
    pass

class Board:
    def __init__(self, continents: list[Continent], rules: GameRules):
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
        pass
    
    @classmethod
    def traditional(cls, rules: GameRules) -> Self:
        """
        Returns an initialised board
        with the board data of the antiquity map.

        Parameters
        ----------
        continents : list[Continent]
            The list of continents in the game
        _rules : GameRules
            The rules Board is operating under
        
        Returns
        -------
            An instance of Board with the traditional
            map continents

        Notes
        -----
        Data about the traditional map should be taken
        from the traditional file. 
        """

    @classmethod
    def antiquity(cls, rules: GameRules) -> Self:
        """
        Returns an initialised board
        with the board data of the antiquity map.

        Parameters
        ----------
        continents : list[Continent]
            The list of continents in the game
        _rules : GameRules
            The rules Board is operating under
        
        Returns
        -------
            An instance of Board with the antiquity
            map continents

        Notes
        -----
        Data about the antiquity map should be taken
        from the antiquity file. 
        """

    @property
    def get_territories(self) -> list[Territory]:
        """
        Get a list of every territory in the game
        
        Returns
        -------
        list[Territory]
            A list of all territories on the board
        """

    def auto_resolve():
        """
        Method that automates the rest of the placement phase 

        Notes
        -----
        If there are unclaimed territories, assign each player
        a random unselected territory in turn order.

        If all territories are claimed, assign each player's 
        remaining unit to a random territory separately until
        their turn is over and in turn order.
        """

    def transfer_units(territory_from: Territory, territory_to: Territory, count: int) -> None:
        """
        Transfer units from one territory to the next

        Parameters
        ----------
        territory_from : Territory
            The first territory
        territory_to : Territory
            The second territory
        count : int
            The number of units transferred

        Notes
        -----
        Subtract units from territory_from and add to territory_to
        To call this in the first place. count must already be of a 
        valid number. 
        """ 

    def get_continent_from_name(self, name: ContinentName) -> Continent:
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

    def get_territory_from_name(self, name: TerritoryName):
        """
        Lookup any continent with the specified name

        Parameters
        ----------
        name : TerritoryName
            The name of the continent being looked up
        
        Returns
        -------
        territory
            The territory object associated with the name
        """

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
    
    def get_captured_continents(self, player: Player) -> list[Territory]:
        """
        Return all continents owned by a player
        
        Parameters
        ----------
        player : Player
            The player whose continents are being checked
        
        Returns
        -------
        list[Territory]
            The list of all friendly continents on the board.

        Notes
        -----
        Iterate through every territory in every continent. Add to list if
        all territories are owned by the player.
        """

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
        Create a list. Use get_connected_attackable_territories
        on all territories and add any missing territories to 
        the list. Return the list
        """

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
    
    def is_adjacent(self, territory_from: Territory, territory_to: Territory) -> bool:
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
        territory to the top of the stack and iterate until the top of the stack
        is territory_to, remove from stack if no unvisited territories, if the stack
        is empty return false.
        """

class Continent:
    """
    A collection of territories. 
    """
    def __init__(self, 
                name: ContinentName, 
                _colour : ContinentColour,
                bonus: int = 0,
                territories: list[Territory] = []
                ):
        pass

    @property
    def owner(self) -> Player:
        """
        Returns the player that owns every territory in the continent else None
        """

class Territory:
    def __init__(self, 
                name: TerritoryName, 
                owner: Player = None, 
                units: int = 0,
                connected_territories: list[Territory] = [], 
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

    @property 
    def owner(self) -> Player:
        """
        Returns the owner of the territory
        """

    @property 
    def connected_friendly_territories(self) -> list[Territory]:
        """
        Returns a list of territories owned by the friendly player
        """
    
    @property 
    def connected_enemy_territories(self) -> list[Territory]:
        """
        Returns a list of connected territories owned by any enemy player
        """

    @property
    def connected_attackable_territories(self) -> list[Territory]:
        """
        Returns a list of connected territories owned by any enemy
        player AND has at least 2 units """
