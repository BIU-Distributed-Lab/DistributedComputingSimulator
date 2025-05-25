import simulator.computer as computer
from simulator.communication import Communication
from simulator.message import Message
import numpy as np
import random


def init(self: computer.Computer, communication: Communication):
    """
    Initialize the node's state before starting the synchronous rounds.
    """
    self.active = True
    self.in_mis = False
    self.priority = None
    self.color = "white"
    self.state = "running"


def mainAlgorithm(self: computer.Computer, communication: Communication, round, messages: list[Message] = None):
    step = round % 3  # 0: send priority, 1: receive priorities, 2: receive IN_MIS

    if self.state == "terminated":
        return

    if step == 0:
        # Pick random priority and broadcast
        if self.active:
            self.priority = random.random()
            communication.send_to_all(self.id, f"PRIORITY {self.priority}", round)
        self.state = "running"

    elif step == 1:
        # Collect neighbors' priorities and determine if this node has the highest
        if self.active:
            highest = True
            for msg in messages:
                parts = msg.content.split(" ")
                if parts[0] == "PRIORITY":
                    neighbor_priority = float(parts[1])
                    if neighbor_priority > self.priority:
                        highest = False
            if highest:
                self.in_mis = True
                self.active = False
                self.color = "blue"
                communication.send_to_all(self.id, "IN_MIS", round)
        self.state = "running"

    elif step == 2:
        # If neighbor is in MIS, deactivate
        if self.active:
            for msg in messages:
                if msg.content == "IN_MIS":
                    self.active = False
                    self.color = "gray"
                    break
        # If no longer active, mark as terminated
        if not self.active:
            self.terminated = True
            self.state = "terminated"
