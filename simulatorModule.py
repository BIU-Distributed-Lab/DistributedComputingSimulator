import json
import threading
import sys
import time
import json
import argparse

from utils.exceptions import *
from utils.logger_config import logger
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from utils.logger_config import logger
from utils.logger_config import loggerConfig
import simulator.runModule as runModule
import simulator.communication as communication
import simulator.initializationModule as initializationModule
import simulator.MainMenu as MainMenu
from simulator.MainMenu import NETWORK_VARIABLES
import visualizations.graphVisualization as graphVisualization
OUTPUT_FILE = './output.txt'

def load_network_variables():
    """
    Load default variables from the NETWORK_VARIABLES JSON file.
    
    Returns:
        dict: A dictionary of network variables loaded from the JSON file.
        
    Raises:
        FileNotFoundError: If the file is not found.
        json.JSONDecodeError: If the JSON is improperly formatted.
    """
    try:
        with open(NETWORK_VARIABLES, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def initializeSimulator():
    """
    Initializes the simulator by creating the network, communication instances, and loading network variables.

    Returns:
        tuple: A tuple containing the initialized network, communication instance, and the loaded network variables.
    """
    show_error = None
    for_testing = True if 'pytest' in sys.modules else False
    while True:
        try:
            logger.debug("Loading network variables")
            network_variables = load_network_variables()
            exitButtonPressed = MainMenu.menu(network_variables, show_error)

            if exitButtonPressed:
                if for_testing:
                    return None, None, None
                else:
                    sys.exit()

            network = initializationModule.Initialization(network_variables)

            comm = communication.Communication(network)
            logger.debug("Network and Communication objects created")
            return network, comm, network_variables

        except ParseTopologyFileError as e:
            logger.error(e)
            show_error = e.message
            continue
        except Exception as e:
            logger.error("An error occurred during network initialization: %s" % e)
            break



def runSimulator(network: initializationModule.Initialization, comm: communication.Communication,
                 network_variables: dict, start_time, for_testing=False):
    """
    Runs the simulator based on user-provided network configuration and algorithm.
    
    Args:
        network (initializationModule.Initialization): The initialized network object.
        comm (communication.Communication): The communication object handling network communication.
        network_variables (dict): Dictionary of network parameters.
        start_time (float): The time when the simulation started.

    Returns:
        None
    """
    net_creation_time = time.time() - start_time
    algorithm_run_time = 0  # Initialize to avoid UnboundLocalError

    if network_variables['Display'] == "Graph":
        app = QApplication(sys.argv)
        graphVisualization.visualize_network(network, comm)
        if for_testing:
            # Run synchronously for testing control
            runModule.initiateRun(network, comm, network_variables['Sync'])
            QTimer.singleShot(0, app.quit)
            app.exec_()  # Let GUI run
        else:
            thread = threading.Thread(target=runModule.initiateRun, args=(network, comm, network_variables['Sync']))
            thread.start()
            thread.join()
            sys.exit(app.exec_())
    else:
        runModule.initiateRun(network, comm, network_variables['Sync'])
        algorithm_run_time = time.time() - start_time - net_creation_time

    logger.summary("--- Total Simulation Time : %s seconds ---" % (time.time() - start_time))
    logger.summary("--- Net Creation Time : %s seconds ---" % (net_creation_time))
    logger.summary("--- Algorithm Run Time : %s seconds ---" % (algorithm_run_time))


def main():
    """
    Main entry point for the simulator. Redirects standard output to a log file and runs the simulator.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--testing", action="store_true")
    args = parser.parse_args()
    if args.debug:
        loggerConfig.output_debug()

    #sys.stdout = open(OUTPUT_FILE, "w")
    logger.info("Starting the simulator")
    logger.debug("check if print to console")
    start_time = time.time()
    network, comm, network_variables = initializeSimulator()
    runSimulator(network, comm, network_variables, start_time, args.testing)
    
    if args.testing:
        return network, comm, network_variables


if __name__ == "__main__":
    main()

#sdfsdfs