from abc import ABC, abstractmethod
from __future__ import annotations
from event import ExplicitEvent

class Game:
    pass

class Command(ABC):
    def __init__(self):
        """
        The set of commands that can be called in any phase

        Notes
        -----
        Any command inherited directly from Command signifies a 
        Metacommand, that is relevant to the game itself rather 
        than the state

        Commands control their own logic for validation, error 
        handling and execution.

        Commands are objects representing requests a player
        can make to the Game object. To specify that a Command
        can only be made in a specific State, refer to Command's
        subclasses. 

        Returns data stating what changes were made to `Game`. 
        Could be no data or all possible data.

        A base command means it will pass any check, for a 
        phase-specific commands use subclasses
        """
        pass
    
    @abstractmethod
    def execute(self, game: Game) -> ExplicitEvent:
        """
        Method that mutates `Game` through its protected interface
        
        Parameters
        ----------
        game : Game
            The game instance `Command` is executed to

        Returns
        -------
        CommandResult
            Data describing what changed in `Game`.

        Notes
        -----
        The rule must be validated using _validate() before executing, 
        the return of None from _validate() assumes that no failure in 
        operation.
        """   
        pass

    @abstractmethod
    def _validate(self, game: Game) -> str:
        """
        Method to check if `Command` is legal within 
        the game rules by accessing `State`'s protected
        interface

        Parameters
        ----------
        game : Game
            The game instance `Command` is executed onto

        Returns : str
            The accompanying error message if failed(None assumes no error)
        
        Notes
        -----
        Should not immediately return if an error is found. All errors should
        be found in one call.
        """
        pass