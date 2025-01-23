"""
Computer module representing a node in the distributed network simulation.

This module defines the `Computer` class, which is used to represent a computer node in the network, including its connections, delays, and other properties.
"""
from utils.logger_config import logger

class Computer:
    """
    A class representing a computer in the network.
    
    Attributes:
        id (int): The ID of the computer.
        connectedEdges (list of int): List of computer IDs to which this computer is connected.
        algorithm_file (module): The algorithm file associated with this computer.
        state (str): The state of the computer (e.g., active, idle, terminated).
        is_root (bool): Whether this computer is designated as the root node in the network.
        color (str): The color associated with this computer, used in visualization.
        _has_changed (bool): A private flag indicating whether the computer's state has changed.
    """
    
    def __init__(self, new_id=None):
        """
        Initializes a Computer object with default values for attributes.
        """
        self._has_changed = False
                
        self.id = new_id
        self.connectedEdges = []
        self.algorithm_file=None
        self.state = None
        self.is_root = False
        self.color = "olivedrab"

        self.inputs = {}
        self.outputs = {}

    def __str__(self):
        """
        Provides a string representation of the computer's ID, connections, and delays.
        
        Returns:
            str: The string representation of the computer.
        """
        return f"id = {self.id}\nconnected edges = {self.connectedEdges}\n"
    
    def __setattr__(self, name, value):
        """
        Overrides the default setattr method to set the `_has_changed` flag when non-private attributes change.
        
        Args:
            name (str): The name of the attribute being set.
            value (Any): The value to set the attribute to.
        """
        # Only set the flag if the attribute is not private
        if not name.startswith('_') and getattr(self, name, None) != value:
            self._has_changed = True
            # print the id and what is changing
            #logger.debug(f"Computer {self.id} is changing {name} to {value}")
        super().__setattr__(name, value)

    def reset_flag(self):
        """
        Resets the `_has_changed` flag to False.
        """
        self._has_changed = False

    def has_changed(self):
        """
        Returns whether the computer's state has changed.
        
        Returns:
            bool: True if the state has changed, False otherwise.
        """
        return self._has_changed
    
    def getConnectedEdges(self):
        """
        Returns the list of IDs of connected computers (edges).
        
        Returns:
            list of int: The connected edges for this computer.
        """
        return self.connectedEdges
    
    def getDelays(self):
        """
        Returns the list of delays for the connected edges.
        
        Returns:
            list of float: The delays associated with the connected edges.
        """
        return self.delays
