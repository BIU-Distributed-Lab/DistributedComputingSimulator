import heapq
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

    def push(self, message_format):
        """
        Pushes a message onto the heap.

        Args:
            message_format (dict): The message format containing arrival time.
        """
        heapq.heappush(self.heap, (message_format['arrival_time'], self.counter, message_format))
        self.counter += 1

    def pop(self) -> dict:
        """
        Pops the message with the smallest arrival time from the heap.

        Returns:
            dict: The message with the smallest arrival time.
        """
        priority, priority2, message_format = heapq.heappop(self.heap)
        return message_format

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