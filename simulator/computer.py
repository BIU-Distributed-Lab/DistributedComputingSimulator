"""
Computer module representing a node in the distributed network simulation.

This module defines the `Computer` class, which is used to represent a computer node in the network, including its connections, delays, and other properties.
"""
from utils.logger_config import logger
from simulator.config import NodeState
from typing import Optional, List


class Computer:
    """
    A class representing a computer in the network.

    Attributes:
        id (int): The ID of the computer.
        connectedEdges (list of int): List of computer IDs to which this computer is connected.
        algorithm_file (module): The algorithm file associated with this computer.
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
        self.algorithm_file = None
        self._state = NodeState.ACTIVE
        self.is_root = False
        self.color = "olivedrab"
        self.inputs = {}
        self.outputs = {}
        self.received_msg_count = 0
        self.sent_msg_count = 0

    @property
    def state(self) -> NodeState:
        """Get the current state of the computer."""
        return self._state

    @state.setter
    def state(self, value: NodeState) -> None:
        """Set the state, ensuring it's a valid NodeState value."""
        if not isinstance(value, NodeState):
            raise ValueError(f"State must be a NodeState enum value, got {type(value)}")
        if self._state != value:
            self._has_changed = True
            logger.info(f"Computer {self.id} is changing state from {self._state.value} to {value.value}")
            self._state = value

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
        if not name.startswith('_') and getattr(self, name, None) != value and name != "algorithm_file" and name != "id" and name != "connectedEdges" and name != "delays" and name != "received_msg_count" and name != "sent_msg_count":   
            self._has_changed = True
            # print the id and what is changing
            logger.info(f"Computer {self.id} is changing {name} to {value}")
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

    def collapse(self):
        """
        Collapses the computer.
        """
        self.state = NodeState.COLLAPSED
        logger.info(f"Computer {self.id} has collapsed")
        logger.debug(f"Computer {self.id} has collapsed")
        

    def update_received_msg_count(self, delta):
        """
        Updates the received message count for the computer.
        """
        self.received_msg_count += delta

    def update_sent_msg_count(self, delta):
        """
        Updates the sent message count for the computer.
        """
        self.sent_msg_count += delta
