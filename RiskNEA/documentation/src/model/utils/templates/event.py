from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Event(ABC):
    """
    Abstract class for containers with data
    relevant to external objects.
    """

@dataclass
class ExplicitEvent(Event):
    """
    An event called as a direct result of a player input
    """

@dataclass
class ImplicitEvent(Event):
    """
    An event called indirectly due to a significant change
    in State
    """

