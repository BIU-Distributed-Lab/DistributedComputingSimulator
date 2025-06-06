import heapq
from simulator.message import Message

class CustomMinHeap:
    """
    A class to represent a custom min-heap for managing messages.

    Attributes:
        heap (list): A list used to represent the heap.
        counter (int): A counter used to ensure unique priorities in the heap.
    """

    def __init__(self):
        """
        Initializes the custom min-heap.
        """
        self.heap = []
        self.counter = 0  # unique sequence count
        self.total_messages_sent = 0
        self.total_messages_received = 0

    def push(self, message: Message):
        """
        Pushes a message onto the heap.

        Args:
            message (Message): The message to add.
        """
        heapq.heappush(self.heap, (message.arrival_time, self.counter, message))
        self.counter += 1
        self.total_messages_sent += 1

    def pop(self) -> Message:
        """
        Pops the message with the smallest arrival time from the heap.

        Returns:
            Message: The message with the smallest arrival time.
        """
        priority, priority2, message = heapq.heappop(self.heap)
        self.total_messages_received += 1
        return message

    def empty(self) -> bool:
        """
        Checks whether the heap is empty.

        Returns:
            bool: True if the heap is empty, False otherwise.
        """
        return len(self.heap) == 0

    def size(self) -> int:
        """
        Returns the size of the heap.

        Returns:
            int: The number of elements in the heap.
        """
        return len(self.heap)