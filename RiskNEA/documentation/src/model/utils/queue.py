from typing import Any

class Queue:
    def __init__(self,
                body: list[Any]
                ):
        """
        A FIFO data structure useful for event buses and
        turn order

        Attributes
        ----------
        body : list[Any]
            The data of the queue
        """
        pass
    
    @property
    def is_empty(self):
        """
        Returns true if no body else false
        """

    def cycle(self):
        """
        Move the top element
        to the back of the queue
        """
  
    def enqueue(self, element: Any):
        """
        Add an element to the back of the queue

        Parameters
        ----------
        element : Any
            The element being appended
        """
    
    def dequeue(self):
        """
        Return and remove the top item
        from the stack
        """
    
    def peek(self):
        """
        Return the top element 
        from the stack
        """