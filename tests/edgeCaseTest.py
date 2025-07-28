import json
import os
import tempfile
import shutil
import pytest
from simulator.config import NodeState


def test_simulation_sync_mode():
    # Backup original network_variables.json if it exists
    original_vars_file = "network_variables.json"
    backup_file = None
    if os.path.exists(original_vars_file):
        backup_file = tempfile.mktemp(suffix=".json")
        shutil.copy2(original_vars_file, backup_file)

    try:
        print("=== PHASE 1: Setting up simulation configuration ===")

        # Create network variables configuration directly (no GUI)
        network_variables = {
            "Algorithm": "edgeCaseSyncAlg.py",
            "Topology File": "testTopology.txt",
            "Topology": "Custom",
            "Root": "Custom",
            "ID Type": "Custom",
            "Sync": "Sync",
            "Delay": "Constant",
            "Display": "Text",
            "Logging": "Short",
            "Number of Computers": "17"
        }

        # Save configuration to file
        with open("network_variables.json", 'w') as f:
            json.dump(network_variables, f, indent=4)

        print("Configuration saved:")
        for key, value in network_variables.items():
            print(f"  {key}: {value}")

        print("\n=== PHASE 2: Running Simulation in Text Mode ===")

        # Import simulation modules
        from simulator import initializationModule, communication, runModule

        # Run the simulation directly
        try:
            print(f"Initializing simulation with {network_variables['Number of Computers']} computers")

            # Create network and communication objects
            network = initializationModule.Initialization(network_variables)
            comm = communication.Communication(network)

            print("Network topology loaded successfully")
            print(f"Number of nodes in network: {len(network.network_dict)}")

            # Print initial network state
            print("\nInitial network state:")
            for node_id, node in network.network_dict.items():
                neighbors = [n for n in node.connectedEdges]
                print(f"  Node {node_id}: neighbors = {neighbors}")

            print("\nStarting algorithm execution...")

            # Run the algorithm directly (no threading needed for text mode)
            runModule.initiateRun(network, comm, network_variables['Sync'])

            print("\n=== SIMULATION COMPLETED ===")
            print(f"Algorithm: {network_variables['Algorithm']}")
            print(f"Topology: {network_variables['Topology']}")
            print(f"Number of computers: {network_variables['Number of Computers']}")
            print(f"Display mode: {network_variables['Display']}")
            print("Simulation completed successfully in text mode.")

            # Print final network state
            print("\nFinal network state:")
            for node_id, node in network.network_dict.items():
                # Try to access common algorithm result attributes
                status_info = []
                if hasattr(node, 'parent'):
                    status_info.append(f"parent={node.parent}")
                if hasattr(node, 'distance'):
                    status_info.append(f"distance={node.distance}")
                if hasattr(node, 'level'):
                    status_info.append(f"level={node.level}")
                if hasattr(node, 'state'):
                    status_info.append(f"state={node.state}")

                status_str = ", ".join(status_info) if status_info else "no additional state"
                print(f"  Node {node_id}: {status_str}")
                assert node.state == NodeState.TERMINATED, f"Node {node_id} did not terminate correctly"
                if node.id == 5 or node.id ==6 or node.id ==7 or node.id ==8 or node.id ==9 or node.id ==2 or node.id ==3 or node.id ==4 or node.id ==17:
                    assert node.color == "purple", f"Node {node_id} did not set purple to coral correctly"
                else:
                    assert node.color == "salmon", f"Node {node_id} did not set salmon to purple correctly"

        except SystemExit:
            print("Simulation completed normally (SystemExit caught)")

        print("SUCCESS: Text mode simulation finished!")

    finally:
        # Restore original network_variables.json if it existed
        if backup_file and os.path.exists(backup_file):
            shutil.move(backup_file, original_vars_file)
        elif os.path.exists(original_vars_file):
            os.remove(original_vars_file)
