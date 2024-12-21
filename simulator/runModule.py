"""
Main module to run the network simulation.

This module initializes the network, runs the algorithms on each computer, and manages the message queue for the simulation.
"""

import simulator.initializationModule as initializationModule
import simulator.communication as communication


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

    print("************************************************************************************")

    ## runs mainAlgorithm
    while not network.message_queue.empty():
        message = network.message_queue.pop()
        comm.receive_message(message, comm)


def sync_run(network: initializationModule.Initialization, comm: communication.Communication):
    current_round = 0
    all_terminated = len(network.connected_computers)

    while all_terminated > 0:
        all_terminated = len(network.connected_computers)

        for comp in network.connected_computers:
            if comp.state == "terminated":
                all_terminated -= 1
                continue

            # Get messages for the current computer from the dictionary and clear the key
            current_messages = network.message_queue.get_messages_for_specific_dest(comp.id, current_round)
            network.message_queue.clear_key(comp.id)

            comm.run_algorithm(comp, 'mainAlgorithm', current_round, current_messages)

        current_round += 1
