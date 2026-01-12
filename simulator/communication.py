"""
Communication module for handling message passing between computers in a simulated network.

This module handles the sending and receiving of messages between computers in the network, including broadcasting messages and running algorithms.
"""

import random
from simulator.computer import Computer
import simulator.initializationModule as initializationModule
from simulator.config import NodeState
from simulator.message import Message
from utils.logger_config import logger
import simulator.errorModule as errorModule
from simulator.errorModule import ReorderConfig


class Communication:
    """
    A class to handle communication between computers in a distributed network simulation.
    
    Attributes:
        network (Initialization): The network initialization object containing the computers and configurations.
    """

    def __init__(self, network: initializationModule.Initialization):
        """
        Initializes the Communication instance with the given network.
        
        Args:
            network (Initialization): The initialized network containing the computers.
        """
        self.network = network
        # dict to hold the last time message sent for the async case for each edge, (source_id, dest_id) -> time
        self.last_arrival_time = {}

    # Send a message from the source computer to the destination computer
    def send_message(self, source, dest, message_info, sent_time=None, corruption_info=None):
        """
        Sends a message from the source computer to the destination computer, with optional arrival time.
        if the destination computer is terminated, the message will not be sent.
        if the source computer is terminated, the message will not be sent.
        
        Args:
            source (int): The ID of the source computer sending the message.
            dest (int): The ID of the destination computer receiving the message.
            message_info (str): The content of the message being sent.
            sent_time (float, optional): The time at which the message was sent. If None, defaults to 0.
            corruption_info (dict, optional): The corruption information of the message being sent.
        """
        # check if dest connected to source
        if dest not in self.network.network_dict.get(source).connectedEdges:
            logger.info(f"Cannot send message from {source} to {dest} because they are not connected.")
            return

        if sent_time is None:
            sent_time = 0

        # get the delay of that edge if async
        if self.network.sync == 'Async':
            if self.network.delay_type == 'Random':
                # generate a random delay between 0 and 1
                edge_delay = random.uniform(0, 1)
                #logger.debug(f"Random edge delay from {source} to {dest} is {edge_delay}")

                if self.network.reorder_config.is_edge_ordered(source, dest):
                    # so we can see sent time needs to be the max of the last arrival time and the current sent time
                    logger.debug(f"send_time before max check: {sent_time}")

                    sent_time = max(sent_time, self.last_arrival_time.get((source, dest), 0))

                    # sent_time = self.last_arrival_time.get((source, dest), 0)

                else:
                    #logger.debug(f"Edge {source} to {dest} is not ordered")
                    pass

            else:
                # get the delay of the edge
                edge_delay = self.network.get_edge_delay(source, dest)
                logger.debug(f"Edge delay from {source} to {dest} is {edge_delay}")
        else:
            # in sync, we want to use a constant delay of 1 round
            edge_delay = 1

        current_computer = self.network.network_dict.get(source)

        current_computer_active = current_computer.state != NodeState.COLLAPSED
        dest_computer_active = self.network.network_dict.get(dest).state == NodeState.ACTIVE

        if current_computer_active and dest_computer_active:
            # creating a new message which will be put into the queue
            message = Message(
                source_id=source,
                dest_id=dest,
                arrival_time=sent_time + edge_delay,#bug here
                content=message_info
            )

            if corruption_info is not None:
                message.content = errorModule.corrupt_message(message.content, corruption_info)

            if message.content is not None:
                self.network.message_queue.push(message)
                current_computer.update_sent_msg_count(1)
                # Check collapse after sending the message
                self.network.collapse_config.should_collapse(current_computer)
                self.last_arrival_time[(source, dest)] = sent_time + edge_delay

    def send_to_all(self, source_id, message_info, sent_time=None, corruption_info=None):
        """
        Sends a message from the source computer to all connected computers.
        
        Args:
            source_id (int): The ID of the source computer sending the message.
            message_info (str): The content of the message being sent.
            sent_time (float, optional): The time at which the message was sent. If None, defaults to 0.
            corruption_info (dict, optional): The corruption information of the message being sent.
        """
        source_computer = self.network.network_dict.get(source_id)
        for index, connected_computer_id in enumerate(source_computer.connectedEdges):
            self.send_message(source_id, connected_computer_id, message_info, sent_time, corruption_info)

    def receive_message(self, message: Message, comm):
        """
        Receives a message and runs the appropriate algorithm on the destination computer.
        
        Args:
            message (Message): The message that was received.
            comm (Communication): The communication object handling the message passing.
        """
        #if self.network.logging_type == "Long":\
        logger.info(message.to_dict())

        received_computer = self.network.network_dict.get(message.dest_id)

        if received_computer.state != NodeState.ACTIVE:
            logger.info(f"Computer {received_computer.id} is not active, ignoring message.")
            return

        received_computer.update_received_msg_count(1)
        # Check if the computer should collapse after receiving the message
        self.network.collapse_config.should_collapse(received_computer, message)

        self.run_algorithm(received_computer, 'mainAlgorithm', message.arrival_time, message.content)

    def run_algorithm(self, comp: Computer, function_name: str, arrival_time=None, message_content=None):
        """
        Runs the specified algorithm on the given computer, handling the provided message content and arrival time.
        
        Args:
            comp (Computer): The computer object on which to run the algorithm.
            function_name (str): The name of the function (algorithm) to be executed.
            arrival_time (float, optional): The time the message arrived, if applicable.
            message_content (str, optional): The content of the message being processed by the algorithm.
        """
        algorithm_function = getattr(comp.algorithm_file, function_name, None)
        if callable(algorithm_function):
            if function_name == 'init':
                algorithm_function(comp, self)  # Call with two arguments
            elif function_name == 'mainAlgorithm':
                algorithm_function(comp, self, arrival_time, message_content)

            if self.network.display_type == "Graph" and comp.has_changed():
                self.network.node_values_change.append((comp.__dict__.copy(), arrival_time))
                comp.reset_flag()
        else:
            logger.info(f"Error: Function '{function_name}' not found in {comp.algorithm_file}.py")
            return None
