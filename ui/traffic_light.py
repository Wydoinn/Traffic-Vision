import cv2
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLabel, QPushButton, QSpinBox, QComboBox,
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QMessageBox, QFileDialog, QDialog, QFormLayout,
                            QLineEdit, QDialogButtonBox, QScrollArea, QCheckBox)
from PyQt6.QtCore import Qt, QCoreApplication

from controller.light_controller import TrafficLightController, TrafficLightConfig


class TrafficLightPositionSelector:
    """
    Class for interactively selecting traffic light positions on the video frame.
    Uses the same interactive approach as zone creation.
    """
    def __init__(self, video_path, frame_width, frame_height):
        self.video_path = video_path
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.selected_position = None

    def select_position(self, light_name: str) -> tuple:
        """Interactively select a position on the video frame."""
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print("Error opening video stream")
            return None

        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("Failed to capture frame")
            return None

        resized_frame = cv2.resize(frame, (self.frame_width, self.frame_height))
        window_name = f"Select Position for {light_name}"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, self.frame_width, self.frame_height)

        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

        # Create a copy of the frame for drawing
        display_frame = resized_frame.copy()

        # Add instructions text
        self._draw_instructions(display_frame)

        cv2.imshow(window_name, display_frame)

        # Store clicked position
        self.selected_position = None

        def mouse_callback(event, x, y, flags, param):
            """Handle mouse events for position selection."""
            if event == cv2.EVENT_LBUTTONDOWN:
                # Create a copy of the original frame
                temp_frame = resized_frame.copy()

                # Draw marker at selected position
                cv2.circle(temp_frame, (x, y), 15, (0, 255, 0), -1)
                cv2.circle(temp_frame, (x, y), 15, (255, 255, 255), 2)

                # Add position text
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(temp_frame, f"Position: ({x}, {y})", (x + 20, y),
                           font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
                self._draw_instructions(temp_frame)
                cv2.imshow(window_name, temp_frame)
                self.selected_position = (x, y)

        cv2.setMouseCallback(window_name, mouse_callback)

        # Wait for user input with a way to ensure it doesn't block the UI thread
        while True:
            key = cv2.waitKey(100) & 0xFF
            QCoreApplication.processEvents()

            if key == 27:  # ESC key
                self.selected_position = None
                break
            elif key == 13:  # Enter key
                break

            # Check if window still exists, break if it's been closed
            try:
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
            except:
                break

        cv2.destroyAllWindows()

        # Additional cleanup to ensure window is closed
        for i in range(5):
            cv2.waitKey(1)

        return self.selected_position

    def _draw_instructions(self, frame):
        """Helper method to draw instruction text on frame."""
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, "Click to position traffic light.", (10, 30),
                   font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "Press Enter to confirm, Esc to cancel", (10, 60),
                   font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)


class AddTrafficLightDialog(QDialog):
    """Dialog for adding a new traffic light."""

    def __init__(self, parent=None, zone_names=None):
        super().__init__(parent)
        self.setWindowTitle("Add Traffic Light")
        self.zone_names = zone_names or []
        self.parent = parent
        self.position_selector = None

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # ID field
        self.id_edit = QLineEdit()
        self.id_edit.setToolTip("Enter a unique identifier for the traffic light")
        form_layout.addRow("Light ID:", self.id_edit)

        # Name field
        self.name_edit = QLineEdit()
        self.name_edit.setToolTip("Enter a display name for the traffic light")
        form_layout.addRow("Display Name:", self.name_edit)

        # Zone selection
        self.zone_combo = QComboBox()
        self.zone_combo.setToolTip("Select the traffic zone this light will control")
        self.zone_combo.addItems(self.zone_names)
        form_layout.addRow("Traffic Zone:", self.zone_combo)

        # Timing fields
        self.min_green_spin = QSpinBox()
        self.min_green_spin.setToolTip("Minimum duration of green light in seconds")
        self.min_green_spin.setRange(5, 30)
        self.min_green_spin.setValue(16)
        form_layout.addRow("Min Green Time (s):", self.min_green_spin)

        self.max_green_spin = QSpinBox()
        self.max_green_spin.setToolTip("Maximum duration of green light in seconds")
        self.max_green_spin.setRange(15, 120)
        self.max_green_spin.setValue(60)
        form_layout.addRow("Max Green Time (s):", self.max_green_spin)

        self.yellow_spin = QSpinBox()
        self.yellow_spin.setToolTip("Duration of yellow light in seconds")
        self.yellow_spin.setRange(2, 5)
        self.yellow_spin.setValue(3)
        form_layout.addRow("Yellow Duration (s):", self.yellow_spin)

        # Add pedestrian timing settings
        self.ped_min_spin = QSpinBox()
        self.ped_min_spin.setToolTip("Minimum duration of pedestrian crossing phase in seconds")
        self.ped_min_spin.setRange(5, 20)
        self.ped_min_spin.setValue(10)
        form_layout.addRow("Min Pedestrian Time (s):", self.ped_min_spin)

        self.ped_max_spin = QSpinBox()
        self.ped_max_spin.setToolTip("Maximum duration of pedestrian crossing phase in seconds")
        self.ped_max_spin.setRange(15, 45)
        self.ped_max_spin.setValue(30)
        form_layout.addRow("Max Pedestrian Time (s):", self.ped_max_spin)

        layout.addLayout(form_layout)

        # Position selection
        self.position_label = QLabel("Position: (0, 0)")
        layout.addWidget(self.position_label)

        self.select_position_btn = QPushButton("Select Position on Video")
        self.select_position_btn.setToolTip("Click to place the traffic light on the video frame")
        self.select_position_btn.clicked.connect(self.select_position)
        layout.addWidget(self.select_position_btn)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

        # Initialize position
        self.position = (0, 0)

    def select_position(self):
        """Open position selector to choose position on the video frame."""
        if not self._validate_prerequisites():
            return

        # Prepare UI state for position selection
        ui_state = self._prepare_ui_state()

        # Get main window reference
        main_window = self.parent.parent

        # Initialize position selector
        self.position_selector = TrafficLightPositionSelector(
            main_window.video_path,
            main_window.zone_manager.frame_width,
            main_window.zone_manager.frame_height
        )

        # Select position interactively
        light_name = self.name_edit.text() or "Traffic Light"
        position = self.position_selector.select_position(light_name)

        # Restore UI state
        self._restore_ui_state(ui_state)

        # Handle selection result
        self._handle_position_result(position)

    def _validate_prerequisites(self):
        """Validate all prerequisites for position selection."""
        # Check if we have a valid parent reference
        if not self.parent or not hasattr(self.parent, 'parent') or not self.parent.parent:
            QMessageBox.warning(self, "Error", "Cannot access main application window.")
            return False

        main_window = self.parent.parent

        # Check if video path exists
        if not hasattr(main_window, 'video_path') or not main_window.video_path:
            QMessageBox.warning(self, "Error", "Please select a video first!")
            return False

        # Check if zone manager is initialized
        if not hasattr(main_window, 'zone_manager') or not main_window.zone_manager:
            QMessageBox.warning(self, "Error", "Zone manager not initialized!")
            return False

        return True

    def _prepare_ui_state(self):
        """Prepare dialog UI state for position selection."""
        was_modal = self.isModal()
        self.setModal(False)
        self.showMinimized()
        QCoreApplication.processEvents()
        return {"was_modal": was_modal}

    def _restore_ui_state(self, state):
        """Restore dialog UI state after position selection."""
        self.showNormal()
        self.raise_()
        self.activateWindow()
        self.setModal(state["was_modal"])
        QCoreApplication.processEvents()

    def _handle_position_result(self, position):
        """Handle the position selection result."""
        if position:
            self.set_position(position)
        else:
            self._show_cancelled_dialog()

    def _show_cancelled_dialog(self):
        """Show a dialog indicating position selection was cancelled."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Cancelled")
        msg_box.setText("Position selection cancelled.")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setWindowModality(Qt.WindowModality.WindowModal)
        msg_box.exec()
        self.raise_()
        self.activateWindow()

    def set_position(self, position):
        """Set the selected position."""
        self.position = position
        self.position_label.setText(f"Position: {position}")

    def get_traffic_light_config(self):
        """Returns a TrafficLightConfig object with the entered data."""
        return TrafficLightConfig(
            id=self.id_edit.text(),
            name=self.name_edit.text(),
            zone_id=self.zone_combo.currentText(),
            min_green_time=self.min_green_spin.value(),
            max_green_time=self.max_green_spin.value(),
            yellow_duration=self.yellow_spin.value(),
            pedestrian_min_time=self.ped_min_spin.value(),
            pedestrian_max_time=self.ped_max_spin.value(),
            position=self.position
        )


class AddIntersectionDialog(QDialog):
    """Dialog for creating a new intersection."""

    def __init__(self, parent=None, available_lights=None):
        super().__init__(parent)
        self.setWindowTitle("Add Intersection")
        self.available_lights = available_lights or {}

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Intersection ID
        self.id_edit = QLineEdit()
        form_layout.addRow("Intersection ID:", self.id_edit)

        layout.addLayout(form_layout)

        # Available lights with scrolling
        lights_group = QGroupBox("Select Traffic Lights")
        lights_layout = QVBoxLayout()

        # Create a scrollable area for lights
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create a container widget for the checkboxes
        scroll_content = QWidget()
        checkbox_layout = QVBoxLayout(scroll_content)

        self.light_checkboxes = {}
        for light_id, light_name in self.available_lights.items():
            checkbox = QCheckBox(f"{light_name} ({light_id})")
            checkbox.setProperty("light_id", light_id)
            self.light_checkboxes[light_id] = checkbox
            checkbox_layout.addWidget(checkbox)

        checkbox_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        scroll_area.setFixedHeight(200)

        lights_layout.addWidget(scroll_area)
        lights_group.setLayout(lights_layout)
        layout.addWidget(lights_group)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_intersection_data(self):
        """Returns the intersection ID and selected light IDs."""
        intersection_id = self.id_edit.text()
        selected_lights = []

        for light_id, checkbox in self.light_checkboxes.items():
            if checkbox.isChecked():
                selected_lights.append(light_id)

        return intersection_id, selected_lights


class TrafficLightConfigTab(QWidget):
    """Tab for configuring and managing traffic lights."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.traffic_controller = TrafficLightController()
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI components for traffic light configuration."""
        layout = QVBoxLayout()

        # Control buttons
        control_layout = QHBoxLayout()

        self.save_config_btn = QPushButton("Save Configuration")
        self.save_config_btn.setToolTip("Save the current traffic light configuration to a file")
        self.save_config_btn.clicked.connect(self.save_configuration)

        self.load_config_btn = QPushButton("Load Configuration")
        self.load_config_btn.setToolTip("Load a previously saved traffic light configuration")
        self.load_config_btn.clicked.connect(self.load_configuration)

        control_layout.addWidget(self.save_config_btn)
        control_layout.addWidget(self.load_config_btn)

        layout.addLayout(control_layout)

        # Traffic lights section
        lights_group = QGroupBox("Traffic Lights")
        lights_layout = QVBoxLayout()

        # Traffic lights table
        self.lights_table = QTableWidget()
        self.lights_table.setColumnCount(8)
        self.lights_table.setHorizontalHeaderLabels([
            "ID", "Name", "Zone", "Min Time", "Max Time", "Yellow Time", "Ped Min", "Ped Max"
        ])

        self._configure_table(self.lights_table, 200, [80, 120, 100, 80, 80, 80, 80, 80])

        lights_layout.addWidget(self.lights_table)

        # Add/Remove light buttons
        light_buttons_layout = QHBoxLayout()
        self.add_light_btn = QPushButton("Add Light")
        self.add_light_btn.setToolTip("Add a new traffic light to the configuration")
        self.add_light_btn.clicked.connect(self.add_traffic_light)

        self.remove_light_btn = QPushButton("Remove Light")
        self.remove_light_btn.setToolTip("Remove the selected traffic light")
        self.remove_light_btn.clicked.connect(self.remove_traffic_light)

        light_buttons_layout.addWidget(self.add_light_btn)
        light_buttons_layout.addWidget(self.remove_light_btn)
        lights_layout.addLayout(light_buttons_layout)

        lights_group.setLayout(lights_layout)
        layout.addWidget(lights_group)

        # Intersections section
        intersections_group = QGroupBox("Intersections")
        intersections_layout = QVBoxLayout()

        # Intersections table
        self.intersections_table = QTableWidget()
        self.intersections_table.setColumnCount(2)
        self.intersections_table.setHorizontalHeaderLabels([
            "Intersection ID", "Traffic Lights"
        ])

        self._configure_table(self.intersections_table, 150, [120, 300])

        intersections_layout.addWidget(self.intersections_table)

        # Add/Remove intersection buttons
        intersection_buttons_layout = QHBoxLayout()
        self.add_intersection_btn = QPushButton("Add Intersection")
        self.add_intersection_btn.setToolTip("Create a new intersection by grouping traffic lights")
        self.add_intersection_btn.clicked.connect(self.add_intersection)

        self.remove_intersection_btn = QPushButton("Remove Intersection")
        self.remove_intersection_btn.setToolTip("Remove the selected intersection")
        self.remove_intersection_btn.clicked.connect(self.remove_intersection)

        intersection_buttons_layout.addWidget(self.add_intersection_btn)
        intersection_buttons_layout.addWidget(self.remove_intersection_btn)
        intersections_layout.addLayout(intersection_buttons_layout)

        intersections_group.setLayout(intersections_layout)
        layout.addWidget(intersections_group)

        # Add adaptive mode button in center at the bottom
        self.adaptive_btn = QPushButton("Adaptive Mode: ON")
        self.adaptive_btn.setToolTip("Toggle between adaptive timing based on traffic conditions and fixed timing")
        self.adaptive_btn.setCheckable(True)
        self.adaptive_btn.setChecked(True)
        self.adaptive_btn.clicked.connect(self.toggle_adaptive_mode)

        adaptive_layout = QHBoxLayout()
        adaptive_layout.addStretch(1)
        adaptive_layout.addWidget(self.adaptive_btn)
        adaptive_layout.addStretch(1)
        layout.addLayout(adaptive_layout)

        self.setLayout(layout)

        # Initial table update
        self.update_tables()

        # Initially disable buttons until there's something to control/save
        self._update_button_states()

    def _configure_table(self, table, fixed_height, column_widths):
        """Configure a table with standard settings to avoid code duplication."""
        # Make the table scrollable with fixed height
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setFixedHeight(fixed_height)

        # Configure header to optimize space usage
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setMinimumSectionSize(80)
        header.setStretchLastSection(False)

        # Configure the table for better text display
        table.setWordWrap(True)
        table.setTextElideMode(Qt.TextElideMode.ElideRight)
        table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)

        # Set reasonable initial column widths
        for i, width in enumerate(column_widths):
            table.setColumnWidth(i, width)

    def _update_button_states(self):
        """Update button enable states based on current configuration."""
        has_config = self.has_saveable_configuration()
        self.save_config_btn.setEnabled(has_config)
        self.adaptive_btn.setEnabled(has_config)

    def has_saveable_configuration(self):
        """Check if there's any traffic light configuration to save or control."""
        return (len(self.traffic_controller.traffic_lights) > 0 or
                len(self.traffic_controller.intersections) > 0)

    def toggle_adaptive_mode(self):
        """Toggle between adaptive and fixed timing modes."""
        is_adaptive = self.traffic_controller.toggle_adaptive_mode()
        self.adaptive_btn.setText(f"Adaptive Mode: {'ON' if is_adaptive else 'OFF'}")

    def add_traffic_light(self):
        """Open dialog to add a new traffic light."""
        # Get available zone names from parent
        zone_names = []
        if hasattr(self.parent, 'zone_manager') and self.parent.zone_manager:
            vehicle_zones = list(self.parent.zone_manager.zones.get('vehicle', {}).keys())
            zone_names = vehicle_zones

        dialog = AddTrafficLightDialog(self, zone_names)
        # Connect position selection if we have a video frame
        if hasattr(self.parent, 'select_position_on_frame'):
            dialog.select_position_btn.clicked.connect(
                lambda: self.parent.select_position_on_frame(dialog.set_position)
            )

        if dialog.exec():
            try:
                config = dialog.get_traffic_light_config()
                self.traffic_controller.add_traffic_light(config)
                self.update_tables()
                QMessageBox.information(self, "Success", f"Traffic light '{config.name}' added successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not add traffic light: {str(e)}")

    def remove_traffic_light(self):
        """Remove the selected traffic light."""
        selected_rows = self.lights_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No traffic light selected.")
            return

        # Get the ID from the first column of the selected row
        light_id = self.lights_table.item(selected_rows[0].row(), 0).text()

        # Check if this light is used in any intersection
        for intersection_id, light_ids in self.traffic_controller.intersections.items():
            if light_id in light_ids:
                QMessageBox.warning(
                    self, "Warning",
                    f"Cannot remove traffic light '{light_id}' as it is used in intersection '{intersection_id}'."
                )
                return

        # Remove the traffic light
        if light_id in self.traffic_controller.traffic_lights:
            del self.traffic_controller.traffic_lights[light_id]
            self.update_tables()
            QMessageBox.information(self, "Success", f"Traffic light '{light_id}' removed.")

    def add_intersection(self):
        """Open dialog to add a new intersection."""
        # Get available traffic lights
        available_lights = {
            light_id: light.config.name
            for light_id, light in self.traffic_controller.traffic_lights.items()
        }

        if not available_lights:
            QMessageBox.warning(self, "Warning", "No traffic lights available. Please add traffic lights first.")
            return

        dialog = AddIntersectionDialog(self, available_lights)
        if dialog.exec():
            intersection_id, selected_lights = dialog.get_intersection_data()

            if not intersection_id:
                QMessageBox.warning(self, "Warning", "Intersection ID cannot be empty.")
                return

            if not selected_lights:
                QMessageBox.warning(self, "Warning", "No traffic lights selected.")
                return

            if len(selected_lights) < 2:
                QMessageBox.warning(self, "Warning", "You need at least 2 traffic lights for an intersection.")
                return

            try:
                self.traffic_controller.create_intersection(intersection_id, selected_lights)
                self.update_tables()
                QMessageBox.information(self, "Success", f"Intersection '{intersection_id}' created successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not create intersection: {str(e)}")

    def remove_intersection(self):
        """Remove the selected intersection."""
        selected_rows = self.intersections_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No intersection selected.")
            return

        # Get the intersection ID from the first column of the selected row
        intersection_id = self.intersections_table.item(selected_rows[0].row(), 0).text()

        # Remove the intersection
        if intersection_id in self.traffic_controller.intersections:
            # Also cleanup related data structures
            if intersection_id in self.traffic_controller.active_phase:
                del self.traffic_controller.active_phase[intersection_id]
            if intersection_id in self.traffic_controller.phase_start_time:
                del self.traffic_controller.phase_start_time[intersection_id]

            del self.traffic_controller.intersections[intersection_id]
            self.update_tables()
            QMessageBox.information(self, "Success", f"Intersection '{intersection_id}' removed.")

    def update_tables(self):
        """Update the traffic lights and intersections tables."""
        # Update traffic lights table
        self.lights_table.setRowCount(0)
        self.lights_table.setColumnCount(8)
        self.lights_table.setHorizontalHeaderLabels([
            "ID", "Name", "Zone", "Min Time", "Max Time", "Yellow Time", "Ped Min", "Ped Max"
        ])

        row = 0

        for light_id, light in self.traffic_controller.traffic_lights.items():
            self.lights_table.insertRow(row)

            # Create items and ensure they're selectable and editable for better interaction
            id_item = QTableWidgetItem(light_id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.lights_table.setItem(row, 0, id_item)
            self.lights_table.setItem(row, 1, QTableWidgetItem(light.config.name))
            self.lights_table.setItem(row, 2, QTableWidgetItem(light.config.zone_id))
            self.lights_table.setItem(row, 3, QTableWidgetItem(str(light.config.min_green_time)))
            self.lights_table.setItem(row, 4, QTableWidgetItem(str(light.config.max_green_time)))
            self.lights_table.setItem(row, 5, QTableWidgetItem(str(light.config.yellow_duration)))
            self.lights_table.setItem(row, 6, QTableWidgetItem(str(getattr(light.config, 'pedestrian_min_time', 10))))
            self.lights_table.setItem(row, 7, QTableWidgetItem(str(getattr(light.config, 'pedestrian_max_time', 30))))

            row += 1

        # Update intersections table
        self.intersections_table.setRowCount(0)
        row = 0

        for intersection_id, light_ids in self.traffic_controller.intersections.items():
            self.intersections_table.insertRow(row)

            id_item = QTableWidgetItem(intersection_id)
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.intersections_table.setItem(row, 0, id_item)

            # Create a comma-separated list of light IDs
            light_names = []
            for light_id in light_ids:
                if light_id in self.traffic_controller.traffic_lights:
                    light = self.traffic_controller.traffic_lights[light_id]
                    light_names.append(f"{light.config.name} ({light_id})")
                else:
                    light_names.append(f"Unknown ({light_id})")

            lights_item = QTableWidgetItem(", ".join(light_names))
            lights_item.setToolTip(", ".join(light_names))

            self.intersections_table.setItem(row, 1, lights_item)

            row += 1

        self._update_button_states()

    def save_configuration(self):
        """Save traffic light configuration to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Traffic Light Configuration", "", "JSON Files (*.json)"
        )

        if not file_path:
            return

        if not file_path.endswith('.json'):
            file_path += '.json'
        try:
            self.traffic_controller.save_configuration(file_path)
            QMessageBox.information(self, "Success", f"Configuration saved to {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save configuration: {str(e)}")

    def load_configuration(self):
        """Load traffic light configuration from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Traffic Light Configuration", "", "JSON Files (*.json)"
        )

        if not file_path:
            return

        try:
            success = self.traffic_controller.load_configuration(file_path)
            if success:
                self.update_tables()
                QMessageBox.information(self, "Success", f"Configuration loaded from {file_path}")
            else:
                QMessageBox.warning(self, "Error", "Failed to load configuration.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load configuration: {str(e)}")

    def get_controller(self):
        """Returns the traffic light controller instance."""
        return self.traffic_controller
