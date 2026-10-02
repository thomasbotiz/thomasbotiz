from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .templates import Event 

class EventBus:
    def __init__(self):
        """
        Manages the flow of data from intenal to external components.

        Attributes
        ----------
        subscribers : dict
            The dictionary of subscribers and their events
        """
        self.subscribers = {}
    
    def subscribe(self, event: type, subscriber: callable) -> None:
        """
        Maps a subscriber to an event occurring. 

        Parameters
        ----------
        subscriber : callable
            Any method that executes when the event is passed
        event : Event
            A significant occurence in Game that external
            components need to know about.
        """
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(subscriber)

    def emit(self, event: Event) -> None:
        """
        Call the associate method for all listeners of a given event

        Parameters
        ----------
        event : Event
            The event that occured
        """
        event_type = type(event)
        if event_type in self.subscribers:
            for method in self.subscribers[event_type]:
                method(event)

