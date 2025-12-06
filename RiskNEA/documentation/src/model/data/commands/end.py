from dataclasses import dataclass
from ....utils import Command, ExplicitEvent
from __future__ import annotations

class Territory():
    pass

class Game():
    pass

class EndCommand(Command):
    """
    The family of classes only allowed to execute during the End phase.
    """ 

class CyclePlayerCommand(EndCommand):
    def __init__(self):
        """
        A command to set the player whose statistics 
        are focused on to the main screen
        """
        pass

    def _validate(self, game: Game) -> str:
        """
        Checks if it is legal to cycle the player
        
        Parameters
        ----------
        game : Game 
            The instance of Game being executed on

        Returns
        -------
        str 
            The accompanying error message(None assumes valid)

        Notes
        -----
        It is always legal to call this command once it passes State's
        validation.
        """
    
    def execute(self, game: Game) -> None:
        """
        Set's current player to the next player in the queue

        Attributes
        ----------
        game : Game
            The instance of Game being executed on 
        
        Returns
        -------
        CyclePlayerEvent
            Data on what was changed in `Game`  
        """

@dataclass
class CyclePlayerEvent(ExplicitEvent):
    """
    An event emitted when a player is cycled
    
    Attributes
    ----------
    success : bool
        True if the offensive was successfully changed
    error : str
        The accompanying error message from _validate()
    stats : PlayerStats
        The stats of the new focused on player
    """