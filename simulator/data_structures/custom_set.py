# simulator/data_structures/custom_set.py
class CustomSet:
    """
    A class to represent a custom set for managing messages.

    Attributes:
        set (set): A set used to store unique messages.
    """

    def __init__(self):
        """
        Initializes the custom set.
        """
        self.set = set()

    def push(self, message_format):
        """
        Adds a message to the set.

        Args:
            message_format (dict): The message format to add.
        """
        self.set.add(tuple(message_format.items()))


    def remove(self, message_format):
            """
            Removes a message from the set.

            Args:
                message_format (dict): The message format to remove.
            """
            self.set.remove(message_format)

    def contains(self, message_format) -> bool:
        """
        Checks whether the set contains a message.

        Args:
            message_format (dict): The message format to check.

        Returns:
            bool: True if the set contains the message, False otherwise.
        """
        return message_format in self.set

    def empty(self) -> bool:
        """
        Checks whether the set is empty.

        Returns:
            bool: True if the set is empty, False otherwise.
        """
        return len(self.set) == 0

    def size(self) -> int:
        """
        Returns the size of the set.

        Returns:
            int: The number of elements in the set.
        """
        return len(self.set)

    def clear(self):
        """
        Clears the set.
        """
        self.set.clear()

    def get_all_messages(self):
        """
        Returns all messages in the set.

        Returns:
            list: A list of all messages in the set as dictionaries.
        """
        return [dict(msg) for msg in self.set]