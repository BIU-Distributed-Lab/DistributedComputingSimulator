import simulator.computer as computer
from simulator.communication import Communication
import numpy as np

colors = ["blue", "red", "green", "yellow", "purple", "pink", "orange", "cyan", "magenta", "lime", "teal", "lavender",
          "brown", "maroon", "navy", "olive", "coral", "salmon", "gold", "silver"]

def mainAlgorithm(self: computer.Computer, communication: Communication, round, messages=None):
    #print(f"Computer {self.id} is running the main algorithm, round {round}")
    if round == 0:
        # Initialize the root node
        print(f"id = {self.id}, self.height = {self.height}, self.weight = {self.weight}")
        self.state = 'terminated'
