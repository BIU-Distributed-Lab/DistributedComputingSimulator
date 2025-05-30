"""
Error module for handling node failures and collapse conditions in the distributed network simulation.

This module defines the configuration and conditions for node failures/collapses in the network.
"""
import random 
import string
import simulator.Constants as Constants
from utils.logger_config import logger


class NodeState:
    """
    Enumeration of possible node states.
    Only these three states are allowed in the system.
    """
    ACTIVE = "active"      # Node is functioning normally
    COLLAPSED = "collapsed"  # Node has failed/collapsed
    TERMINATED = "terminated"  # Node has completed its algorithm

    @staticmethod
    def is_valid_state(state):
        """
        Check if a state is one of the valid system states.
        
        Args:
            state (str): The state to check
            
        Returns:
            bool: True if the state is valid, False otherwise
        """
        return state in {NodeState.ACTIVE, NodeState.COLLAPSED, NodeState.TERMINATED}
    

class CollapseConfig:
    """
    Configuration class for node collapse conditions.

    Attributes:
        round_number (int): Round number at which the node should collapse (for sync mode)
        received_msg_count (int): Number of received messages after which node should collapse
        sent_msg_count (int): Number of sent messages after which node should collapse
        message_content (str): Specific message content that triggers collapse
        node_ids (list): List of node IDs that should collapse
    """

    def __init__(self, 
                 round_number=None, 
                 received_msg_count=None, 
                 sent_msg_count=None,
                 message_content=None,
                 node_ids=None):
        """
        Initialize collapse configuration.

        Args:
            round_number (int, optional): Round number for collapse
            received_msg_count (int, optional): Message receive count for collapse
            sent_msg_count (int, optional): Message send count for collapse
            message_content (str, optional): Message content that triggers collapse
            node_ids (list, optional): List of node IDs to collapse
        """
        self.round_number = round_number
        self.received_msg_count = received_msg_count
        self.sent_msg_count = sent_msg_count
        self.message_content = message_content
        self.node_ids = node_ids if node_ids else []

    def should_collapse(self, computer, current_round=None, message=None):
        """
        Check if a computer should collapse based on the configuration.

        Args:
            computer: Computer object to check
            current_round (int, optional): Current round number (for sync mode)
            message (Message, optional): Current message being processed

        Returns:
            bool: True if the computer should collapse, False otherwise
        """
        # Check if computer ID is in the list of nodes to collapse
        if self.node_ids and computer.id in self.node_ids:
            return True

        # Check round number (for sync mode)
        if self.round_number is not None and current_round == self.round_number:
            return True

        # Check received message count
        if (self.received_msg_count is not None and 
            hasattr(computer, 'received_msg_count') and 
            computer.received_msg_count >= self.received_msg_count):
            return True

        # Check sent message count
        if (self.sent_msg_count is not None and 
            hasattr(computer, 'sent_msg_count') and 
            computer.sent_msg_count >= self.sent_msg_count):
            return True

        # Check message content
        if (self.message_content is not None and 
            message is not None and 
            str(message.content) == self.message_content):
            return True

        return False
    


# function to get corruption info and the message content and do
def corrupt_message(message_content, corruption_info):
    if corruption_info is None:
        return message_content
    
    if corruption_info.get(Constants.RESERVED_PROBABILITY_OF_LOSS) is not None:
        # get random number between 0 and 1
        random_number = random.random()
        if random_number < corruption_info.get(Constants.RESERVED_PROBABILITY_OF_LOSS):
            logger.debug(f"message lost: {message_content}")
            logger.info(f"message lost: {message_content}")
            return None
        
        
    if corruption_info.get(Constants.RESERVED_PROBABILITY_OF_CORRUPTION) is not None:    
        random_number = random.random()
        if random_number < corruption_info.get(Constants.RESERVED_PROBABILITY_OF_CORRUPTION):
            # balagan
            return corrupt_message_content(message_content, corruption_info.get("corruption"))

        
        
    return message_content


def corrupt_message_content(message_content, corruption_info):
    if not isinstance(message_content, dict) or not isinstance(corruption_info, dict):
        return message_content
        
    # Create a copy of the message content to modify
    corrupted_content = message_content.copy()
    
    # Process each field in the corruption info
    for field, corruption_value in corruption_info.items():
        if field not in corrupted_content:
            continue
            
        if isinstance(corruption_value, str) and corruption_value == "_RANDOM":
            # Handle random corruption
            original_value = corrupted_content[field]
            if isinstance(original_value, (int, float)):
                # For numbers, add random offset
                # generate random bit between 0 to the size of the number and flip it
                bit_to_flip = random.randint(0, len(str(original_value)))
                # flip the bit
                corrupted_content[field] = original_value ^ (1 << bit_to_flip)


            elif isinstance(original_value, str):
                # For strings, either reverse it or add corruption marker
                if not original_value:
                    return original_value
                index = random.randint(0, len(original_value) - 1)
                char = random.choice(string.ascii_letters + string.digits)
                return original_value[:index] + char + original_value[index+1:]
            

            elif isinstance(original_value, bool):
                # For booleans, flip the value
                corrupted_content[field] = not original_value

            elif isinstance(original_value, list):
                # For lists, shuffle the elements
                corrupted_list = original_value.copy()
                random.shuffle(corrupted_list)
                corrupted_content[field] = corrupted_list

        else:
            # Direct value replacement
            corrupted_content[field] = corruption_value

    # print the original and the corrupted content
    logger.debug(f"original content: {message_content}\n corrupted content: {corrupted_content}")

            
    return corrupted_content




            

