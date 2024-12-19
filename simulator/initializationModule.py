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

from simulator.computer import Computer
from simulator.data_structures.union_find import UnionFind
from simulator.data_structures.custom_min_heap import CustomMinHeap
from simulator.data_structures.custom_set import CustomSet
from simulator.data_structures.custom_dict import CustomDict


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
        ## if network_variables.topology_file
        ##      self.parse_topology_file(file_path)
        ##      self.build toplogy
        ##      self.root_selection()
        ## else:
        ##    self.update_network_variables(network_variables)
        ##


        self.update_network_variables(network_variables)

        # use in custom
        self.connected_computers = [Computer() for _ in range(self.computer_number)]

        if network_variables['Sync'] == "Sync":
            self.message_queue = CustomDict()
        else:
            # always
            self.message_queue = CustomMinHeap()


        self.node_values_change = []  # for graph display
        self.edges_delays = {}  # holds the delays of each edge in the network

        # no use in custom
        self.create_computer_ids()

        # always
        self.network_dict = {}
        for comp in self.connected_computers:
            self.network_dict[comp.id] = comp

        # no use in custom
        self.root_selection()
        self.create_connected_computers()

        # always
        self.load_algorithms(self.algorithm_path)

        # self.delays_creation() # used for creating delays for edges, not used in current version

        # always
        for comp in self.connected_computers:  # resets the changed flag
            comp.reset_flag()

    def parse_topology_file(self, file_path):
        """
        Parses a topology file to create the network topology.

        Args:
            file_path (str): The file path to the topology file.
        """
        with open(file_path, 'r') as f:
            lines = f.readlines()
        #self.topologyType = 'Custom'

        ## read lines in file and parse into network variables



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
        Loads the network algorithms for each computer from the specified path.

        Args:
            algorithm_module_path (str): The file path to the algorithm module.
        """
        if algorithm_module_path == 'no_alg_provided':
            print("No algorithm was provided")
            exit()

        try:
            directory, file_name = os.path.split(algorithm_module_path)
            base_file_name, _ = os.path.splitext(file_name)
            sys.path.insert(0, directory)

            algorithm_module = importlib.import_module(base_file_name)
            for comp in self.connected_computers:
                comp.algorithm_file = algorithm_module

        except ImportError:
            print(f"Error: Unable to import {base_file_name}.py")
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
