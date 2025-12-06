from typing import Any

class Stack:
    def __init__(self,
                body: list[Any]
                ):
        """
        A LIFO data structure useful for decks, search algorithms 
        and replay systems

        Attributes
        ----------
        body : list[Any]
            The data of the stack
        """
        pass

    @property
    def is_empty(self):
        """
        Returns true if no body else false
        """
    
    def push(self, element: Any):
        """
        Add an element to the top of the stack

        Parameters
        ----------
        element : Any
            The element being appended
        """
    
    def pop(self):
        """
        Return and remove the top item
        from the stack
        """
    
    def peek(self):
        """
        Return the top element 
        from the stack
        """