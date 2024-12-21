import simulator.computer as computer
from simulator.communication import Communication
import numpy as np

colors = ["blue", "red", "green", "yellow", "purple", "pink", "orange", "cyan", "magenta", "lime", "teal", "lavender",
          "brown", "maroon", "navy", "olive", "coral", "salmon", "gold", "silver"]

def mainAlgorithm(self: computer.Computer, communication: Communication, round, messages=None):
    #print(f"Computer {self.id} is running the main algorithm, round {round}")
    if round == 0:
        # Initialize the root node
        if self.is_root:
            self.distance = 0
            self.parent = self.id
            communication.send_to_all(self.id, f"INITIALIZE {self.distance} {self.parent}", round)
            self.color = colors[0]
            self.state = "terminated"
        else:
            self.distance = np.inf
            self.parent = None
    else:
        for message in messages:
            message_parts = message["content"].split(" ")
            dist = float(message_parts[1])
            parent = int(message_parts[2])

            if dist + 1 < self.distance:
                self.parent = parent
                self.distance = dist + 1
                communication.send_to_all(self.id, f"UPDATE {self.distance} {self.id}", round)
                self.color = colors[int(self.distance) % len(colors)]
                self.state = "terminated"
