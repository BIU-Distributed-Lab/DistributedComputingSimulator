import ast

import simulator.computer as computer
from simulator.communication import Communication
from simulator.message import Message
from simulator.config import NodeState



colors = ["blue", "red", "green", "yellow", "coral", "pink", "orange", "cyan", "magenta", "lime", "teal", "lavender",
          "brown", "maroon", "navy", "olive", "purple", "salmon", "gold", "silver"]

collapse_config = {
}

reorder_config = None


def init(self: computer.Computer, communication: Communication):
    self.inputs = {self.id: self.id}
    self.color = colors[int(self.id) % len(colors)]
    self.farthest_node = self.id
    self.farthest_distance = 0
    self.distance_vector = [999999] * len(communication.network.network_dict)#start with max distance
    self.distance_vector[self.id-1] = 0  # Distance to self is 0

"""
Algorithm that finds the farthest node in the network and sets the color to that number 
"""

def mainAlgorithm(self: computer.Computer, communication: Communication, round, messages=None):
    if round == 0:
       communication.send_to_all(self.id, f"LEADER {self.id} {self.distance_vector}", round)
       return
    bool_new = False
    for messages in messages:
        message_parts = messages.split(" ", 2)  # Split into max 3 parts

        array_str = message_parts[2]

        message_vector2 = ast.literal_eval(array_str)  # Convert string representation of list to actual list
        for i in range(len(self.distance_vector)):
            if message_vector2[i] + 1 < self.distance_vector[i]:
                self.distance_vector[i] = message_vector2[i] + 1  # Update distance vector with the received message
                if self.distance_vector[i] > self.farthest_distance:
                    bool_new = True
                    self.farthest_distance = self.distance_vector[i]
                    self.farthest_node = i + 1

    communication.send_to_all(self.id, f"LEADER {self.id} {self.distance_vector}", round)#send the updated distance vector to all neighbors
    self.color = colors[int(self.farthest_node) % len(colors)]

    if not bool_new:
        self.state = NodeState.TERMINATED

