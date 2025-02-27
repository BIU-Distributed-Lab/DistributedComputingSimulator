from utils.logger_config import logger


def wheelEvent(self, event):
    """
    Zoom in or out on mouse wheel event.

    This method handles the zoom functionality based on the wheel event.
    
    Args:
        event (QWheelEvent): The event object containing information about the mouse wheel movement.
    """
    delta_y = event.angleDelta().y()
    factor = self.zoom_factor if delta_y > 0 else 1 / self.zoom_factor
    self.view.scale(factor, factor)


def regenarate_clicked(self):
    """
    Generate a new layout if the current choice in the combo box is 'random'.

    This method is triggered when the 'regenerate' button is clicked and checks if the
    layout choice is set to 'random' to generate a new random layout.
    """
    if self.choice_combo.currentText() == "random":
        self.set_nx_layout("random")


def toggle_timer(self):
    """
    Toggle the timer based on the QCheckBox state.

    This method starts or stops the timer based on whether the 'run_checkbox' is checked.
    """
    if self.run_checkbox.isChecked():
        self.timer.start(abs(self.slider.value()))
    else:
        self.timer.stop()


def update_timer_interval(self):
    """
    Update the timer interval based on the slider value.

    This method adjusts the timer interval whenever the slider value changes.
    """
    new_interval = self.slider.value()
    self.timer.setInterval(abs(new_interval))


def update_slider_label(self):
    """
    Update the slider label to show the interval in seconds per tick.

    This method updates the label that shows the current slider value in seconds.
    """
    self.slider_label.setText(f"{abs(self.slider.value() / 1000)} seconds per tick")


def reset(self):
    """
    Reset the system to its initial state.

    This method is triggered when the 'reset' button is pressed and undoes all changes by calling 'undo_change' until the change stack is empty.
    """
    while self.change_stack:
        self.undo_change()


def undo_change(self):
    """
    Undo the last change made to a node.

    This method is triggered when the 'undo' button is pressed. It retrieves the last change from the change stack, reverts the node's state, and updates the network.
    """
    if self.change_stack:
        previous_node_item, previous_state = self.change_stack.pop(0)
        previous_node_item.values = previous_state
        previous_node_item.color = previous_state['color']

        _, next_state = self.change_stack.pop(0)
        self.network.node_values_change.insert(0, next_state)

        previous_node_item.update()


def change_node_color(self, times, sync):
    """
    Change the color of a node based on the current state in the network.

    This method is called when a button is clicked and updates the color of a node based on the values in 'node_values_change'. It can update the color multiple times based on the 'times' argument.

    Args:
        times (int): The number of times to update the node color.
    """

    if not hasattr(self, 'current_round'):
        self.current_round = 0

    if sync:
        self.round_label.show()  # Show the label in synchronous mode
        for _ in range(times):
            round_changes = []
            if self.network.node_values_change:
                current_round = self.network.node_values_change[0][1]
                round_changes.append(self.network.node_values_change.pop(0))
                while len(self.network.node_values_change) and self.network.node_values_change[0][1] == current_round:
                    round_changes.append(self.network.node_values_change.pop(0))

                for values_change_dict, _ in round_changes:
                    node_name = values_change_dict.get('id')
                    if node_name is not None:
                        self.update_node_color(node_name, values_change_dict)

            if round_changes:  # Only update the round if there are changes
                self.current_round += 1
                self.round_label.setText(f"Round: {self.current_round}")

    else:
        self.round_label.hide()  # Hide the label in asynchronous mode
        for _ in range(times):
            if self.network.node_values_change:
                values_change_dict = self.network.node_values_change.pop(0) # (values, round)
                values_change_dict = values_change_dict[0]
                node_name = values_change_dict.get('id')
                if node_name != None:
                    self.update_node_color(node_name, values_change_dict)


def update_node_color(self, node_name, values_change_dict):
    """
    Update the node's color and state based on the provided values.

    This method updates the node's color and other values based on the 'values_change_dict', and it stores the current state in the change stack for undo purposes.

    Args:
        node_name (str): The name (ID) of the node whose color is to be updated.
        values_change_dict (dict): The dictionary containing the updated values for the node.
    """
    node_item = self.nodes_map[str(node_name)]
    previous_state = node_item.values.copy()
    changes = []
    for key, value in values_change_dict.items():
        node_item.values[key] = value
        if not key.startswith("_") and previous_state.get(key) != value:
            changes.append(f"'{key}' changed to '{value}'")
            #print(f"Key '{key}' changed to '{value}'")
            logger.debug(f"Key '{key}' changed to '{value}'")

    node_item.color = node_item.values['color']
    next_state = node_item.values.copy()
    self.change_stack.insert(0, (node_item, previous_state))
    self.change_stack.insert(1, (node_item, next_state))
    node_item.update()

    # Update the label with the changes
    # if changes:
    #     self.last_phase_label.setText(f"Last phase changes in node {node_name}: " + ", ".join(changes))
    # else:
    #     self.last_phase_label.setText("Last phase: No changes")
