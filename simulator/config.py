from enum import Enum


class NodeState(Enum):
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