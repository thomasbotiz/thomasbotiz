from abc import ABC, abstractmethod
from __future__ import annotations
from command import Command
from event import ExplicitEvent

class Game:
    pass

class State(ABC):
    """
    Abstract class to represent all `Game` states.

    Attributes
    ----------
    game : Game
        The game instance controlling `State`
    whitelisted_commands : set[Command]
        A list of all accepted commands 

    Notes
    -----
    `Game` is a finite state machine. `State` follows
    State pattern and Chain of Responsibility Pattern. 
    `State` verifies `Game` is in the correct state 
    to execute phase-specific commands. 

    Has a whitelist of expected types of Commands to receive from Command.

    Responsible for emitting `Event`s to objects external to 
    `Game`.
    
    """
    def __init__(self):
        """
        Constructor for State

        Attributes
        ----------
        whitelisted_commands : set[Command]
            The family of commands that aren't immediately filtered

        Notes
        -----
        State is also responsible for constructing 
        it's own ephemeral data. For example, 
        AttackState needs to know if the player has
        captured a territory before the end of their turn,
        so we would need an extra boolean attribute which
        exists only for State's lifecycle. 
        """
        self.game: Game
        self.whitelisted_commands: set[type[Command]]

    @abstractmethod
    def execute(self, command: Command) -> None:
        """
        Method to validate and execute Commands

        Attributes:
        command : Command
            The command being executed
        Notes
        -----
        Returns None, mutates `Game` as a side effect.
        """
        if self._validate(command):
            result = command.execute(self.game)
        self._on_execute(result)

    @abstractmethod
    def _on_execute(self, result: ExplicitEvent) -> None:
        """
        Method to manage the cascade of methods and to broadcast `Events`

        Notes
        -----
        Should be called after `Command` is executed. Parses
        `CommandResult` from `execute()` and checks if Game
        needs to be edited more than by the atomic level by 
        `Command`. Also emits any `Events` as a side effect.
        """
        pass

    @abstractmethod
    def _validate(self, command: Command) -> bool:
        """
        Method to check if `Command` is legal within 
        the game rules by checking against whitelist
        and against internal data. 

        Parameters
        ----------
        game : Game
            The `Game` instance being executed on
        command : Command
            The request attempting to execute

        Returns : bool
        """
        if type(command) in self.whitelisted_commands:
            return True
        
        else:
            return False
    