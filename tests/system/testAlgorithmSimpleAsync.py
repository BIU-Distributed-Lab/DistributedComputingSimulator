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
    self.messages_received = 0
    # Send initial leader message
    communication.send_to_all(self.id, f"LEADER {self.id} {self.leader}", 0)


def mainAlgorithm(self: computer.Computer, communication: Communication, _arrival_time, message=None):
    if message is None:
        return

    self.messages_received += 1

    # Parse the message
    message_parts = message.split(" ")
    message_id = int(message_parts[1])
    message_leader = int(message_parts[2])

    self.inputs[message_id] = message_leader

    # Update leader if a higher ID is found
    if int(message_leader) > int(self.leader):
        self.leader = message_leader
        self.color = colors[int(self.leader) % len(colors)]
        # Propagate the new leader information
        communication.send_to_all(self.id, f"LEADER {self.id} {self.leader}", _arrival_time)

    # Terminate after receiving messages from all neighbors
    if self.messages_received >= len(self.connectedEdges):
        self.color = "pink"
        self.state = NodeState.TERMINATED