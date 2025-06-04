"""
Main module to run the network simulation.

This module initializes the network, runs the algorithms on each computer, and manages the message queue for the simulation.
"""

import simulator.initializationModule as initializationModule
import simulator.communication as communication
from simulator.config import NodeState
from utils.logger_config import logger
from simulator.Constants import *

def initiateRun(network: initializationModule.Initialization, comm: communication.Communication, sync: str):
    """
    Runs the network algorithm on the created network.

    This function runs the `init` function on every computer in the network, enqueues messages,
    and processes the messages by running the main algorithm until the message queue is empty.

    Args:
        network (Initialization): The initialized network with connected computers.
        comm (Communication): The communication object handling message passing between computers.
    """
    if sync == "Sync":
        sync_run(network, comm)
    else:
        async_run(network, comm)

    # Log the statistics after the run
    log_statistics(network)


def async_run(network: initializationModule.Initialization, comm: communication.Communication):
    """
    Runs the network algorithm asynchronously on the created network.

    This function runs the `init` function on every computer in the network, enqueues messages,
    and processes the messages by running the main algorithm until the message queue is empty.

    Args:
        network (Initialization): The initialized network with connected computers.
        comm (Communication): The communication object handling message passing between computers.
    """
    # runs init() for every computer which must be defined, and puting messages into the network queue
    for comp in network.connected_computers:
        comm.run_algorithm(comp, 'init')

    logger.info("************************************************************************************")

    ## runs mainAlgorithm
    while not network.message_queue.empty():
        message = network.message_queue.pop()
        comm.receive_message(message, comm)
        # comp = network.network_dict.get(message.dest_id)
        # network.collapse_config.should_collapse(comp, message)

    logger.info("************************************************************************************")
    logger.info("Async run completed")  

def sync_run(network: initializationModule.Initialization, comm: communication.Communication):
    """
    Runs the network algorithm synchronously on the created network.
    First runs the initialization phase, then proceeds with synchronous rounds.

    Args:
        network (Initialization): The initialized network with connected computers.
        comm (Communication): The communication object handling message passing between computers.
    """
    # Initialization phase - run init() for every computer
    for comp in network.connected_computers:
        comm.run_algorithm(comp, 'init')

    logger.info("************************************************************************************")
    logger.info("Initialization phase completed, starting synchronous rounds")

    current_round = 0
    all_terminated = len(network.connected_computers)

    while all_terminated > 0:
        logger.info("Current round: %s", current_round)
        all_terminated = len(network.connected_computers)

        for comp in network.connected_computers:
            if comp.state == NodeState.TERMINATED or comp.state == NodeState.COLLAPSED:
                all_terminated -= 1
                continue

            # Get messages for the current computer from the dictionary and clear the key
            current_messages = network.message_queue.get_messages_for_specific_dest(comp.id, current_round)
            #logger.info("Current messages for computer %s: %s", comp.id, current_messages)
            network.message_queue.clear_key(comp.id)
            # we want to take only the content of each message and send as alist
            current_messages = [message.content for message in current_messages]
            network.collapse_config.should_collapse(comp, current_round, current_messages)
            comm.run_algorithm(comp, 'mainAlgorithm', current_round, current_messages)

        # randomly collapse:
        network.collapse_config.maybe_collapse_randomly(network.network_dict)

        current_round += 1
        if current_round > NUMBER_OF_ROUNDS:
            logger.info("Reached max number of rounds, stopping sync run")
            break

    logger.info("sync run completed")



def log_statistics(network: initializationModule.Initialization):
    """
    Logs the statistics of the network after the simulation run.

    Args:
        network (Initialization): The initialized network with connected computers.
    """
    logger.info("************************************************************************************")
    logger.info("Network Statistics:")
    logger.info("Total number of computers: %s", len(network.connected_computers))
    #logger.info("Total number of messages sent: %s", network.message_queue.total_messages_sent)
    #logger.info("Total number of messages received: %s", network.message_queue.total_messages_received)

    network.collapse_config.log_collapse_statistics()
    network.reorder_config.log_reorder_statistics()
    logger.info("************************************************************************************")
