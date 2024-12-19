# simulator/data_structures/custom_dict.py
class CustomDict:
    """
    A class to represent a custom dictionary for managing messages.

    Attributes:
        dict (dict): A dictionary used to store messages with their destination IDs as keys.
    """

    def __init__(self):
        """
        Initializes the custom dictionary.
        """
        self.dict = {}

    def push(self, message_format):
        """
        Adds a message to the dictionary.

        Args:
            message_format (dict): The message format to add.
        """
        dest_id = message_format['dest_id']
        round = message_format['arrival_time']
        key = (dest_id, round)

        if key not in self.dict:
            self.dict[key] = []
        self.dict[key].append(message_format)


    def remove(self, message_format):
        """
        Removes a message from the dictionary.

        Args:
            message_format (dict): The message format to remove.
        """
        dest_id = message_format['dest_id']
        if dest_id in self.dict:
            self.dict[dest_id].remove(message_format)
            if not self.dict[dest_id]:
                del self.dict[dest_id]

    def contains(self, message_format) -> bool:
        """
        Checks whether the dictionary contains a message.

        Args:
            message_format (dict): The message format to check.

        Returns:
            bool: True if the dictionary contains the message, False otherwise.
        """
        dest_id = message_format['dest_id']
        return dest_id in self.dict and message_format in self.dict[dest_id]

    def empty(self) -> bool:
        """
        Checks whether the dictionary is empty.

        Returns:
            bool: True if the dictionary is empty, False otherwise.
        """
        return not bool(self.dict)

    def size(self) -> int:
        """
        Returns the size of the dictionary.

        Returns:
            int: The number of elements in the dictionary.
        """
        return sum(len(messages) for messages in self.dict.values())

    def clear(self):
        """
        Clears the dictionary.
        """
        self.dict.clear()

    def get_messages_for_specific_dest(self, dest_id, current_round):
        """
        Returns all messages in the dictionary for a specific destination ID.
        if dest_id is not in the dictionary, return an empty list.

        Args:
            dest_id (int): The destination ID for which to retrieve messages.

        Returns:
            list: A list of messages for the specified destination ID.
        """
        key = (dest_id, current_round)
        return self.dict.get(key, [])

    def clear_key(self, dest_id):
        """
        Removes the key from the dictionary.

        Args:
            dest_id (int): The destination ID to remove.
        """
        if dest_id in self.dict:
            del self.dict[dest_id]

    def get_all_messages(self):
        """
        Returns all messages in the dictionary.

        Returns:
            list: A list of all messages in the dictionary.
        """
        return [msg for messages in self.dict.values() for msg in messages]
