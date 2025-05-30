import simulator.computer as computer
from simulator.communication import Communication
from simulator.message import Message
from simulator.config import NodeState
import numpy as np
from utils.logger_config import logger
import simulator.Constants as Constants


''' 
user implemented code that runs a BFS algorithm

The following data exists for every computer:
- parent - the parents id
- distance - the distance of the computer from the root computer.
'''

colors = ["blue", "red", "green", "yellow", "purple", "pink", "orange", "cyan", "magenta", "lime", "teal", "lavender",
          "brown", "maroon", "navy", "olive", "coral", "salmon", "gold", "silver"]


def mainAlgorithm(self: computer.Computer, communication: Communication, _arrival_time, message = None):

    parent = message.get("parent")
    dist = message.get("distance")

    if dist + 1 < self.distance:
        self.parent = parent
        self.distance = dist + 1
        color_index = int(dist) % len(colors)
        self.color = colors[color_index]
      
        x = {
            "distance": self.distance,
            "parent": self.id,
        }


        x_balagan = {
            Constants.RESERVED_PROBABILITY_OF_LOSS: 0.6,
            Constants.RESERVED_PROBABILITY_OF_CORRUPTION: 0.5,
            "corruption": {
                "distance": "_RANDOM",
            }
        }

        communication.send_to_all(self.id, x, _arrival_time, x_balagan)


def init(self: computer.Computer, communication: Communication):
    if self.is_root:
        logger.info(f"{self.id} is the root")
        self.parent = self.id
        self.distance = 0
       
        x = {
            "distance": self.distance,
            "parent": self.id,
        }

        communication.send_to_all(self.id, x)

        self.color = "#000000"
        self.state = NodeState.TERMINATED
    else:
        self.parent = None
        self.distance = np.inf
