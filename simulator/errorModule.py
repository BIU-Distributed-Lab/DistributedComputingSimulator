"""
Error module for handling node failures and collapse conditions in the distributed network simulation.

This module defines the configuration and conditions for node failures/collapses in the network.
"""
import random
import string

import numpy as np

import simulator.Constants as Constants
from utils.logger_config import logger
from simulator.config import NodeState


class CollapseConfig:
    """
    Configuration class for node collapse conditions.

    Attributes:
        node_configs (dict): Dictionary mapping node IDs to their collapse configurations
        Each node configuration contains:
            - round_number (int): Round number at which the node should collapse
            - round_reoccurence (int): How often the collapse should reoccur
            - probability (float): Probability of collapse when conditions are met
            - received_msg_count (int): Number of messages to receive before collapse
            - sent_msg_count (int): Number of messages to send before collapse
    """

    def __init__(self, config_dict=None):
        """
        Initialize collapse configuration.

        Args:
            config_dict (dict): Configuration dictionary from algorithm file
            Format example:
            {
                "1": {"round": 2, "round_reoccurence": 1, "probability": 1},
                "2": {"round": 3, "received_msg_count": 5},
                "3": {"sent_msg_count": 3, "probability": 0.5}
            }
        """
        self.node_configs = {}
        self.overall_collapse_percent = 0.0
        self.estimated_rounds_number = 100
        self.collapsed_nodes = set()

        # object to update each collapse, for the log at the end of the program
        self.collapse_log = {}

        if config_dict is not None:
            self.overall_collapse_percent = config_dict.get("overall", 0.0)
            self.estimated_rounds_number = config_dict.get("rounds_number", 100)

            for node_id, node_config in config_dict.items():
                if node_id == "overall":
                    continue
                if node_id.isdigit():
                    node_id = int(node_id)
                    self.node_configs[node_id] = {
                        'round': node_config.get('round'),
                        'round_reoccurrence': node_config.get('round_reoccurrence', 1),
                        'probability': node_config.get('probability', 1.0),
                        'received_msg_count': node_config.get('received_msg_count'),
                        'sent_msg_count': node_config.get('sent_msg_count')
                    }

    def maybe_collapse_randomly(self, all_computers):
        """
        Randomly collapse a subset of active computers based on the overall percentage.

        Args:
            all_computers (dict): Dictionary of all Computer objects by ID
        """
        total_nodes = len(all_computers)
        if total_nodes == 0 or self.overall_collapse_percent <= 0:
            return

        # Filter only active and not-yet-collapsed nodes
        candidates = [
            c for c in all_computers.values()
            if hasattr(c, 'state') and c.state == NodeState.ACTIVE and c.id not in self.collapsed_nodes
        ]

        if not candidates:
            return

        target_collapse_count = int(total_nodes * self.overall_collapse_percent)
        remaining_to_collapse = target_collapse_count - len(self.collapsed_nodes)

        if remaining_to_collapse <= 0:
            return

        logger.debug(f"Total nodes: {total_nodes}, Target collapse count: {target_collapse_count}, "
                     f"Remaining to collapse: {remaining_to_collapse}")

        # Estimate how many to collapse this round (can use Poisson or a fixed small number)
        parameter = self.estimated_rounds_number
        dynamic_lambda = max(1, remaining_to_collapse / parameter)  # Ensure at least 1 node is selected
        logger.debug(f"Dynamic lambda for collapse: {dynamic_lambda}")
        num_to_collapse = min(len(candidates), np.random.poisson(dynamic_lambda), remaining_to_collapse)
        logger.debug(f"Number of nodes to collapse this round: {num_to_collapse}")

        # Randomly select and collapse
        if num_to_collapse > 0:
            selected = random.sample(candidates, num_to_collapse)
            for comp in selected:
                #comp.collapse()
                self.collapse_node(comp)
                self.collapsed_nodes.add(comp.id)
                logger.info(f"Node {comp.id} randomly collapsed (overall={self.overall_collapse_percent})")

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
        #logger.debug(f"checking collapse, computer: {computer.id}, current_round: {current_round}, curr received msg: {getattr(computer, 'received_msg_count', 0)}, ")
        # quick check if node active just make sure computer is not none and has state
        if computer is None:
            return

        if not hasattr(computer, 'state') or computer.state != NodeState.ACTIVE:
            logger.debug(f"computer {computer.id} is not active, skipping collapse check")
            return

        # Quick check if this node has a collapse configuration
        node_config = self.node_configs.get(computer.id)
        if not node_config:
            return

            # Apply probability check
        if random.random() > node_config['probability']:
            return

            # Check round number (for sync mode)
        if current_round is not None and node_config['round'] is not None:
            if node_config['round_reoccurrence']:
                # Check if we're at a round where collapse should occur
                if (current_round >= node_config['round'] and
                        (current_round - node_config['round']) % node_config['round_reoccurrence'] == 0):
                    self.collapse_node(computer)
                    return
            elif current_round == node_config['round']:
                self.collapse_node(computer)
                return

        # Check received message count
        if (node_config['received_msg_count'] is not None and
                hasattr(computer, 'received_msg_count') and
                computer.received_msg_count >= node_config['received_msg_count']):
            self.collapse_node(computer)
            return

        # Check sent message count
        if (node_config['sent_msg_count'] is not None and
                hasattr(computer, 'sent_msg_count') and
                computer.sent_msg_count >= node_config['sent_msg_count']):
            self.collapse_node(computer)
            return

        return

    def collapse_node(self, computer, round_number=None):
        """
        Collapse a specific computer node.

        Args:
            computer: Computer object to collapse
        """
        if computer is None or not hasattr(computer, 'state'):
            return

        # Collapse the node and update its state
        computer.collapse()
        self.collapsed_nodes.add(computer.id)

        # Log the collapse event, message received, and message sent, and if round is not None, include it
        self.collapse_log[computer.id] = {
            'round': round_number,
            'received_msg_count': getattr(computer, 'received_msg_count', 0),
            'sent_msg_count': getattr(computer, 'sent_msg_count', 0)
        }


    def get_node_config(self, node_id):
        """
        Get the collapse configuration for a specific node.

        Args:
            node_id (int): The ID of the node

        Returns:
            dict: The node's collapse configuration or None if not found
        """
        return self.node_configs.get(node_id)

    def __str__(self):
        """String representation of the collapse configuration."""
        return f"CollapseConfig(nodes={list(self.node_configs.keys())})"

    # function to log at the end of the program the number of collapsed nodes and what time they collapsed
    def log_collapse_statistics(self):
        """
        Log the collapsed nodes for debugging.
        """
        # iterate collapse log and print
        logger.info("=== ERROR MODULE COLLAPSE STATISTICS ===")
        if self.collapse_log:
            logger.info("Collapse Config Class Log:")
            for node_id, collapse_info in self.collapse_log.items():
                round_info = f"at round {collapse_info['round']}" if collapse_info['round'] is not None else ""
                logger.info(f"Node {node_id} collapsed {round_info}, "
                            f"message received: {collapse_info['received_msg_count']} and "
                            f"msg sent: {collapse_info['sent_msg_count']}")

        else:
            logger.info("No nodes collapsed during the simulation.")

        logger.info("=== END OF ERROR MODULE COLLAPSE STATISTICS ===")


class ReorderConfig:
    """
    Configuration class for message reordering conditions.

    Attributes:
        unordered_edges (set): Set of unordered edges represented as tuples (min(source, dest), max(source, dest)).
    """

    def __init__(self, config_dict=None):
        """
        Initialize reorder configuration.

        Args:
            config_dict (dict): Configuration dictionary from algorithm file
        """
        self.unordered_edges = set()
        self.roll_the_dice(config_dict)

    def roll_the_dice(self, config_dict):
        """
        Roll the dice to determine which edges should be unordered.

        Args:
            config_dict (dict): Configuration dictionary with edges and their probabilities
        """
        if config_dict is None:
            return

        for edge, probability in config_dict.items():
            # Normalize edge representation
            source, dest = map(int, edge.strip("()").split(","))
            normalized_edge = (min(source, dest), max(source, dest))
            if random.random() < probability:
                self.unordered_edges.add(normalized_edge)

    def is_edge_ordered(self, source, dest):
        """
        Check if the edge is ordered.

        Args:
            source (int): Source node ID
            dest (int): Destination node ID

        Returns:
            bool: True if the edge is ordered, False otherwise
        """
        # Normalize edge representation
        normalized_edge = (min(source, dest), max(source, dest))
        return normalized_edge not in self.unordered_edges

    def log_reorder_statistics(self):
        """
        Log the unordered edges for debugging.
        """
        logger.info("=== ERROR MODULE REORDER STATISTICS ===")
        if self.unordered_edges:
            logger.info(f"Unordered edges: {self.unordered_edges}")
        else:
            logger.info("No unordered edges configured.")
        logger.info("=== END OF ERROR MODULE REORDER STATISTICS ===")

class MessageCorruptionStats:
    """
    Statistics tracking class for message corruption operations.
    
    Tracks various metrics about message corruption including:
    - Total messages processed
    - Messages lost
    - Messages corrupted by type
    - Field-specific corruption statistics
    """
    
    def __init__(self):
        """Initialize corruption statistics tracking."""
        self.total_messages_processed = 0
        self.messages_lost = 0
        self.messages_corrupted = 0
        self.corruption_by_type = {
            'int': 0,
            'float': 0,
            'str': 0,
            'bool': 0,
            'list': 0,
            'direct_replacement': 0
        }
        self.corruption_by_field = {}
        self.loss_attempts = 0
        self.corruption_attempts = 0
        self.corruption_log = []
        
    def record_message_processed(self):
        """Record that a message was processed."""
        self.total_messages_processed += 1
        
    def record_message_lost(self, message_content, probability):
        """Record that a message was lost."""
        self.messages_lost += 1
        self.loss_attempts += 1
        self.corruption_log.append({
            'type': 'loss',
            'message': str(message_content),
            'probability': probability,
            'timestamp': self.total_messages_processed
        })
        
    def record_loss_attempt(self):
        """Record that a message loss was attempted but didn't occur."""
        self.loss_attempts += 1
        
    def record_message_corrupted(self, original_content, corrupted_content, corruption_info):
        """Record that a message was corrupted."""
        self.messages_corrupted += 1
        self.corruption_attempts += 1
        self.corruption_log.append({
            'type': 'corruption',
            'original': str(original_content),
            'corrupted': str(corrupted_content),
            'corruption_info': str(corruption_info),
            'timestamp': self.total_messages_processed
        })
        
    def record_corruption_attempt(self):
        """Record that a message corruption was attempted but didn't occur."""
        self.corruption_attempts += 1
        
    def record_field_corruption(self, field_name, corruption_type, original_value, corrupted_value):
        """Record corruption of a specific field."""
        if field_name not in self.corruption_by_field:
            self.corruption_by_field[field_name] = {
                'count': 0,
                'types': {},
                'examples': []
            }
            
        self.corruption_by_field[field_name]['count'] += 1
        
        if corruption_type not in self.corruption_by_field[field_name]['types']:
            self.corruption_by_field[field_name]['types'][corruption_type] = 0
        self.corruption_by_field[field_name]['types'][corruption_type] += 1
        
        # Keep only last 5 examples to avoid memory issues
        if len(self.corruption_by_field[field_name]['examples']) < 5:
            self.corruption_by_field[field_name]['examples'].append({
                'original': str(original_value),
                'corrupted': str(corrupted_value),
                'type': corruption_type
            })
            
        self.corruption_by_type[corruption_type] += 1
        
    def log_corruption_statistics(self):
        """Log comprehensive corruption statistics."""
        logger.info("Message Corruption Statistics:")
        logger.info(f"Total messages processed: {self.total_messages_processed}")
        logger.info(f"Messages lost: {self.messages_lost} (attempts: {self.loss_attempts})")
        logger.info(f"Messages corrupted: {self.messages_corrupted} (attempts: {self.corruption_attempts})")
        
        if self.total_messages_processed > 0:
            loss_rate = (self.messages_lost / self.total_messages_processed) * 100
            corruption_rate = (self.messages_corrupted / self.total_messages_processed) * 100
            logger.info(f"Loss rate: {loss_rate:.2f}%")
            logger.info(f"Corruption rate: {corruption_rate:.2f}%")
            
        # Log corruption by type
        if any(count > 0 for count in self.corruption_by_type.values()):
            logger.info("Corruption by data type:")
            for data_type, count in self.corruption_by_type.items():
                if count > 0:
                    logger.info(f"  {data_type}: {count}")
                    
        # Log corruption by field
        if self.corruption_by_field:
            logger.info("Corruption by field:")
            for field_name, field_stats in self.corruption_by_field.items():
                logger.info(f"  {field_name}: {field_stats['count']} corruptions")
                for corruption_type, type_count in field_stats['types'].items():
                    logger.info(f"    {corruption_type}: {type_count}")
                    
        # Log recent corruption events (last 10)
        if self.corruption_log:
            logger.info("Recent corruption events:")
            recent_events = self.corruption_log[-10:] if len(self.corruption_log) > 10 else self.corruption_log
            for event in recent_events:
                if event['type'] == 'loss':
                    logger.info(f"  [Loss] Message: {event['message'][:50]}... (p={event['probability']})")
                else:
                    logger.info(f"  [Corruption] Original: {event['original'][:30]}... -> Corrupted: {event['corrupted'][:30]}...")
                    
    def get_statistics_summary(self):
        """Get a summary of corruption statistics as a dictionary."""
        return {
            'total_processed': self.total_messages_processed,
            'messages_lost': self.messages_lost,
            'messages_corrupted': self.messages_corrupted,
            'loss_attempts': self.loss_attempts,
            'corruption_attempts': self.corruption_attempts,
            'loss_rate': (self.messages_lost / self.total_messages_processed * 100) if self.total_messages_processed > 0 else 0,
            'corruption_rate': (self.messages_corrupted / self.total_messages_processed * 100) if self.total_messages_processed > 0 else 0,
            'corruption_by_type': self.corruption_by_type.copy(),
            'corruption_by_field': {k: v['count'] for k, v in self.corruption_by_field.items()}
        }


# Global instance for tracking corruption statistics
corruption_stats = MessageCorruptionStats()


# function to get corruption info and the message content and do
def corrupt_message(message_content, corruption_info):
    # Record that we're processing a message
    corruption_stats.record_message_processed()
    
    if corruption_info is None:
        return message_content

    if corruption_info.get(Constants.RESERVED_PROBABILITY_OF_LOSS) is not None:
        # get random number between 0 and 1
        random_number = random.random()
        loss_probability = corruption_info.get(Constants.RESERVED_PROBABILITY_OF_LOSS)
        if random_number < loss_probability:
            logger.debug(f"message lost: {message_content}")
            logger.info(f"message lost: {message_content}")
            corruption_stats.record_message_lost(message_content, loss_probability)
            return None
        else:
            corruption_stats.record_loss_attempt()

    if corruption_info.get(Constants.RESERVED_PROBABILITY_OF_CORRUPTION) is not None:
        random_number = random.random()
        corruption_probability = corruption_info.get(Constants.RESERVED_PROBABILITY_OF_CORRUPTION)
        if random_number < corruption_probability:
            # balagan
            original_content = message_content
            corrupted_content = corrupt_message_content(message_content, corruption_info.get("corruption"))
            if corrupted_content != original_content:
                corruption_stats.record_message_corrupted(original_content, corrupted_content, corruption_info.get("corruption"))
            return corrupted_content
        else:
            corruption_stats.record_corruption_attempt()

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

        original_value = corrupted_content[field]

        if isinstance(corruption_value, str) and corruption_value == "_RANDOM":
            # Handle random corruption
            if isinstance(original_value, (int, float)):
                # For numbers, add random offset
                # generate random bit between 0 to the size of the number and flip it
                bit_to_flip = random.randint(0, len(str(original_value)))
                # flip the bit
                corrupted_content[field] = original_value ^ (1 << bit_to_flip)
                corruption_stats.record_field_corruption(field, 'int' if isinstance(original_value, int) else 'float', 
                                                       original_value, corrupted_content[field])

            elif isinstance(original_value, str):
                # For strings, either reverse it or add corruption marker
                if not original_value:
                    continue
                index = random.randint(0, len(original_value) - 1)
                char = random.choice(string.ascii_letters + string.digits)
                corrupted_content[field] = original_value[:index] + char + original_value[index + 1:]
                corruption_stats.record_field_corruption(field, 'str', original_value, corrupted_content[field])

            elif isinstance(original_value, bool):
                # For booleans, flip the value
                corrupted_content[field] = not original_value
                corruption_stats.record_field_corruption(field, 'bool', original_value, corrupted_content[field])

            elif isinstance(original_value, list):
                # For lists, shuffle the elements
                corrupted_list = original_value.copy()
                random.shuffle(corrupted_list)
                corrupted_content[field] = corrupted_list
                corruption_stats.record_field_corruption(field, 'list', original_value, corrupted_content[field])

        else:
            # Direct value replacement
            corrupted_content[field] = corruption_value
            corruption_stats.record_field_corruption(field, 'direct_replacement', original_value, corruption_value)

    # print the original and the corrupted content
    logger.debug(f"original content: {message_content}\n corrupted content: {corrupted_content}")

    return corrupted_content


def log_all_error_statistics():
    """
    Convenience function to log all error module statistics.
    Should be called at the end of simulation to get comprehensive error statistics.
    """
    logger.info("=== ERROR MODULE CORRUPT MESSAGES STATISTICS ===")
    corruption_stats.log_corruption_statistics()
    logger.info("=== END OF ERROR MODULE CORRUPT MESSAGES STATISTICS ===")

def get_all_error_statistics():
    """
    Get all error statistics as a dictionary for analysis.
    
    Returns:
        dict: Comprehensive error statistics
    """
    return {
        'corruption_stats': corruption_stats.get_statistics_summary()
    }


def reset_error_statistics():
    """
    Reset all error statistics. Useful for running multiple simulations.
    """
    global corruption_stats
    corruption_stats = MessageCorruptionStats()
    logger.info("Error module statistics reset")
