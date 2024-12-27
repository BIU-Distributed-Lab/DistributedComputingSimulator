"""
Main menu module for the Distributed Networks Simulator.

This module defines the PyQt5-based GUI for configuring network simulation settings, including
choosing a topology, specifying the number of computers, uploading algorithms, and setting other parameters.
"""

import json
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
from utils.logger_config import logger
# Constants 
NETWORK_VARIABLES = 'network_variables.json'
CHECKBOX_LAYOUT_GEOMETRY = (800, 90, 500, 800)
COMBOBOX_OPTIONS = {
    "Sync": "Sync, Async",
    "Topology": "Random, Clique, Line, Tree, Star, Custom",
    "ID Type": "Random, Sequential, Custom",
    "Delay": "Random, Constant",
    "Display": "Text, Graph",
    "Root": "No Root, Min ID, Random, Custom",
    "Logging": "Short, Medium, Long",
}


class SimulationInProgressWindow(QMainWindow):
    """
    A class representing the window that appears when the simulation is in progress.
    """

    def __init__(self):
        """
        Initialize the SimulationInProgressWindow.
        """
        super().__init__()
        self.setGeometry(0, 0, 800, 600)
        self.setWindowTitle("Simulation In Process")


class MenuWindow(QMainWindow):
    """
    The main menu window for configuring and running the network simulation.

    Attributes:
        checkbox_values (dict): A dictionary to store selected values for network variables.
        label_values (dict): A dictionary to store QLabel widgets for displaying selected values.
    """

    def __init__(self, network_variables_data):
        """
        Initialize the menu window with the provided network variables.
        
        Args:
            network_variables_data (dict): The initial network variable values.
        """
        super().__init__()
        ##self.network_variables_file = network_variables_file
        self.combo_boxes = {}
        self.checkbox_values = network_variables_data # Dictionary to store checkbox values with default values
        self.setGeometry(0, 0, 1500, 900)
        self.setWindowTitle("Simulator for Distributed Networks")
        self.init_ui()
        
    def init_ui(self):
        """
        Initialize the UI components, including labels, buttons, and input options.
        """
        self.label_values = {}  
        self.create_labels()
        self.create_buttons()
        self.create_options()
        self.submit_button.setEnabled(True)

    def update_value(self, key: str, value: str):
        """
        Update the value of the specified label and save it in the checkbox_values dictionary.

        Args:
            key (str): The key to update.
            value (str): The value to set.
        """
        self.checkbox_values[key] = value
        if key == "Number of Computers":
            self.validate_number_input(value)
        elif key == "Display":
            self.validate_display_type()

        if key in self.label_values:
            self.label_values[key].setText(f"{key}: <span style='color: blue;'>{value}</span>")
            self.label_values[key].setWordWrap(True)


    def create_labels(self):
        """
        Create labels for displaying the network variable values.
        """
        y_offset = 300
        for key, value in self.checkbox_values.items():
            label = QLabel(f"{key}: <span style='color: blue;'>{value}</span>", self)
            label.setGeometry(50, y_offset, 1000, 30)
            y_offset += 62
            self.label_values[key] = label
            self.label_values[key].setWordWrap(True)

        title_label = QLabel(self)
        title_label.setText("Distributed Simulator Project")
        title_label.move(500, 25)
        title_label.resize(450, 40)

        info_label = QLabel(self)
        info_label.setText("Please upload your Python algorithm file:")
        info_label.move(50, 100)
        info_label.resize(650, 50)
        info_label.setStyleSheet("color: blue;")  # Set the color of the info label to blue

        info_label = QLabel(self)
        info_label.setText("Please upload your topology file:")
        info_label.move(50, 200)
        info_label.resize(650, 50)
        info_label.setStyleSheet("color: blue;")  # Set the color of the info label to blue

    def get_button_color(self,button):
        palette = button.palette()
        color = palette.color(QPalette.Button)
        return color.name()  # Returns the color in hex format, e.g., "#f0f0f0"

    def create_buttons(self):
        """
        Create buttons for uploading a Python file and submitting the form.
        """
        upload_algorithm_file_button = QPushButton("Upload Python File", self)
        upload_algorithm_file_button.setGeometry(50, 150, 200, 30)
        upload_algorithm_file_button.clicked.connect(lambda: self.on_upload_algorithm())

        upload__topology_file_button = QPushButton("Upload Topology File", self)
        upload__topology_file_button.setGeometry(50, 250, 200, 30)
        upload__topology_file_button.clicked.connect(lambda: self.on_upload_topology())

        trash_button = QPushButton("Reset", self)
        trash_button.setGeometry(260, 250, 30, 30)
        trash_button.clicked.connect(lambda: self.on_delete_topology_file())


        self.submit_button = QPushButton("Submit", self) 
        self.submit_button.setGeometry(550, 900, 150, 30)
        self.submit_button.clicked.connect(lambda: self.on_submit_all())



    def create_options(self):
        """
        Create options using combo boxes and number input for configuring network variables.
        """
        checkbox_layout = QVBoxLayout()
        
        self.add_number_input(checkbox_layout)  # adding the number of computers option

        for key, options in COMBOBOX_OPTIONS.items():
            self.add_combo_box(checkbox_layout, key, options)

        checkbox_layout.setSpacing(20)
        checkbox_widget = QWidget(self)
        checkbox_widget.setLayout(checkbox_layout)
        checkbox_widget.setGeometry(*CHECKBOX_LAYOUT_GEOMETRY)


    def add_number_input(self, layout):
        """
        Add a number input field to the layout for entering the number of computers.

        Args:
            layout (QVBoxLayout): The layout to add the number input to.
        """
        number_label = QLabel("Number of Computers", self)
        layout.addWidget(number_label)

        self.number_input = QLineEdit(self)
        self.number_input.setPlaceholderText("Enter a number")
        layout.addWidget(self.number_input)

        # Initially disable the submit button
        self.submit_button.setEnabled(False)

        # Connect textChanged signal to validation logic
        self.number_input.textChanged.connect(lambda value: self.update_value("Number of Computers", value))

    def validate_number_input(self, value):
        """
        Validate the number input and enable/disable the submit button.

        Args:
            value (str): The input value to validate.
        """
        if value.isdigit():
            number = int(value)
            self.checkbox_values["Number of Computers"] = number
            self.validate_display_type()
        else:
            self.submit_button.setEnabled(False)
    
    def validate_display_type(self):
        """
        Validate the display type based on the number of computers selected.
        """
        number_of_computers = int(self.checkbox_values.get("Number of Computers", 0))
        display_type = self.checkbox_values.get("Display", "")
        
        if number_of_computers > 500 and display_type != "Text":
            QMessageBox.warning(self, 'Error', 'The number of computers cannot exceed 500 unless the display is set to Text. You will be able to submit only if you choose Text output!', QMessageBox.Ok)
            self.submit_button.setEnabled(False)
        else:
            self.submit_button.setEnabled(True)




    def add_combo_box(self, layout, label_text, options):
        """
        Add a combo box to the layout for selecting various options like topology, delay, etc.

        Args:
            layout (QVBoxLayout): The layout to add the combo box to.
            label_text (str): The label text for the combo box.
            options (str): The options for the combo box, separated by commas.
        """
        combo_label = QLabel(label_text, self)
        layout.addWidget(combo_label)

        combo_box = QComboBox(self)
        items_list = options.split(", ")
        items_list.insert(0, "")
        combo_box.addItems(items_list)
        combo_box.setCurrentText("")
        layout.addWidget(combo_box)

        self.combo_boxes[label_text] = combo_box

        combo_box.currentTextChanged.connect(lambda value: self.update_value(label_text, value))

    def on_upload_algorithm(self):
        """
        Handle the upload of a Python algorithm file.
        """
        initial_dir = os.getcwd()  # Get the current working directory
        fname, _ = QFileDialog.getOpenFileName(self, 'Upload Python File', initial_dir, "Python Files (*.py)")
        if fname:
            _, file_extension = os.path.splitext(fname)
            if file_extension.lower() == '.py':
                self.checkbox_values["Algorithm"] = fname
                self.update_value("Algorithm", fname)
            else:
                QMessageBox.warning(self, 'Error', 'Please select a Python file (.py)', QMessageBox.Ok)

    def on_upload_topology(self):
        """
        Handle the upload of a topology file.
        """
        fname, _ = QFileDialog.getOpenFileName(self, 'Upload Text File', '/home', "Text Files (*.txt)")
        if fname:
            _, file_extension = os.path.splitext(fname)
            if file_extension.lower() == '.txt':
                logger.info(f"file name is {fname}")
                self.checkbox_values["Topology File"] = fname
                self.update_value("Topology File", fname)
                self.handle_custom_topology()

            else:
                QMessageBox.warning(self, 'Error', 'Please select a text file (.txt)', QMessageBox.Ok)




    def on_delete_topology_file(self):
        """
        Handle the deletion of the uploaded topology file.
        """
        self.checkbox_values["Topology File"] = ""
        self.update_value("Topology File", "")
        self.combo_boxes["Topology"].setCurrentText("Random")
        self.combo_boxes["Topology"].setEnabled(True)
        self.combo_boxes["Root"].setCurrentText("Random")
        self.combo_boxes["Root"].setEnabled(True)
        self.combo_boxes["ID Type"].setCurrentText("Random")
        self.combo_boxes["ID Type"].setEnabled(True)

    def handle_custom_topology(self):
        self.combo_boxes["Topology"].setCurrentText("Custom")
        self.combo_boxes["Topology"].setEnabled(False)
        self.combo_boxes["Root"].setCurrentText("Custom")
        self.combo_boxes["Root"].setEnabled(False)
        self.combo_boxes["ID Type"].setCurrentText("Custom")
        self.combo_boxes["ID Type"].setEnabled(False)

    def on_submit_all(self):
        """
        Handle the final submission of all settings and save them to a JSON file.
        """
        logger.debug(f"Checkbox values are: {self.checkbox_values}")
        if any([value == "" for key, value in self.checkbox_values.items() if key != "Topology File"]):
            QMessageBox.warning(self, 'Error', 'Please fill in all the fields before submitting.', QMessageBox.Ok)
            return
        if self.checkbox_values["Topology File"] == '' and (
                self.checkbox_values["Topology"] == "Custom" or
                self.checkbox_values["Root"] == "Custom" or
                self.checkbox_values["ID Type"] == "Custom"
        ):
            QMessageBox.warning(self, 'Error', 'Please upload a topology file when any custom option is selected.', QMessageBox.Ok)
            return
        with open(NETWORK_VARIABLES, "w") as f:
            json.dump(self.checkbox_values, f, indent=4)
        self.close()


def menu(network_variables: dict):
    """
    Launch the menu application for configuring network variables.

    Args:
        network_variables (dict): A dictionary of default or previously saved network variables.
    """
    app = QApplication(sys.argv)
    menu_window = MenuWindow(network_variables)
    menu_window.setWindowIcon(QIcon('./designFiles/app_icon.jpeg'))
    stylesheet_file = os.path.join('./designFiles', 'main_window.qss')
    with open(stylesheet_file, 'r') as f:
        menu_window.setStyleSheet(f.read())
    
    menu_window.show()
    app.exec_()
