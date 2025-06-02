"""
Network Initialization and Topology Creation for Distributed Networks.

This module contains classes and functions used to initialize and configure a simulated network
using different topologies (Tree, Star, Line, Clique, etc.). The module also handles network algorithms,
computer ID assignments, and delay creation for network edges.
"""
import importlib
import os
import random
import sys
import math
from utils.logger_config import logger
from simulator.computer import Computer
from simulator.data_structures.union_find import UnionFind
from simulator.data_structures.custom_min_heap import CustomMinHeap
from simulator.data_structures.custom_set import CustomSet
from simulator.data_structures.custom_dict import CustomDict
from utils.exceptions import *
from simulator.errorModule import CollapseConfig


class Initialization:
    """
    Initialization class for setting up network parameters and topologies.

    Attributes:
        network_variables (dict): The dictionary containing network configuration data.
        connected_computers (list): A list of Computer objects representing network nodes.
        message_queue (CustomMinHeap): A custom min-heap for message management.
        node_values_change (list): A list for tracking changes in node values for display.
        edges_delays (dict): A dictionary of delays associated with network edges.
        network_dict (dict): A dictionary mapping computer IDs to Computer objects.
    """

    def __init__(self, network_variables):
        """
        Initializes the network by setting parameters and creating computers and topologies.

        Args:
            network_variables (dict): The network configuration dictionary.
        """
        if network_variables['Topology File'] != '':
            self.parse_topology_file(network_variables['Topology File'], network_variables)
        else:
            self.update_network_variables(network_variables)
            self.connected_computers = [Computer() for _ in range(self.computer_number)]
            self.create_computer_ids()
            self.root_selection()
            self.create_connected_computers()
            self.network_dict = {comp.id: comp for comp in self.connected_computers}

        # always
        self.message_queue = CustomDict() if network_variables['Sync'] == "Sync" else CustomMinHeap()
        self.node_values_change = []  # for graph display
        self.edges_delays = {}  # holds the delays of each edge in the network
        self.collapse_config = None
        self.load_algorithms(self.algorithm_path)

        for comp in self.connected_computers:  # resets the changed flag
            comp.reset_flag()

        # self.delays_creation() # used for creating delays for edges, not used in current version

    def parse_topology_file(self, file_path, network_variables):
        """
        Parses a topology file to create the network topology.

        Args:
            file_path (str): The file path to the topology file.
        """
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                logger.debug(f"Reading topology file {file_path}")
                logger.debug(f"File contents: {lines}")

            section = None
            ids_set = set()
            edges_set = set()
            num_computers = 0
            root_id = None
            input_names = []
            ids_inputs = []

            for line in lines:
                line = line.strip()
                if line.endswith(':'):
                    section = line[:-1].lower().replace(' ', '_')
                elif section == "ids_list":
                    for new_id in map(int, line.split(',')):
                        ids_set.add(new_id)  # Add to set; duplicates are ignored
                elif section == "number_of_computers":
                    num_computers = int(line)

                elif section == "root_id":
                    root_values = line.split(',')
                    if len(root_values) > 1:
                        raise ParseTopologyFileError(f"Multiple roots detected: {root_values}")
                    root_value = root_values[0].strip()  # Get the single root value
                    if root_value.lower() == "random":
                        root_id = "random"
                    else:
                        try:
                            root_id = int(root_value)  # Try to convert it to an integer
                        except ValueError:
                            raise ParseTopologyFileError(
                                f"Invalid root ID: {root_value}. Must be 'random' or an integer.")

                elif section == "edges":
                    edges = line.replace('(', '').replace(')', '').split(',')
                    for i in range(0, len(edges), 2):
                        u, v = int(edges[i]), int(edges[i + 1])
                        # Validate that both IDs exist in ids_set
                        if u not in ids_set or v not in ids_set:
                            raise ParseTopologyFileError(f"Edge ({u}, {v}) contains ID(s) not in ids_list")
                        # Add edge to edges_set in a consistent order to avoid duplicates
                        edges_set.add((min(u, v), max(u, v)))

                # Input:
                # [height,weight]
                # 1:[11,11],2:[22,22],3:[33,33],4:[44,44],5:[55,55]
                elif section == "input":
                    if line.startswith('[') and line.endswith(']'):
                        input_names = line[1:-1].split(',')
                        logger.debug(f"Attribute names: {input_names}")
                    else:
                        ids_inputs = line.split('],')
                        logger.debug(f"ID attributes: {ids_inputs}")

            logger.info(f"Topology file {file_path} parsed successfully.")
            logger.debug(f"IDs: {ids_set}")
            logger.debug(f"Number of computers: {num_computers}")
            logger.debug(f"Root ID: {root_id}")
            logger.debug(f"Edges: {edges_set}")
            logger.debug(f"Attributes: {input_names}")

            if len(ids_set) != num_computers:
                raise ParseTopologyFileError("The number of computers does not match the number of IDs provided.")

            self.computer_number = num_computers
            self.connected_computers = [Computer(new_id=new_id) for new_id in ids_set]
            self.network_dict = {comp.id: comp for comp in self.connected_computers}

            if isinstance(root_id, str) and root_id.lower() == "random":
                selected_computer = random.choice(self.connected_computers)
                selected_computer.is_root = True
            else:
                selected_computer = self.network_dict.get(root_id)
                if selected_computer is None:
                    raise ParseTopologyFileError(f"Root ID {root_id} not found in ids_list")
                selected_computer.is_root = True

            for u, v in edges_set:
                self.network_dict[u].connectedEdges.append(v)
                self.network_dict[v].connectedEdges.append(u)

            for id_input in ids_inputs:
                id_str, attr_str = id_input.split(':')
                logger.debug(f"ID: {id_str}, Inputs: {attr_str}")
                id = int(id_str)
                if id not in ids_set:
                    raise ParseTopologyFileError(f"ID {id} not found in ids_list when parsing input")
                attr_str = attr_str.strip('[]').split(',')
                logger.debug(f"Inputs for ID {id}: {attr_str}")
                if len(attr_str) > len(input_names):
                    raise ParseTopologyFileError(
                        f"Number of Inputs does not match the number of Input names on ID {id}")

                for name, value in zip(input_names, attr_str):
                    self.network_dict[id].inputs[name.strip()] = value
                    logger.info(f"ID {id} has input {name.strip()} with value {value}")

            self.topologyType = 'Custom'
            self.id_type = 'Custom'
            self.display_type = network_variables.get('Display', 'Text')
            self.root_type = root_id
            self.delay_type = network_variables.get('Delay', 'Random')
            self.algorithm_path = network_variables.get('Algorithm', 'no_alg_provided')
            self.logging_type = network_variables.get('Logging', 'Short')
            self.sync = network_variables.get('Sync')

            # check if graph is connected if not return to main menu
            connected = self.is_connected()
            if not connected:
                raise ParseTopologyFileError("The network is not connected. Please connect the network and try again.")
        except ParseTopologyFileError as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.debug(f"Error parsing topology file: {e}")
            raise ParseTopologyFileError(f"Error parsing topology file, please check the file format and try again")

    def update_network_variables(self, network_variables_data):
        """
        Updates network parameters from the given configuration dictionary.
        
        Args:
            network_variables_data (dict): The dictionary containing network configuration data.
        """
        self.computer_number = int(network_variables_data.get('Number of Computers', 10))
        self.topologyType = network_variables_data.get('Topology', 'Line')
        self.id_type = network_variables_data.get('ID Type', 'Sequential')
        self.display_type = network_variables_data.get('Display', 'Text')
        self.root_type = network_variables_data.get('Root', 'Random')
        self.delay_type = network_variables_data.get('Delay', 'Random')
        self.algorithm_path = network_variables_data.get('Algorithm', 'no_alg_provided')
        self.logging_type = network_variables_data.get('Logging', 'Short')
        self.sync = network_variables_data.get('Sync')

    def __str__(self) -> list:
        """
        Provides a string representation of the network configuration and connected computers.
        
        Returns:
            str: The string representation of the network.
        """
        result = [
            f"Number of Computers: {self.computer_number}",
            f"Topology: {self.topologyType}",
            f"ID Type: {self.id_type}",
            f"Display Type: {self.display_type}",
            f"Root Type: {self.root_type}",
            f"Algorithm Path: {self.algorithm_path}",
            f"Logging Type: {self.logging_type}",
        ]

        result.append("\nComputers:")
        result.extend(str(comp) for comp in self.connected_computers)

        return "\n".join(result)

    # used for creating delays for edges, not used in current version     
    """ def delays_creation(self):
        delay_functions = {
        "Random": self.random_delay,
        "Constant": self.constant_delay,
        }
        id_function = delay_functions[self.delay_type]
        id_function()
            
    # Creates random delay for every edge
    def random_delay(self):
        for comp in self.connected_computers:
            comp.delays = [None] * len(comp.connectedEdges)
            for i, connected in enumerate(comp.connectedEdges):
                edge_tuple = (comp.id, connected) if comp.id < connected else (connected, comp.id) # unique representation of the edge as a tuple
                
                if edge_tuple not in self.edges_delays: # if not already in edgesDelays, generate a random delay, and insert into edgesDelays
                    random_num = random.random()
                    self.edges_delays[edge_tuple] = random_num
                
                comp.delays[i] = self.edges_delays[edge_tuple]
                
    # Creates constant delay for every edge
    def constant_delay(self):
        for comp in self.connected_computers:
            comp.delays = [None] * len(comp.connectedEdges)
            for i, connected in enumerate(comp.connectedEdges):
                edge_tuple = (comp.id, connected) if comp.id < connected else (connected, comp.id) # unique representation of the edge as a tuple
                
                if edge_tuple not in self.edges_delays: # if not already in edgesDelays, generate a delay of 1 and insert into edgesDelays
                    self.edges_delays[edge_tuple] =1
                
                comp.delays[i] = self.edges_delays[edge_tuple] """

    def create_connected_computers(self):
        """
        Creates the network topology based on the specified topology type and configuration.
        """
        topology_functions = {
            "Random": self.create_random_topology,
            "Line": self.create_line_topology,
            "Clique": self.create_clique_topology,
            "Tree": self.create_tree_topology,
            "Star": self.create_star_topology,
        }

        topology_function = topology_functions[self.topologyType]

        # check network connectivity
        connected = False
        while not connected:
            topology_function()
            connected = self.is_connected()

    def is_connected(self):
        """
        Checks if the network is connected by using Union-Find.

        Returns:
            bool: True if the network is connected, False otherwise.
        """
        uf = UnionFind(len(self.connected_computers))

        for node in self.connected_computers:
            for neighbor in node.connectedEdges:
                uf.union(self.connected_computers.index(node),
                         self.connected_computers.index(self.find_computer(neighbor)))

        root = uf.find(0)
        return all(uf.find(i) == root for i in range(len(self.connected_computers)))

    def create_computer_ids(self):
        """
        Creates IDs for the computers in the network based on the selected ID type.
        """
        id_functions = {
            "Random": self.create_random_ids,
            "Sequential": self.create_sequential_ids,
        }

        id_function = id_functions[self.id_type]
        id_function()

    def create_random_ids(self):
        """
        Creates random, unique IDs for the computers.
        """
        used_ids = set()
        for comp in self.connected_computers:
            comp_id = random.randint(100, 100 * self.computer_number - 1)
            while comp_id in used_ids:
                comp_id = random.randint(100, 100 * self.computer_number - 1)
            comp.id = comp_id
            used_ids.add(comp_id)

        # Sort the connected_computers list by their ids after assigning them
        self.connected_computers.sort(key=lambda x: x.id)

    def create_sequential_ids(self):
        """
        Creates sequential IDs for the computers.
        """
        for i, comp in enumerate(self.connected_computers):
            comp.id = i

    def create_random_topology(self):
        """
        Creates a random topology for the network.
        """
        ids_list = [comp.id for comp in self.connected_computers]

        if len(self.connected_computers) == 2:
            # Connect the first computer to the second
            self.connected_computers[0].connectedEdges.append(self.connected_computers[1].id)
            self.connected_computers[1].connectedEdges.append(self.connected_computers[0].id)

        elif len(self.connected_computers) == 3:
            # All possible connected graphs for 3 nodes
            connected_graphs = [
                [(0, 1), (1, 2)],
                [(0, 1), (0, 2)],
                [(0, 2), (1, 2)],
                [(0, 1), (1, 2), (0, 2)]
            ]

            # Choose one random connected graph
            chosen_edges = random.choice(connected_graphs)

            # Create the connections based on the chosen graph
            for u, v in chosen_edges:
                self.connected_computers[u].connectedEdges.append(self.connected_computers[v].id)
                self.connected_computers[v].connectedEdges.append(self.connected_computers[u].id)

        else:
            for i, comp in enumerate(self.connected_computers):
                # Determine a random number of edges (between 1 and 2 * log(computer_number - 1))
                num_edges = random.randint(1, 2 * int(math.log(self.computer_number - 1)))
                # Choose num_edges unique vertices (excluding comp.id)
                connected_to_vertices = random.sample([j for j in ids_list if j != comp.id], num_edges)

                # Add connections
                comp.connectedEdges.extend(connected_to_vertices)

                # Ensure bi-directional connection
                for connected_to_id in connected_to_vertices:
                    for comp_other in self.connected_computers:
                        if comp_other.id == connected_to_id:
                            comp_other.connectedEdges.append(comp.id)
                            break

            # Remove duplicates
            for comp in self.connected_computers:
                comp.connectedEdges = sorted(list(set(comp.connectedEdges)))

        # Sort the connected_computers list by their ids (optional, if needed)
        self.connected_computers.sort(key=lambda x: x.id)

    def create_line_topology(self):
        """
        Creates a line topology for the network, where each computer is connected to the next one in sequence.
        """
        for i in range(self.computer_number - 1):
            # Connect each computer to the next one in line
            self.connected_computers[i].connectedEdges.append(self.connected_computers[i + 1].id)
            self.connected_computers[i + 1].connectedEdges.append(
                self.connected_computers[i].id)  # Ensure bi-directional connection

    def create_clique_topology(self):
        """
        Creates a clique topology for the network, where each computer is connected to every other computer.
        """
        # Connect each computer to every other computer
        for i in range(self.computer_number):
            for j in range(i + 1, self.computer_number):
                # Ensure bi-directional connection
                self.connected_computers[i].connectedEdges.append(self.connected_computers[j].id)
                self.connected_computers[j].connectedEdges.append(self.connected_computers[i].id)

        # Removing duplicates
        for comp in self.connected_computers:
            comp.connectedEdges = list(set(comp.connectedEdges))

    def create_tree_topology(self):
        """
        Creates a tree topology for the network using a randomly generated Prüfer sequence.
        """
        # Generate a Prüfer sequence
        prufer_sequence = [random.choice(self.connected_computers) for _ in range(self.computer_number - 2)]

        # sort the connected computers by id
        extra_list = sorted(self.connected_computers, key=lambda comp: comp.id)

        # Connect nodes in L with nodes in S
        while len(extra_list) > 2:
            for i in extra_list:
                if len(extra_list) <= 2:
                    break

                if i not in prufer_sequence:
                    j = prufer_sequence[0]  # Always connect to the first node in S
                    i.connectedEdges.append(j.id)
                    j.connectedEdges.append(i.id)
                    prufer_sequence.remove(j)
                    extra_list.remove(i)

        # Connect the last two nodes in L
        if len(extra_list) == 2:
            extra_list[0].connectedEdges.append(extra_list[1].id)
            extra_list[1].connectedEdges.append(extra_list[0].id)

    def create_star_topology(self):
        """
        Creates a star topology for the network, where all computers are connected to a central hub (root node).
        """
        root = None
        for comp in self.connected_computers:
            if getattr(comp, 'is_root', False):
                root = comp
                break
        if root is None:
            root = self.connected_computers[0]

        # Connect all other nodes to the hub
        for comp in self.connected_computers:
            if comp.id != root.id:
                root.connectedEdges.append(comp.id)
                comp.connectedEdges.append(root.id)  # Ensure bi-directional connection

    def load_algorithms(self, algorithm_module_path):
        """
        Loads the network algorithms and collapse configuration for each computer from the specified path.

        Args:
            algorithm_module_path (str): The file path to the algorithm module.
        """
        if algorithm_module_path == 'no_alg_provided':
            logger.error("No algorithm was provided")
            exit()

        try:
            directory, file_name = os.path.split(algorithm_module_path)
            base_file_name, _ = os.path.splitext(file_name)
            sys.path.insert(0, directory)

            algorithm_module = importlib.import_module(base_file_name)
            # print all algorithm module attributes
            logger.debug(f"Algorithm module attributes: {dir(algorithm_module)}")

            # Load collapse configuration if it exists
            collapse_config = None
            if hasattr(algorithm_module, 'collapse_config'):
                collapse_config = getattr(algorithm_module, 'collapse_config')
                logger.debug(f"Found collapse configuration in {base_file_name}: {collapse_config}")
                self.collapse_config = CollapseConfig(collapse_config)

            for comp in self.connected_computers:
                comp.algorithm_file = algorithm_module

        except ImportError:
            logger.error(f"Error: Unable to import {base_file_name}.py")
            return None

    def root_selection(self):
        """
        Selects the root node based on the specified root selection method.
        """
        if self.root_type == "Random":
            selected_computer = random.choice(self.connected_computers)
            selected_computer.is_root = True
        elif self.root_type == "Min ID":
            selected_computer = min(self.connected_computers, key=lambda computer: computer.id)
            selected_computer.is_root = True

    def find_computer(self, id: int) -> Computer:
        """
        Finds a computer in the network by its ID.

        Args:
            id (int): The ID of the computer to find.

        Returns:
            Computer: The computer object with the specified ID, or None if not found.
        """
        for comp in self.connected_computers:
            if comp.id == id:
                return comp
        return None


def main():
    init = Initialization()
    init.toString()


if __name__ == "__main__":
    main()
