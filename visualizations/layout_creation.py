"""
Layout creation and visualization module for network graph.

This module defines functions for creating and updating the layout of a network graph in a graphical
interface using PyQt5. It supports various layouts such as circular, random, and customized layouts
for small and large graphs.
"""

import math
import random

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer, QPointF

from visualizations.edge import Edge


# Define the normal and pressed styles
normal_button_style = """
    QPushButton {
        padding: 5px; 
        font-size: 14px; 
        background-color: lightblue;
    }
"""
pressed_button_style = """
    QPushButton {
        padding: 5px; 
        font-size: 14px; 
        background-color: darkblue;
        color: white;
    }
"""


def set_button_style(button, normal_style, pressed_style):
    button.setStyleSheet(normal_style)
    button.pressed.connect(lambda: button.setStyleSheet(pressed_style))
    button.released.connect(lambda: button.setStyleSheet(normal_style))




def layoutCreation(self):
    """
    Create and configure the graph visualization layout.

    This function initializes the layout, including combo boxes for layout selection, buttons for
    controlling the simulation (e.g., 'regenerate', 'next phase', 'reset'), sliders for adjusting timer intervals,
    and other UI elements for controlling the graph.
    """

    self.choice_combo = QComboBox()
    self.choice_combo.addItems(self.get_nx_layouts())
    self.choice_combo.currentTextChanged.connect(self.set_nx_layout)

    # self.regenarate_button = QPushButton("regenarate")
    # self.regenarate_button.clicked.connect(self.regenarate_clicked)

    main_layout = QVBoxLayout(self)
    # main_layout.addWidget(self.choice_combo)
    # main_layout.addWidget(self.regenarate_button)
    main_layout.addWidget(self.view)

    slider_h_layout = QHBoxLayout()

    self.slider = QSlider(Qt.Horizontal)
    self.slider.setRange(-2000, -1)
    self.slider.setValue(-1000)
    self.slider.valueChanged.connect(self.update_timer_interval)

    self.slider_label = QLabel(f"{abs(self.slider.value() / 1000)} seconds per tick")
    self.slider.valueChanged.connect(self.update_slider_label)

    self.timer = QTimer(self)
    self.timer.timeout.connect(lambda: self.change_node_color(1))

    self.run_checkbox = QCheckBox()
    self.run_checkbox.stateChanged.connect(self.toggle_timer)
    run_label = QLabel("Run")
    slider_h_layout.addWidget(self.run_checkbox)
    slider_h_layout.addWidget(run_label)
    slider_h_layout.addWidget(self.slider)
    slider_h_layout.addWidget(self.slider_label)

    buttons_layout = QGridLayout()


    # Add a label to show what happened in the last phase
    #self.last_phase_label = QLabel("Last phase: None")
    #buttons_layout.addWidget(self.last_phase_label, 0, 0, 1, 2)

    self.next_phase_button = QPushButton("Next Phase")
    self.next_phase_button.setFixedSize(300, 40)
    set_button_style(self.next_phase_button, normal_button_style, pressed_button_style)
    self.next_phase_button.clicked.connect(lambda: self.change_node_color(1))

    self.next_5_phase_button = QPushButton("Next 5 Phases")
    self.next_5_phase_button.setFixedSize(300, 40)
    set_button_style(self.next_5_phase_button, normal_button_style, pressed_button_style)
    self.next_5_phase_button.clicked.connect(lambda: self.change_node_color(5))

    self.undo_button = QPushButton('Undo', self)
    self.undo_button.setFixedSize(300, 40)
    set_button_style(self.undo_button, normal_button_style, pressed_button_style)
    self.undo_button.clicked.connect(self.undo_change)

    self.reset_button = QPushButton('Reset', self)
    self.reset_button.setFixedSize(300, 40)
    set_button_style(self.reset_button, normal_button_style, pressed_button_style)
    self.reset_button.clicked.connect(self.reset)

    buttons_layout.addWidget(self.slider_label, 0, 0, 1, 2)  # Move slider label above the line
    buttons_layout.addWidget(self.next_phase_button, 1, 0)
    buttons_layout.addWidget(self.next_5_phase_button, 1, 1)
    buttons_layout.addWidget(self.undo_button, 2, 0)
    buttons_layout.addWidget(self.reset_button, 2, 1)

    # Add the horizontal layouts to the main layout
    main_layout.addLayout(slider_h_layout)
    main_layout.addLayout(buttons_layout)
    
    
    
def set_nx_layout_large_graph(self, positions):
    """
    Set a layout for large graphs (number of nodes > 200).

    This function positions nodes randomly within the window bounds, and sets lower boldness for edges to handle larger graphs.

    Args:
        positions (dict): Dictionary of node positions in the layout.
    """
    for node, pos in positions.items():
        window_size = self.size()
        item = self.nodes_map[node]
        x = random.randint(item.radius, window_size.width() - item.radius)
        y = random.randint(item.radius, window_size.height() - item.radius)
        item.setPos(QPointF(x, y))

    for edge in self.scene.items():
        if isinstance(edge, Edge):
            edge.boldness = -1
            edge.update()
                
                
def set_nx_layout_circular_graph(self, positions):
    """
    Set a circular layout for the graph.

    This function positions nodes in a circular pattern based on the layout positions provided.

    Args:
        positions (dict): Dictionary of node positions in the layout.
    """
    for node, pos in positions.items():
        x, y = pos
        x *= self.graph_scale
        y *= self.graph_scale
        item = self.nodes_map[node]
        item.setPos(QPointF(x, y))

            

def set_nx_layout_random_small_graph(self, name, positions):
    """
    Set a random layout for smaller graphs (number of nodes <= 200).

    This function ensures that nodes are spaced apart by adjusting their positions iteratively to prevent overlaps.

    Args:
        name (str): The name of the layout.
        positions (dict): Dictionary of node positions in the layout.
    """
    if name in self.nx_layout and self.nx_layout[name] is not None:
        item_radius = next(iter(self.nodes_map.values())).radius
        threshold_distance = 2 * item_radius / self.graph_scale

        # compute node position from layout function
        locations = {node: (pos[0], pos[1]) for node, pos in positions.items()}  # holds position for each node

        changed = True
        while changed:
            changed = False
            for node, pos in positions.items():
                x, y = pos
                # adjust position if it overlaps with existing nodes
                for _, loc in locations.items():
                    x2, y2 = loc
                    distance = math.sqrt((x2 - x) ** 2 + (y2 - y) ** 2)
                    if distance < threshold_distance and x != x2 and y != y2:
                        angle = math.atan2(y2 - y, x2 - x)
                        x += 5 * threshold_distance * math.cos(angle)
                        y += 5 * threshold_distance * math.sin(angle)
                        changed = True
                        break

                locations[node] = (x, y)

                # scale x,y
                x_scaled = x * self.graph_scale
                y_scaled = y * self.graph_scale

                # Set the position for the node
                item = self.nodes_map[node]
                item.setPos(QPointF(x_scaled, y_scaled))

                # update positions
                if changed:
                    for node, (x, y) in positions.items():
                        new_x, new_y = locations[node]
                        positions[node] = (new_x, new_y)
                    break
