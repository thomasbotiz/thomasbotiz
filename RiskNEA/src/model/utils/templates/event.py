from dataclasses import dataclass
from abc import ABC

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

    Attributes
    ----------
    error : str
        The accompanying error message

    Notes
    -----
    Generally, explicit events transfer low level data,
    such as objects. This is unlike an implicit event,
    which transfer higher level data such as strings,
    and integers (though this is not a rule, more a general
    philosophy).
    """
    error: str

@dataclass
class ImplicitEvent(Event):
    """
    An event called indirectly due to a significant change
    in State

    Notes
    -----
    Generally, implicit events transfer high level data,
    such as integers and strings. This is unlike an explicit 
    event, which transfer lower level data such as objects,
    (though this is not a rule, more a general
    philosophy).
    """
