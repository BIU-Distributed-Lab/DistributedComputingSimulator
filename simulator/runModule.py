"""
Main module to run the network simulation.

This module initializes the network, runs the algorithms on each computer, and manages the message queue for the simulation.
"""

import simulator.initializationModule as initializationModule
import simulator.communication as communication
from simulator.config import NodeState
from utils.logger_config import logger

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
            if comp.state == NodeState.TERMINATED:
                all_terminated -= 1
                continue

            # Get messages for the current computer from the dictionary and clear the key
            current_messages = network.message_queue.get_messages_for_specific_dest(comp.id, current_round)
            #logger.info("Current messages for computer %s: %s", comp.id, current_messages)
            network.message_queue.clear_key(comp.id)
            # we want to take only the content of each message and send as alist
            current_messages = [message.content for message in current_messages]
            comm.run_algorithm(comp, 'mainAlgorithm', current_round, current_messages)

        current_round += 1

    logger.info("sync run completed")
