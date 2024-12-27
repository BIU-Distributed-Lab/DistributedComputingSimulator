import simulator.computer as computer
from simulator.communication  import Communication
from utils.logger_config import logger
''' user implemented code that runs a broadcast algorithm'''

def mainAlgorithm(self: computer.Computer, communication: Communication, _arrival_time, message = None):
    if  self.state != "terminated":
        communication.send_to_all(self.id, "running a broadcast", _arrival_time)
        self.color = "#7427e9"
        self.state = "terminated"


def init(self: computer.Computer, communication : Communication):
    if self.is_root:
        logger.info("%s is root", self.id)
        communication.send_to_all(self.id, "running a broadcast")
        self.color = "#000000"
        self.state = "terminated"
