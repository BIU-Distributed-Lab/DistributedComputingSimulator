"""
Message class for representing messages in the distributed network simulation.
"""

class Message:
    """
    A class representing a message in the distributed network simulation.
    
    Attributes:
        source_id (int): The ID of the source computer sending the message.
        dest_id (int): The ID of the destination computer receiving the message.
        arrival_time (float): The time at which the message will arrive.
        content (str): The content/payload of the message.
    """
    
    def __init__(self, source_id: int, dest_id: int, arrival_time: float, content: str):
        """
        Initialize a new Message instance.
        
        Args:
            source_id (int): The ID of the source computer.
            dest_id (int): The ID of the destination computer.
            arrival_time (float): The time at which the message will arrive.
            content (str): The content/payload of the message.
        """
        self.source_id = source_id
        self.dest_id = dest_id
        self.arrival_time = arrival_time
        self.content = content
    
    def to_dict(self) -> dict:
        """
        Convert the message to a dictionary format.
        
        Returns:
            dict: Dictionary representation of the message.
        """
        return {
            'source_id': self.source_id,
            'dest_id': self.dest_id,
            'arrival_time': self.arrival_time,
            'content': self.content
        }
    
    @classmethod
    def from_dict(cls, message_dict: dict) -> 'Message':
        """
        Create a Message instance from a dictionary.
        
        Args:
            message_dict (dict): Dictionary containing message data.
            
        Returns:
            Message: A new Message instance.
        """
        return cls(
            source_id=message_dict['source_id'],
            dest_id=message_dict['dest_id'],
            arrival_time=message_dict['arrival_time'],
            content=message_dict['content']
        )
    
    def __lt__(self, other: 'Message') -> bool:
        """
        Compare messages based on arrival time for priority queue ordering.
        
        Args:
            other (Message): Another message to compare with.
            
        Returns:
            bool: True if this message should arrive before the other message.
        """
        return self.arrival_time < other.arrival_time 