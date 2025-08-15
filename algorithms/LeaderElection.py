import simulator.computer as computer
from simulator.communication import Communication
from simulator.message import Message
from simulator.config import NodeState
import numpy as np
import time

colors = ["blue", "red", "green", "yellow", "purple", "pink", "orange", "cyan", "magenta", "lime", "teal", "lavender",
          "brown", "maroon", "navy", "olive", "coral", "salmon", "gold", "silver"]

collapse_config = {
}

reorder_config = None


def init(self: computer.Computer, communication: Communication):
    if self.is_root:
        self.distance = 0
        self.parent = self.id
        self.color = colors[0]
    else:
        self.distance = np.inf
        self.parent = None
    self.number_of_comps = 5
    self.inputs = {self.id: self.id}
    self.leader = self.id
    communication.send_to_all(self.id, f"LEADER {self.id} {self.leader}") # Send initial message to all nodes
    self.color = colors[int(self.leader) % len(colors)]


def mainAlgorithm(self: computer.Computer, communication: Communication, _arrival_time, messages=None):
    found_leader = False
    #print(f"Node {self.id} received message: {messages}")
    message_parts = messages.split(" ")
    #print(message_parts)
    message_id = int(message_parts[1])
    message_leader = int(message_parts[2])
    self.inputs[message_id] = message_leader
    #print(self.inputs)
    if int(message_leader) > int(self.leader):
        self.leader = message_leader
        #print(f"Node {self.id} found new leader: {self.leader}")
        self.color = colors[int(self.leader) % len(colors)]
        communication.send_to_all(self.id, f"LEADER {self.id} {self.leader}")
        
    total = 0
    for key, value in self.inputs.items():
        if value == self.leader:
                total += 1
        if total >= self.number_of_comps / 2:
            found_leader = True
        if not found_leader:
            communication.send_to_all(self.id, f"LEADER {self.id} {self.leader}")
        else:
            self.state = NodeState.TERMINATED
    
