import simulator.computer as computer
from simulator.communication import Communication
from simulator.message import Message
from simulator.config import NodeState
import numpy as np
from utils.logger_config import logger



reorder_config = {
    "(0,1)": 1,
}


collapse_config = {

}


def init(self: computer.Computer, communication: Communication):
    self.counter = 0
    self.partner_id = 1 if self.id == 0 else 0  # assumes nodes 0 and 1 are the pair
    self.state = NodeState.ACTIVE

    if self.id == 1:  # Node 1 starts the communication
        logger.info(f"{self.id} initiating ping-pong with Node {self.partner_id}")
        # Send two messages with increasing counters
        for i in range(10):
            communication.send_message(self.id, self.partner_id, f"counter {self.counter + i}")




def mainAlgorithm(self: computer.Computer, communication: Communication, _arrival_time, message: str = None):
    if message.startswith("counter"):
        parts = message.split()
        self.counter = int(parts[1]) + 1  # increment counter
        logger.info(f"{self.id} received counter {parts[1]}, incrementing to {self.counter}")

        # send back to partner
        #communication.send_message(self.id, self.partner_id, f"counter {self.counter}", _arrival_time)
