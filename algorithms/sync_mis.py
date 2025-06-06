import simulator.computer as computer
from simulator.communication import Communication
from simulator.message import Message
from simulator.config import NodeState
import numpy as np
import random

reorder_config = None  # Placeholder for reorder configuration, if needed

collapse_config = None  # Placeholder for collapse configuration, if needed

def init(self: computer.Computer, communication: Communication):
    """
    Initialize the node's state before starting the synchronous rounds.
    """
    self.in_mis = False
    self.priority = None
    self.color = "white"
    self.state = NodeState.ACTIVE


def mainAlgorithm(self: computer.Computer, communication: Communication, round, messages = None):
    step = round % 3  # 0: send priority, 1: receive priorities, 2: receive IN_MIS

    if self.state == NodeState.TERMINATED:
        return

    if step == 0:
        # Pick random priority and broadcast
        if self.state == NodeState.ACTIVE:
            self.priority = random.random()
            communication.send_to_all(self.id, f"PRIORITY {self.priority}", round)

    elif step == 1:
        # Collect neighbors' priorities and determine if this node has the highest
        if self.state == NodeState.ACTIVE:
            highest = True
            for msg in messages:
                parts = msg.split(" ")
                if parts[0] == "PRIORITY":
                    neighbor_priority = float(parts[1])
                    if neighbor_priority > self.priority:
                        highest = False
            if highest:
                self.in_mis = True
                self.state = NodeState.TERMINATED
                self.color = "blue"
                communication.send_to_all(self.id, "IN_MIS", round)

    elif step == 2:
        # If neighbor is in MIS, deactivate
        if self.state == NodeState.ACTIVE:
            for msg in messages:
                if msg == "IN_MIS":
                    self.state = NodeState.TERMINATED
                    self.color = "gray"
                    break
