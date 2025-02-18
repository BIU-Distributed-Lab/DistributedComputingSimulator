"""
GraphVisualizer module for graphical representation of network simulations.

This module defines the `GraphVisualizer` class, which handles the graphical visualization of a network
using PyQt5 and NetworkX. It includes methods for adding nodes and edges, setting layouts, and handling
user interactions such as zooming and undoing changes.
"""

import os
import networkx as nx

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import simulator.initializationModule as initializationModule
from visualizations.node import Node
from visualizations.edge import Edge
import visualizations.functions as gf
import visualizations.layout_creation as glc


class GraphVisualizer(QWidget):
    """
    A class for visualizing a network of nodes and edges using PyQt5 and NetworkX.

    Attributes:
        network (Initialization): The initialized network object containing the network configuration.
        comm: The communication object handling the messages between network nodes.
        graph (nx.DiGraph): The directed graph representing the network.
        num_nodes (int): The number of nodes in the network.
        nodes_map (dict): A dictionary mapping node names to Node objects.
        nx_layout (dict): A dictionary mapping layout names to NetworkX layout functions.
        change_stack (list): A list to keep track of changes for undo functionality.
        scene (QGraphicsScene): The scene for displaying the nodes and edges.
        view (QGraphicsView): The view that displays the scene.
        graph_scale (int): The scaling factor for the graph visualization.
        zoom_factor (float): The factor by which to zoom in and out.
        zoom_step (float): The amount to zoom in or out on each wheel event.
    """

    def __init__(self, network: initializationModule.Initialization, comm, parent=None):
        """
        Initializes the GraphVisualizer with the given network and communication objects.

        Args:
            network (Initialization): The initialized network object.
            comm: The communication object handling message passing in the network.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("Simulator for Distributed Networks")

        self.change_stack = []  # used for "undo" button press

        self.network = network
        self.comm = comm
        self.graph = nx.DiGraph()
        self.num_nodes = self.network.computer_number
        self.nodes_map = {} # A dictionary mapping node names to Node objects (Str -> Node).
        self.nx_layout = {"circular": nx.circular_layout, "random": nx.random_layout,} # A dictionary mapping layout names to NetworkX layout functions.
        
        self.init_graph()
        self.init_ui()


    def init_graph(self):
        """
        Initializes the graph by adding nodes and edges based on the network configuration.
        """
        self.add_nodes_to_graph()
        self.add_edges_to_graph()

    def add_nodes_to_graph(self):
        """
        Adds nodes to the graph based on the connected computers in the network.
        """
        vertex_names = [str(comp.id) for comp in self.network.connected_computers]
        self.graph.add_nodes_from(vertex_names)
            
    def add_edges_to_graph(self):
        """
        Adds edges to the graph based on the connections between computers in the network.
        """
        for comp in self.network.connected_computers:
            for connected in comp.connectedEdges:
                self.graph.add_edge(str(comp.id), str(connected))

    def init_ui(self):
        """
        Initializes the UI components, including the scene, view, and layouts for displaying the graph.
        """
        self.scene = QGraphicsScene()  # manages and organizes the items that make up the visualization.
        self.view = QGraphicsView(self.scene) # visual display for the scene.
        self.graph_scale = 200
        self.load_graph()
        self.set_nx_layout("circular")
        self.zoom_factor = 1.15
        self.zoom_step = 1.1
        self.view.wheelEvent = self.wheelEvent
        self.layoutCreation()
        
    def get_nx_layouts(self) -> list:
        """
        Returns the available NetworkX layouts as a list.

        Returns:
            list: The available layout names.
        """
        return self.nx_layout.keys()

    def set_nx_layout(self, name: str):
        """
        Sets the NetworkX layout for the graph visualization based on the layout name.

        Args:
            name (str): The name of the layout to set (e.g., 'circular', 'random').
        """
        self.nx_layout_function = self.nx_layout[name]
        positions = self.nx_layout_function(self.graph)
        
        if self.graph.number_of_nodes() > 200:
            glc.set_nx_layout_large_graph(self, positions)
        elif name == "circular":
            glc.set_nx_layout_circular_graph(self, positions)
        else:  # random layout with not a lot of nodes
            glc.set_nx_layout_random_small_graph(self, name, positions)

            
    def load_graph(self):
        """
        Loads the graph into the QGraphicsScene using Node and Edge classes to represent nodes and connections.
        """
        self.scene.clear()
        self.nodes_map.clear()

        # add nodes
        for node in self.graph:
            item = Node(node, self.num_nodes, self.network)
            self.scene.addItem(item)
            self.nodes_map[node] = item

        # add edges
        for a, b in self.graph.edges:
            source = self.nodes_map[a]
            dest = self.nodes_map[b]
            self.scene.addItem(Edge(source, dest))


    def layoutCreation(self):
        """
        Calls the layout creation function to arrange nodes in the graph.
        """
        glc.layoutCreation(self)

    def wheelEvent(self, event):
        """
        Handles the zoom functionality based on mouse wheel events.

        Args:
            event (QWheelEvent): The event object containing the wheel movement data.
        """
        gf.wheelEvent(self, event)

    def regenarate_clicked(self):
        """
        Handles the regeneration of the graph layout when the 'regenerate' button is clicked.
        """
        gf.regenarate_clicked(self)

    def toggle_timer(self):
        """
        Toggles the simulation timer based on the 'run_checkbox' state.
        """
        gf.toggle_timer(self)

    def update_timer_interval(self):
        """
        Updates the timer interval based on the value of the slider.
        """
        gf.update_timer_interval(self)

    def update_slider_label(self):
        """
        Updates the label displaying the interval time for the simulation slider.
        """
        gf.update_slider_label(self)

    def undo_change(self):
        """
        Undoes the last change made to the graph (e.g., node color changes).
        """
        gf.undo_change(self)

    def reset(self):
        """
        Resets the graph to its initial state, undoing all changes.
        """
        gf.reset(self)
        
    def change_node_color(self, times):
        """
        Changes the color of nodes based on the current state of the network.

        Args:
            times (int): The number of times to change the node color.
        """
        try:
            sync = self.network.sync == "Sync"
            gf.change_node_color(self, times, sync)
        except Exception as e:
            print(e)
        
    def update_node_color(self, node_name, values_change_dict):
        """
        Updates the color and state of a specific node in the graph.

        Args:
            node_name (str): The name of the node to update.
            values_change_dict (dict): The dictionary containing updated node values.
        """
        gf.update_node_color(self, node_name, values_change_dict)


def visualize_network(network: initializationModule.Initialization, comm):
    """
    Visualizes the network using the GraphVisualizer class.

    Args:
        network (Initialization): The initialized network object.
        comm: The communication object handling message passing in the network.
    """
    graph_window = GraphVisualizer(network, comm)
    stylesheet_file = os.path.join('./designFiles', 'graph_window.qss')
    with open(stylesheet_file, 'r') as f:
        graph_window.setStyleSheet(f.read())
    graph_window.setWindowIcon(QIcon('./designFiles/app_icon.jpeg'))

    graph_window.show()
    graph_window.resize(1000, 800)
    
