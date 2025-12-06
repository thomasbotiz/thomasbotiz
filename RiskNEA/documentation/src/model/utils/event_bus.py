from .templates.event import *

class EventBus:
    def __init__(self):
        """
        Manages the flow of data from intenal to external components.

        Attributes
        ----------
        subscribers : dict
            The dictionary of subscribers and their events
        """
    
    def subscribe(self, event: Event, subscriber: callable) -> None:
        """
        Maps a subscriber to an event occuring. 

        Parameters
        ----------
        subscriber : callable
            Any method that executes when the event is passed
        event : Event
            A significant occurance in Game that external
            components need to know about.
        """


    def emit(event: Event) -> None:
        """
        Call the function for all listeners of the event

        Parameters
        ----------
        event : Event
            The event that occured
        """
