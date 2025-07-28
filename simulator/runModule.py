"""
Main module to run the network simulation.

This module initializes the network, runs the algorithms on each computer, and manages the message queue for the simulation.
"""

import simulator.initializationModule as initializationModule
import simulator.communication as communication
from simulator.config import NodeState
from utils.logger_config import logger
from simulator.Constants import *
from simulator.errorModule import log_all_error_statistics
import psutil
import time

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

            # Update received message count for each message
            comp.update_received_msg_count(len(current_messages))

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

    # 1. Basic network statistics
    logger.info("\n\nBasic Network Statistics:\n")
    logger.info("   Total computers: %s", len(network.connected_computers))
    # logger.info("   Real-time seconds elapsed: %s seconds", time.time() - network.start_time)

    # 2. Message statistics
    logger.info("\n\nMessage Statistics:\n")
    logger.info("   Total messages sent: %s", network.message_queue.total_messages_sent)
    logger.info("   Total messages received: %s", network.message_queue.total_messages_received)
    logger.info("   Messages lost: %s", network.message_queue.total_messages_sent - network.message_queue.total_messages_received)
    logger.info("   Corrupted messages: %s", network.message_queue.corrupted_messages if hasattr(network.message_queue, 'corrupted_messages') else 0)

    # 3. Node communication statistics
    logger.info("\n\nNode Communication Statistics:\n")
    total_nodes = len(network.connected_computers)
    avg_messages_per_node = (network.message_queue.total_messages_sent + network.message_queue.total_messages_received) / (2 * total_nodes)
    logger.info("   Average messages per node: %.2f", avg_messages_per_node)

    # Get top 10 chatty nodes
    node_stats = [(comp.id, comp.sent_msg_count + comp.received_msg_count) for comp in network.connected_computers]
    node_stats.sort(key=lambda x: x[1], reverse=True)
    logger.info("   Top 10 chatty nodes:")
    for node_id, msg_count in node_stats[:10]:
        logger.info("      Node %d: %d messages", node_id, msg_count)

    # 4. Node collapse statistics
    # logger.info("\n4. Node Collapse Statistics:")
    # collapsed_nodes = [comp for comp in network.connected_computers if comp.state == NodeState.COLLAPSED]
    # collapse_percentage = (len(collapsed_nodes) / total_nodes) * 100
    # logger.info("   Number of collapsed nodes: %d (%.2f%%)", len(collapsed_nodes), collapse_percentage)
    # if collapsed_nodes:
    #     logger.info("   IDs of collapsed nodes: %s", [node.id for node in collapsed_nodes])
    #     if hasattr(network.collapse_config, 'collapse_log'):
    #         collapse_times = [info['round'] for info in network.collapse_config.collapse_log.values() if info['round'] is not None]
    #         if collapse_times:
    #             logger.info("   First collapse time: %d", min(collapse_times))
    #             logger.info("   Last collapse time: %d", max(collapse_times))

    # 5. System resource statistics
    logger.info("\n\nSystem Resource Statistics:\n")
    process = psutil.Process()
    memory_info = process.memory_info()
    logger.info("   Peak memory consumption: %.2f MB", memory_info.peak_wset / (1024 * 1024))
    try:
        cpu_percent = process.cpu_percent(interval=1.0)
        logger.info("   Average CPU utilization: %.2f%%", cpu_percent)
    except:
        logger.info("   CPU utilization: Not measurable")

    # Log existing statistics
    logger.info("\n\nError Module Statistics:\n")
    network.collapse_config.log_collapse_statistics()
    network.reorder_config.log_reorder_statistics()
    log_all_error_statistics()
    logger.info("\nEnd of Error Module Statistics\n")
    logger.info("\nOutputs:\n%s", [comp.outputs for comp in network.network_dict.values()])
    logger.info("************************************************************************************")
