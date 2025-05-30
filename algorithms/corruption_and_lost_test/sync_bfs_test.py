import simulator.computer as computer
from simulator.communication import Communication
from simulator.message import Message
from simulator.config import NodeState
import numpy as np
from utils.logger_config import logger
import simulator.Constants as Constants

colors = ["blue", "red", "green", "yellow", "purple", "pink", "orange", "cyan", "magenta"]

def init(self: computer.Computer, communication: Communication):
    """
    Initialize the node's state before starting the synchronous rounds.
    """
    if self.is_root:
        self.distance = 0
        self.parent = self.id
        self.color = colors[0]
        self.state = NodeState.ACTIVE
        self.received_corrupted = False
    else:
        self.distance = np.inf
        self.parent = None
        self.state = NodeState.ACTIVE
        self.received_corrupted = False

def mainAlgorithm(self: computer.Computer, communication: Communication, round, messages = None):
    """
    Main algorithm that tests BFS with message loss and corruption.
    """
    if round == 0:
        # Root sends initial message with corruption config
        if self.is_root:
            message_content = {
                "distance": self.distance,
                "parent": self.id
            }
            

            
            communication.send_to_all(self.id, message_content, round)
            self.state = NodeState.TERMINATED
            
    else:
        if messages:
            for content in messages:
                if not isinstance(content, dict):
                    logger.warning(f"Node {self.id} received invalid message format: {content}")
                    continue
                    
                received_dist = content.get("distance")
                received_parent = content.get("parent")
                
                if received_dist is None or received_parent is None:
                    logger.warning(f"Node {self.id} received incomplete message: {content}")
                    continue
                
                # Check if this is a better path
                if received_dist + 1 < self.distance:
                    old_distance = self.distance
                    self.distance = received_dist + 1
                    self.parent = received_parent
                    
                    # Configure message with corruption for forwarding
                    message_content = {
                        "distance": self.distance,
                        "parent": self.id
                    }
                    
                    corruption_config = {
                        Constants.RESERVED_PROBABILITY_OF_LOSS: 0,
                        Constants.RESERVED_PROBABILITY_OF_CORRUPTION: 1,
                        "corruption": {
                            "distance": "_RANDOM"
                        }
                    }
                    
                    communication.send_to_all(self.id, message_content, round, corruption_config)
                    
                    # Update color based on distance
                    self.color = colors[int(self.distance) % len(colors)]
                    
                    # Log the update
                    logger.info(f"Node {self.id} updated distance from {old_distance} to {self.distance}")
                    
                    if abs(self.distance - received_dist - 1) > 0.1:  # Check if distance is corrupted
                        self.received_corrupted = True
                        logger.warning(f"Node {self.id} detected corrupted distance: expected {received_dist + 1}, got {self.distance}")
                
                # Terminate after processing messages
                self.state = NodeState.TERMINATED 