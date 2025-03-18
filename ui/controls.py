from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QSpinBox, QPushButton, QFrame, QGroupBox)
from PyQt6.QtGui import QIcon
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import ZoneManagerGUI

class ControlPanel(QWidget):
    def __init__(self, parent: 'ZoneManagerGUI'):
        super().__init__(parent)
        self.main_window = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.create_video_selection_group())

        # Use consistent pattern for both zone types
        layout.addWidget(self.create_zone_configuration_group(
            "vehicle", "Vehicle Zone Configuration", "Create Vehicle Zones",
            self.main_window.start_create_vehicle_zones
        ))
        layout.addWidget(self.create_zone_configuration_group(
            "pedestrian", "Pedestrian Zone Configuration", "Create Pedestrian Zones",
            self.main_window.start_create_pedestrian_zones
        ))

        layout.addSpacing(10)
        layout.addLayout(self.create_zones_io_layout())
        layout.addSpacing(20)

        # Add traffic light control
        layout.addWidget(self.create_traffic_light_control_group())
        layout.addSpacing(10)

        layout.addWidget(self.create_inference_control_group())
        layout.addStretch(1)

    def create_video_selection_group(self):
        """Creates the video selection group box."""
        video_group = QGroupBox("Video Selection")
        video_group_layout = QVBoxLayout()
        video_selection_frame = QFrame()
        video_selection_layout = QHBoxLayout()
        self.video_path_label = QLabel("No video selected")
        select_video_btn = QPushButton("Select Video")
        select_video_btn.setIcon(QIcon.fromTheme("document-open"))
        select_video_btn.clicked.connect(self.main_window.select_video)
        video_selection_layout.addWidget(self.video_path_label)
        video_selection_layout.addWidget(select_video_btn)
        video_selection_frame.setLayout(video_selection_layout)
        video_group_layout.addWidget(video_selection_frame)
        video_group.setLayout(video_group_layout)
        return video_group

    def create_zone_configuration_group(self, zone_type, title, create_button_text, create_button_action):
        """Creates a zone configuration group with standardized layout."""
        zone_group = QGroupBox(title)
        zone_group_layout = QVBoxLayout()
        zone_frame = QFrame()
        zone_layout = QVBoxLayout()

        count_layout = QHBoxLayout()
        label_title = title.replace(" Configuration", "")
        count_label = QLabel(f"Number of {label_title}:")
        count_label.setFixedWidth(250)
        count_layout.addWidget(count_label)

        zone_spinbox = QSpinBox()
        zone_spinbox.setRange(1, 10)
        zone_spinbox.setValue(1)
        zone_spinbox.setFixedWidth(120)
        count_layout.addWidget(zone_spinbox)
        count_layout.addStretch()

        # Store spinbox reference
        setattr(self, f"{zone_type}_zone_spinbox", zone_spinbox)

        zone_layout.addLayout(count_layout)
        zone_frame.setLayout(zone_layout)
        zone_group_layout.addWidget(zone_frame)

        create_button = QPushButton(create_button_text)
        create_button.clicked.connect(create_button_action)
        zone_group_layout.addWidget(create_button)

        # Store button reference
        setattr(self, f"create_{zone_type}_zones_btn", create_button)

        zone_group.setLayout(zone_group_layout)
        return zone_group

    def create_zones_io_layout(self):
        """Creates the layout for zone save/load buttons."""
        zones_io_layout = QHBoxLayout()
        self.save_zones_btn = QPushButton("Save Zones")
        self.save_zones_btn.clicked.connect(self.main_window.save_zones)
        self.save_zones_btn.setEnabled(False)
        self.load_zones_btn = QPushButton("Load Zones")
        self.load_zones_btn.clicked.connect(self.main_window.load_zones)
        zones_io_layout.addWidget(self.save_zones_btn)
        zones_io_layout.addWidget(self.load_zones_btn)
        return zones_io_layout

    def create_traffic_light_control_group(self):
        """Creates traffic light control group."""
        traffic_light_group = QGroupBox("Traffic Light Control")
        traffic_light_layout = QVBoxLayout()

        self.toggle_traffic_lights_btn = QPushButton("Show Traffic Lights")
        self.toggle_traffic_lights_btn.setCheckable(True)
        self.toggle_traffic_lights_btn.setChecked(False)
        self.toggle_traffic_lights_btn.clicked.connect(self.toggle_traffic_lights)

        # Initially disable the traffic light button until configured
        self.toggle_traffic_lights_btn.setEnabled(False)

        traffic_light_layout.addWidget(self.toggle_traffic_lights_btn)
        traffic_light_group.setLayout(traffic_light_layout)
        return traffic_light_group

    def toggle_traffic_lights(self):
        """Toggles the display of traffic lights on the video."""
        if not self.main_window.zone_manager:
            return

        is_showing = self.main_window.zone_manager.toggle_traffic_light_display()
        self.update_traffic_light_button_text()

    def update_traffic_light_button_text(self):
        """Updates the traffic light button text based on the current display state."""
        if self.main_window.zone_manager and self.main_window.zone_manager.show_traffic_lights:
            self.toggle_traffic_lights_btn.setText("Hide Traffic Lights")
        else:
            self.toggle_traffic_lights_btn.setText("Show Traffic Lights")

    def enable_traffic_light_controls(self, enable=True):
        """Enable or disable traffic light controls based on configuration status."""
        self.toggle_traffic_lights_btn.setEnabled(enable)
        if not enable and self.toggle_traffic_lights_btn.isChecked():
            self.toggle_traffic_lights_btn.setChecked(False)
            self.update_traffic_light_button_text()

    def create_inference_control_group(self):
        """Creates the inference control group box."""
        inference_group = QGroupBox("Inference Control")
        inference_group_layout = QVBoxLayout()
        self.start_inference_btn = QPushButton("Start Inference")
        self.start_inference_btn.clicked.connect(self.main_window.toggle_inference)
        self.start_inference_btn.setEnabled(False)
        inference_group_layout.addWidget(self.start_inference_btn)
        inference_group.setLayout(inference_group_layout)
        return inference_group
