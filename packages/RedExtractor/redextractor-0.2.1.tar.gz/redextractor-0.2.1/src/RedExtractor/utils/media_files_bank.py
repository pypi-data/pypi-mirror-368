from collections import deque

from core.media_object_class import MediaObject

class MediaFilesBank:
    """
    A Flexible & Reliable Doubly-linked-list 
    based high-performance FIFO (First-In-First-Out) data storage class.

    This class provides constant-time appending and popping operations using
    an underlying `collections.deque`, which is optimized for queue-like access.

    The storage behaves like a queue:
        - Data is added using `store()`
        - Data is retrieved in order using `retrieve()`

    Suitable for:
        - Task queues
        - Message/event buffers
        - Streamed data pipelines

    Attributes:
        _queue (deque): Internal double-ended queue for efficient FIFO operations.
    
    """
    def __init__(self):
        self._queue = deque()

    def store(self, data):
        """Store data in FIFO order."""
        self._queue.append(data)  # O(1)

    def retrieve(self):
        """Retrieve and remove the earliest stored data."""
        if self.is_empty():
            raise IndexError("Cannot retrieve from an empty storage.")
        return self._queue.popleft()  # O(1)

    def peek(self):
        """Return the first item without removing it."""
        if self.is_empty():
            print("Cannot peek into an empty storage.") 
            return
        return self._queue[0]  # O(1)

    def is_empty(self):
        """Check if the storage is empty."""
        return len(self._queue) == 0  # O(1)

    def size(self):
        """Return the number of stored elements."""
        return len(self._queue)  # O(1)
