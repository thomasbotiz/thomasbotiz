from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from dataclasses import dataclass

from ...utils.templates import Command, ExplicitEvent

if TYPE_CHECKING:
    from ...main.game import Game

class State(ABC):
    def __init__(self, game: Game):
        """
        Abstract class to represent all Game states.

        Attributes
        ----------
        game : Game
            The game instance controlling State
        whitelisted_commands : set[Command]
            A list of all accepted commands 

        Notes
        -----
        Game is a finite state machine. State follows
        State pattern and Chain of Responsibility Pattern. 
        State verifies Game is in the correct state 
        to execute phase-specific commands. 

        Has a whitelist of expected types of Commands to receive from Command.

        Responsible for emitting Events to objects external to 
        Game.
        """
        self.game = game
        self.whitelisted_commands: set[type[Command]]

    def execute(self, command: Command) -> None:
        """
        Method to validate and execute Commands

        Attributes:
        command : Command
            The command being executed
        Notes
        -----
        Returns None, mutates Game as a side effect.
        """
        error = self._validate(command)

        if not error:
            event = command.execute(self.game)
            self._on_execute(event)
        else:   
            self.game.event_bus.emit(InvalidCommandEvent(error))

    def _validate(self, command: Command) -> str:
        """
        Method to check if Command is legal within 
        the game rules by checking against whitelist
        and against internal data. 

        Parameters
        ----------
        game : Game
            The Game instance being executed on
        command : Command
            The request attempting to execute

        Returns
        ------- 
        str
            Any error messages from the operation 

        Notes
        -----
        Should not polymorph depending on the state, this should
        be handled by dynamic_validation.
        """
        error = ""
        if type(command) not in self.whitelisted_commands:
            error += "It is not legal to call that command at this time!"
        
        else:
            error += self._dynamic_validate(command)

        return error

    @abstractmethod
    def _save_data(self) -> dict:
        """
        Method to represent this State's inner
        inside a dictionary
        
        Returns
        -------
        dict
            The representation of the current State
            as a dictionary.
            
        Notes
        -----
        Only dynamic data that can change after the State
        will be considered. e.g. whitelisted commands are static,
        whereas territory_has_been_captured_this_turn is dynamic, so
        the latter variable gets saved.
        """
    
    @abstractmethod
    def _load_data(self, state_data: dict) -> None:
        """
        Method to load the dynamic data
        from a dictionary into a Game
        
        Parameters
        ----------
        state_data : dict
            A dictionary representing all
            the dynamic data of a state

        Notes
        -----
        Directly edits its own attributes. 
        """

    @abstractmethod
    def _dynamic_validate(self, command: Command) -> str:
        """
        Method to check if the Command is legal 
        within the context of the game state.
        
        Parameters
        ----------
        command : Command
            The command being checked dynamically against the game state

        Returns
        ------
        str 
            Any error messages from the operation 

        Notes
        -----
        This is the method which should be polymorphed between
        states.
        """

    @abstractmethod
    def on_enter(self) -> None:
        """
        Method called on creation. Checks state specific
        logic before any commands are executed.
        """
    
    @abstractmethod
    def _exit(self) -> None:
        """
        Method called to transfer to the next game state. 
        Performs end of phase actions and signals to game
        """

    @abstractmethod
    def _on_execute(self, result: ExplicitEvent) -> None:
        """
        Method to manage the cascade of methods and to broadcast Events

        Notes
        -----
        Should be called after Command is executed. Parses
        CommandResult from execute() and checks if Game
        needs to be edited more than by the atomic level by 
        Command. Also emits any Events as a side effect.
        """

@dataclass
class InvalidCommandEvent(ExplicitEvent):
    """
    An event emitted when a command was called
    in the incorrect phase

    Attributes
    ----------
    error : str
        The accompanying error message
    """
    error: str
