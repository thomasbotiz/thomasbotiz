from typing import Any

class Stack:
    def __init__(self, body: list[Any] = None):
        """
        A LIFO data structure useful for decks, search algorithms 
        and replay systems

        Parameters
        ----------
        body : list[Any]
            The data of the stack

        Attributes
        ----------
        body : list[Any]
            The data of the stack
        """
        self.body = body if body else []

    @property
    def is_empty(self):
        """
        Returns true if no body else false
        """
        return not(self.body)
    
    @property
    def head(self):
        """
        Return the top element 
        from the stack
        """
        return self.body[-1]

    def push(self, element: Any):
        """
        Add an element to the top of the stack

        Parameters
        ----------
        element : Any
            The element being appended
        """
        self.body.append(element)
    
    def pop(self):
        """
        Return and remove the top item
        from the stack
        """
        return self.body.pop()
    
