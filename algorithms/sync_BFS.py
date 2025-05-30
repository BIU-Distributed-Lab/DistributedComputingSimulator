import simulator.computer as computer
from simulator.communication import Communication
from simulator.message import Message
from simulator.config import NodeState
import numpy as np

colors = ["blue", "red", "green", "yellow", "purple", "pink", "orange", "cyan", "magenta", "lime", "teal", "lavender",
          "brown", "maroon", "navy", "olive", "coral", "salmon", "gold", "silver"]


def init(self: computer.Computer, communication: Communication):
    """
    Initialize the node's state before starting the synchronous rounds.
    """
    if self.is_root:
        self.distance = 0
        self.parent = self.id
        self.color = colors[0]
        self.state = NodeState.ACTIVE
    else:
        self.distance = np.inf
        self.parent = None
        self.state = NodeState.ACTIVE


def mainAlgorithm(self: computer.Computer, communication: Communication, round, messages = None):
    if round == 0:
        # Send initial message if root
        if self.is_root:
            communication.send_to_all(self.id, f"INITIALIZE {self.distance} {self.parent}", round)
            self.state = NodeState.TERMINATED
    else:
        for message in messages:
            message_parts = message.split(" ")
            dist = float(message_parts[1])
            parent = int(message_parts[2])

            if dist + 1 < self.distance:
                self.parent = parent
                self.distance = dist + 1
                communication.send_to_all(self.id, f"UPDATE {self.distance} {self.id}", round)
                self.color = colors[int(self.distance) % len(colors)]
                self.state = NodeState.TERMINATED
