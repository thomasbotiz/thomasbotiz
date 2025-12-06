from ...utils import Command, ExplicitEvent
from dataclasses import dataclass
from __future__ import annotations

class Game:
    pass

class Territory:
    pass

@dataclass
class FailedCommandEvent(ExplicitEvent):
    """
    An event emitted when a command was called
    in the incorrect phase

    Attributes
    ----------
    error : str
        The accompanying error message
    """

class SaveCommand(Command):
    def __init__(self, filename: str):
        """
        A command to save the game to /saves

        Parameters
        ----------
        filename : str
            The name of the file being saved.

        Attributes
        ----------
        filename : str
            The name of the file being saved.
        
        Notes
        -----
        Should overwrite the file if present
        """

    def _validate(self):
        """
        Checks if the command is valid to call or not

        Notes
        -----
        Normal Commands are handled by State, rather than
        Command. SaveCommand should validate in any State 
        at any time EXCEPT in the attack phase where the 
        game is expecting a transfer of units or a trade in
        of a set. 
        """
    
    def execute(self):
        """
        No logic for meta commands

        Notes
        -----
        State itself should act on meta-level commands. 
        """

@dataclass
class SaveEvent(ExplicitEvent):
    """
    Event emitted when a player saves the game

    Attributes
    -------
    success : bool
        True if the offensive was successfully changed
    error : str
        The accompanying error message from _validate()
    filename : str
        The name of the file that was just saved
    """

class LoadCommand(Command):
    def __init__(self, filename: str):
        """
        A command to load a game from /saves with filename

        Parameters
        ----------
        filename : str
            The name of the file being saved.

        Attributes
        ----------
        filename : str
            The name of the file being saved.
        
        Notes
        -----
        Should overwrite the file if present
        """

    def _validate(self):
        """
        Checks if the command is valid to call or not

        Notes
        -----
        Always valid to call. 
        """
    
    def execute(self):
        """
        No logic for meta commands

        Notes
        -----
        State itself should act on meta-level commands. 
        """

class LoadEvent(ExplicitEvent):
    """
    Event emitted when a player saves the game

    Attributes
    -------
    success : bool
        True if the offensive was successfully changed
    error : str
        The accompanying error message from _validate()
    filename : str
        The name of the file that was just saved
    """

class NextTurnCommand(Command):
    def __init__(self):
        """
        A command to load a game from /saves with filename
        """

    def _validate(self):
        """
        Checks if the command is valid to call or not

        Notes
        -----
        See each accompanying state for when the command
        is valid. 
        """
    
    def execute(self):
        """
        No logic for meta commands

        Notes
        -----
        State itself should act on meta-level commands. 
        """

class NextTurnEvent(ExplicitEvent):
    """
    Event emitted when a player saves the game

    Attributes
    -------
    success : bool
        True if the offensive was successfully changed
    error : str
        The accompanying error message from _validate()
    """