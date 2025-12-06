from typing import Any

class Queue:
    def __init__(self, body: list[Any] = None):
        """
        A FIFO data structure useful for event buses and
        turn order

        Attributes
        ----------
        body : list[Any]
            The data of the queue
        """
        self.body = body if body else []
        
    @property
    def is_empty(self) -> bool:
        """
        Checks if the queue is empty

        Returns
        -------
        bool
            true if no elements else false
        """
        return not(self.body)

    @property
    def head(self) -> Any:
        """
        Returns the top element of the queue 
        """
        return self.body[0]

    def cycle(self):
        """
        Move the top element
        to the back of the queue
        """
        self.enqueue(self.dequeue())
  
    def enqueue(self, element: Any) -> None:
        """
        Add an element to the back of the queue

        Parameters
        ----------
        element : Any
            The element being appended
        """
        self.body.append(element)
    
    def dequeue(self) -> Any:
        """
        Return and remove the first item
        from the queue
        """
        return self.body.pop(0)
