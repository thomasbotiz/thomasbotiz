from dataclasses import dataclass
from ....utils import Command, ExplicitEvent
from __future__ import annotations

class Territory():
    pass

class Game():
    pass

class FortifyCommand(Command):
    """
    The family of classes only allowed to execute during the Fortify phase.
    """ 
    pass

class FortifyTerritoryCommand(FortifyCommand):
    def __init__(self, territory_from: Territory, territory_to: Territory, count: int):
        """
        A command to transfer units from one territory to the other
        
        Attributes
        ----------
        territory_from : Territory
            The territory having units transferred from
        territory_to : Territory
            The territory being fortified
        units_transferred : int
            The number of units transferred from `territory_from` to `territory_to`
        """
        pass
        
    def _validate(self, game: Game) -> str:
        """
        Checks if it is legal to fortify
        the specified territory

        Parameters
        ----------
        game : Game
            The instance of game being executed on

        Returns
        -------
        str
            The accompanying error message(None assumes valid)
        
        Notes
        -----
        FortifyTerritoryCommand should validate if:

        territory_from is owned by the current turn player

            AND 

        territory_to is owned by the current turn player

            AND
        
        the number of units on `territory_from` is greater than
        `units_transferred` (the fortifying territory must be left
        with one or more units)

        The territories are directly connected and contiguous rules 
        are enabled

        OR the territories are indirectly connected 
        and adjacent rules are enabled
        """

    def execute(self, game: Game) -> FortifyTerritoryEvent:
        """
        Transfers units from one territory to the other 
        if the units and territories are valid

        Returns
        -------
        FortifyTerritoryEvent
            Data representing the changes made to `Game` by FortifyTerritoryCommand
        
        success: bool
            True if no error message else False
        error : str
            The accompanying error message from _validate()
        player : Player
            The player who issued the command 
        territory_from : Territory
            The territory having units transferred from
        territory_to : Territory
            The territory that is fortified
        territory_from_count : int
            The new number of units on the transferring territory
        territory_to_count : int
            The new number of units on the fortified territory
        units_transferred : int
            The number of units transferred
        """
    
@dataclass
class FortifyTerritoryEvent(ExplicitEvent):
    """
    Event emitted when a territory is fortified

    Attributes
    ----------
    success: bool
        True if no error message else False
    error : str
        The accompanying error message from _validate()
    player : Player
        The player who issued the command 
    territory_from : Territory
        The territory having units transferred from
    territory_to : Territory
        The territory that is fortified
    territory_from_count : int
        The new number of units on the transferring territory
    territory_to_count : int
        The new number of units on the fortified territory
    units_transferred : int
        The number of units transferred
    """
    pass