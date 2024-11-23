"""
Main module to run the network simulation.

This module initializes the network, runs the algorithms on each computer, and manages the message queue for the simulation.
"""

import simulator.initializationModule as initializationModule
import simulator.communication as communication


def initiateRun(network: initializationModule.Initialization, comm: communication.Communication):
    """
    Runs the network algorithm on the created network.

    This function runs the `init` function on every computer in the network, enqueues messages,
    and processes the messages by running the main algorithm until the message queue is empty.

    Args:
        network (Initialization): The initialized network with connected computers.
        comm (Communication): The communication object handling message passing between computers.
    """
    # runs init() for every computer which must be defined, and puting messages into the network queue
    for comp in network.connected_computers:
        comm.run_algorithmm(comp, 'init')

    print("************************************************************************************")

    ## runs mainAlgorithm
    while not network.message_queue.empty():
        message = network.message_queue.pop()
        comm.receive_message(message, comm)
