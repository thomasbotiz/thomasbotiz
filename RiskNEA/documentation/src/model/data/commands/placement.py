from dataclasses import dataclass
from ....utils import Command, ExplicitEvent
from __future__ import annotations

class Territory():
    pass

class Game():
    pass

class PlacementCommand(Command):
    """
    The family of classes only allowed to execute during the Placement phase.
    """ 
    pass


class PlaceUnitCommand(PlacementCommand):
    def __init__(self, game: Game, territory_placed_on: Territory):
        """
        A command to place a unit on a territory

        Attributes
        ----------
        territory_placed_on : Territory
            The territory being placed on
        count : int
            The number of units being placed
        """
        pass

    def execute(self, game: Game) -> PlaceUnitEvent:
        """
        Places units on the territory if the
        units and territory is valid 

        Returns
        -------
        PlacementCommandResult
            Data representing the changes made to `Game` by PlaceUnitCommand
        
        success: bool
            True if no error message else False
        error : str
            The accompanying error message from _validate()
        player : Player
            The player who issued the command 
        units_placed : int
            The number of units placed on the territory
        """

    pass

    def _validate(self, game: Game) -> str:
        """
        Checks if it is legal to place
        the units on the territory

        Returns
        -------
        str
            The accompanying error message(None assumes the command is valid)

        Notes
        -----
        PlaceUnitCommand should successfully
        add units to the territory if: 

        `count` is greater than zero and results in `units_left` being zero or greater 
        
        AND 

        If there are still unclaimed territories, 
        territory_placed_on must be unowned

        OR 

        If all territories are claimed, territory_placed_on
        must be owned by the currently active player in the turn 
        """



@dataclass
class PlaceUnitEvent(ExplicitEvent):
    """
    DTO that is a representation of change when a player calls PlaceUnitCommand

    Attributes
    ----------
    success : bool
        Whether the command successfully executed(None assumes False)
    error : str
        The error message that came with the failed command(None assumes no error message)
    player : Player
        The player who issued the placement command(None assumes currently active player)
    territory_placed_on : Territory
        The territory that a unit was placed on(None assumes no unit was placed)
    units_placed : int 
        The number of units placed(None assumes one)
    """
