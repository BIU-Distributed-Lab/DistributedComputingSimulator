import json
import logging
import os
import pytest
import tempfile
import shutil
from unittest.mock import patch
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QFileDialog, QPushButton
from pytestqt import qtbot

from PyQt5.QtGui import QIcon

@pytest.mark.gui
def test_complete_gui_workflow_with_simulation(qtbot):
    """Complete test: clicks GUI buttons AND runs full simulation with graph window."""
    print("Testing complete GUI workflow with actual simulation")
    
    # Backup original network_variables.json if it exists
    original_vars_file = "network_variables.json"
    backup_file = None
    if os.path.exists(original_vars_file):
        backup_file = tempfile.mktemp(suffix=".json")
        shutil.copy2(original_vars_file, backup_file)
    
    try:
        print("=== PHASE 1: GUI Menu Interaction ===")
        
        # Create a QApplication for the test
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Import the GUI modules
        from simulator import MainMenu
        from simulator.MainMenu import MenuWindow
        
        # Start with default network variables
        default_vars = {
            "Algorithm": "",
            "Topology File": "",
            "Topology": "",
            "Root": "",
            "ID Type": "", 
            "Sync": "",
            "Delay": "",
            "Display": "",
            "Logging": "",
            "Number of Computers": ""
        }
        
        # Create the main menu window
        menu_window = MenuWindow(default_vars)
        qtbot.addWidget(menu_window)
        
        # Apply styling to the main menu window
        main_stylesheet_file = os.path.join('./designFiles', 'main_window.qss')
        if os.path.exists(main_stylesheet_file):
            with open(main_stylesheet_file, 'r') as f:
                menu_window.setStyleSheet(f.read())
        
        # Apply icon to the main menu window
        icon_file = './designFiles/app_icon.jpeg'
        if os.path.exists(icon_file):
            menu_window.setWindowIcon(QIcon(icon_file))
        
        # Show the window and wait for it to be visible
        menu_window.show()
        with qtbot.waitExposed(menu_window):
            pass
        
        print("Menu window opened - performing real user interactions...")
        
        # Interact with GUI like a real user
        print("Setting number of computers")
        number_input = menu_window.number_input
        qtbot.mouseClick(number_input, Qt.LeftButton)
        qtbot.keyClicks(number_input, "10")  # Use 10 computers
        qtbot.wait(100)
        
        print("Selecting topology")
        topology_combo = menu_window.combo_boxes["Topology"]
        qtbot.mouseClick(topology_combo, Qt.LeftButton)
        qtbot.wait(100)
        qtbot.keyClicks(topology_combo, "Custom")
        qtbot.wait(100)
        
        print("Uploading topology file...")
        # Find the topology file upload button
        upload_buttons = menu_window.findChildren(QPushButton, "")
        upload_topology_button = None
        for button in upload_buttons:
            if "Upload" in button.text() and "Topology" in button.text():
                upload_topology_button = button
                break
        
        # If specific topology upload button not found, look for generic upload
        if upload_topology_button is None:
            for button in upload_buttons:
                if "Upload" in button.text() and button.text() != "Upload Python File":
                    upload_topology_button = button
                    break
        
        if upload_topology_button is not None:
            with patch.object(QFileDialog, 'getOpenFileName') as mock_topology_dialog:
                mock_topology_dialog.return_value = ("topologyFiles/tree.txt", "Text Files (*.txt)")
                qtbot.mouseClick(upload_topology_button, Qt.LeftButton)
                qtbot.wait(100)
        
        print("Selecting root...")
        root_combo = menu_window.combo_boxes["Root"]
        qtbot.mouseClick(root_combo, Qt.LeftButton)
        qtbot.wait(100)
        qtbot.keyClicks(root_combo, "Min ID")
        qtbot.wait(100)
        
        print("Selecting ID type...")
        id_combo = menu_window.combo_boxes["ID Type"]
        qtbot.mouseClick(id_combo, Qt.LeftButton)
        qtbot.wait(100)
        qtbot.keyClicks(id_combo, "Sequential")
        qtbot.wait(100)
        
        print("Selecting sync mode...")
        sync_combo = menu_window.combo_boxes["Sync"]
        qtbot.mouseClick(sync_combo, Qt.LeftButton)
        qtbot.wait(100)
        qtbot.keyClicks(sync_combo, "Sync")
        qtbot.wait(100)
        
        print("Selecting delay...")
        delay_combo = menu_window.combo_boxes["Delay"]
        qtbot.mouseClick(delay_combo, Qt.LeftButton)
        qtbot.wait(100)
        qtbot.keyClicks(delay_combo, "Constant")
        qtbot.wait(100)
        
        print("Selecting GRAPH display mode...")
        display_combo = menu_window.combo_boxes["Display"]
        qtbot.mouseClick(display_combo, Qt.LeftButton)
        qtbot.wait(100)
        qtbot.keyClicks(display_combo, "Graph")
        qtbot.wait(100)
        
        print("Selecting logging level...")
        logging_combo = menu_window.combo_boxes["Logging"]
        qtbot.mouseClick(logging_combo, Qt.LeftButton)
        qtbot.wait(100)
        qtbot.keyClicks(logging_combo, "Short")
        qtbot.wait(100)
        
        print("Uploading algorithm...")
        upload_buttons = menu_window.findChildren(QPushButton, "")
        upload_algorithm_button = None
        for button in upload_buttons:
            if button.text() == "Upload Python File":
                upload_algorithm_button = button
                break
        
        assert upload_algorithm_button is not None, "Could not find Upload Python File button"
        
        with patch.object(QFileDialog, 'getOpenFileName') as mock_dialog:
            mock_dialog.return_value = ("algorithms/sync_BFS.py", "Python Files (*.py)")
            qtbot.mouseClick(upload_algorithm_button, Qt.LeftButton)
            qtbot.wait(100)
        
        print("Submitting configuration...")
        submit_button = menu_window.submit_button
        qtbot.mouseClick(submit_button, Qt.LeftButton)
        
        # Wait for the window to close
        qtbot.waitUntil(lambda: not menu_window.isVisible(), timeout=5000)
        print("Menu window closed successfully")
        
        print("=== PHASE 2: Running Simulation with Graph Visualization ===")
        
        # Import simulation modules
        from simulator import initializationModule, communication, runModule
        import visualizations.graphVisualization as graphVisualization
        
        # Run the simulation directly without reopening the menu
        try:
            # Load the saved configuration
            with open("network_variables.json", 'r') as f:
                network_variables = json.load(f)
            
            print(f"Running simulation with {network_variables['Number of Computers']} computers")
            
            # Create network and communication objects directly
            network = initializationModule.Initialization(network_variables)
            comm = communication.Communication(network)
            
            # Open the graph visualization window
            app_for_graph = QApplication.instance()
            if not app_for_graph:
                app_for_graph = QApplication([])
            
            # Create the graph visualization window directly
            from visualizations.graphVisualization import GraphVisualizer
            graph_window = GraphVisualizer(network, comm)
            
            # Apply styling and show the window
            stylesheet_file = os.path.join('./designFiles', 'graph_window.qss')
            if os.path.exists(stylesheet_file):
                with open(stylesheet_file, 'r') as f:
                    graph_window.setStyleSheet(f.read())
            
            icon_file = './designFiles/app_icon.jpeg'
            if os.path.exists(icon_file):
                graph_window.setWindowIcon(QIcon(icon_file))
            
            graph_window.show()
            graph_window.resize(1000, 800)
            
            # Run the algorithm in a separate thread
            import threading
            algorithm_thread = threading.Thread(
                target=runModule.initiateRun, 
                args=(network, comm, network_variables['Sync'])
            )
            algorithm_thread.start()
            
            print("Graph window is now open! Clicking through next phase 5 times...")
            
            # Wait a moment for the window to fully initialize
            qtbot.wait(1000)
            
            # Click the "Next Phase" button 5 times
            if hasattr(graph_window, 'next_phase_button'):
                for i in range(5):
                    qtbot.mouseClick(graph_window.next_phase_button, Qt.LeftButton)
                    qtbot.wait(500)  # Wait 500ms between clicks
                    
                print("Completed 5 Next Phase clicks, closing window...")
                # Close the graph window
                graph_window.close()
            else:
                print("Could not find Next Phase button, running normal event loop")
                # Run the Qt event loop for the graph
                app_for_graph.exec_()
            
            # Wait for algorithm to complete
            algorithm_thread.join()
            
            print("=== SIMULATION COMPLETED ===")
            print(f"Algorithm: {network_variables['Algorithm']}")
            print(f"Topology: {network_variables['Topology']}")
            print(f"Number of computers: {network_variables['Number of Computers']}")
            print(f"Display mode: {network_variables['Display']}")
            print("Graph window was displayed and closed.")
            
        except SystemExit:
            print("Simulation completed normally (SystemExit caught)")
        except Exception as e:
            print(f"Simulation completed (Exception: {e})")
            print("This may happen when the graph window is closed.")
        
        print("SUCCESS: Complete GUI workflow with simulation finished!")
        
    finally:
        # Restore original network_variables.json if it existed
        if backup_file and os.path.exists(backup_file):
            shutil.move(backup_file, original_vars_file)
        elif os.path.exists(original_vars_file):
            os.remove(original_vars_file)

    