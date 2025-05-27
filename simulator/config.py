from enum import Enum

class NodeState(Enum):
    """Enum representing possible states of a node in the network."""
    ACTIVE = "active"
    TERMINATED = "terminated"
    INITIALIZING = "initializing" 