import simulator.computer as computer
from simulator.communication import Communication
from simulator.message import Message
from simulator.config import NodeState


colors = ["blue", "red", "green", "yellow", "purple", "pink", "orange", "cyan", "magenta", "lime", "teal", "lavender",
          "brown", "maroon", "navy", "olive", "coral", "salmon", "gold", "silver"]

collapse_config = {
}

reorder_config = None


def init(self: computer.Computer, communication: Communication):
    self.inputs = {self.id: self.id}
    self.leader = self.id
    self.color = colors[int(self.leader) % len(colors)]


def mainAlgorithm(self: computer.Computer, communication: Communication, round, messages=None):
    if(round == 0):
       communication.send_to_all(self.id, f"LEADER {self.id} {self.leader}", round)
       return
    for messages in messages:
        message_parts = messages.split(" ")
        #print(message_parts)
        message_id = int(message_parts[1])
        message_leader = int(message_parts[2])
        self.inputs[message_id] = message_leader
        #print(self.inputs)
        if int(message_leader) > int(self.leader):
            self.leader = message_leader
            self.color = colors[int(self.leader) % len(colors)]


    if(round == 2):
        self.state = NodeState.TERMINATED
