# monitoring.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QGridLayout,
                             QLabel, QFrame, QScrollArea)
from typing import Dict

class MonitoringTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.vehicle_counts = {
            "bicycle": 0,
            "car": 0,
            "motorcycle": 0,
            "bus": 0,
            "truck": 0
        }
        self.pedestrian_count = 0
        self.emergency_detected = False
        self.accident_detected = False
        self.zone_vehicle_counts = {}
        self.zone_pedestrian_counts = {}

    def setup_ui(self):
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Alert Indicators Section
        alerts_group = QGroupBox("Alert Indicators")
        alerts_layout = QGridLayout()

        # Emergency Vehicle Indicator
        self.emergency_indicator = QFrame()
        self.emergency_indicator.setFixedSize(30, 30)
        self.emergency_indicator.setStyleSheet("""
            QFrame {
                border: 2px solid gray;
                border-radius: 15px;
                background-color: #444444;
            }
        """)
        alerts_layout.addWidget(QLabel("Emergency Vehicle:"), 0, 0)
        alerts_layout.addWidget(self.emergency_indicator, 0, 1)

        # Accident Indicator
        self.accident_indicator = QFrame()
        self.accident_indicator.setFixedSize(30, 30)
        self.accident_indicator.setStyleSheet("""
            QFrame {
                border: 2px solid gray;
                border-radius: 15px;
                background-color: #444444;
            }
        """)
        alerts_layout.addWidget(QLabel("Accident Detected:"), 1, 0)
        alerts_layout.addWidget(self.accident_indicator, 1, 1)
        alerts_group.setLayout(alerts_layout)
        scroll_layout.addWidget(alerts_group)

        # Traffic Light Status Section
        self.traffic_light_group = QGroupBox("Traffic Light Status")
        self.traffic_light_layout = QVBoxLayout()
        self.traffic_light_group.setLayout(self.traffic_light_layout)
        scroll_layout.addWidget(self.traffic_light_group)

        # Vehicle Zones Statistics Group
        self.vehicle_zones_group = QGroupBox("Vehicle Zones Statistics")
        self.vehicle_zones_layout = QVBoxLayout()
        self.vehicle_zones_group.setLayout(self.vehicle_zones_layout)
        scroll_layout.addWidget(self.vehicle_zones_group)

        # Pedestrian Zones Statistics Group
        self.pedestrian_zones_group = QGroupBox("Pedestrian Zones Statistics")
        self.pedestrian_zones_layout = QVBoxLayout()
        self.pedestrian_zones_group.setLayout(self.pedestrian_zones_layout)
        scroll_layout.addWidget(self.pedestrian_zones_group)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        self.setLayout(layout)

    def update_zone_vehicle_counts(self, zone_counts: Dict[str, Dict[str, int]]):
        """Updates statistics for vehicle zones, showing all zones even if empty."""
        # Clear previous widgets
        self.clear_layout(self.vehicle_zones_layout)

        if not zone_counts:
            self.vehicle_zones_layout.addWidget(self.create_no_zones_message("vehicle"))
            return

        for zone_name, counts in zone_counts.items():
            zone_group = QGroupBox(zone_name)
            zone_layout = QGridLayout()

            total_vehicles = sum(counts.values())
            density = self.calculate_traffic_density(total_vehicles)

            # Add density indicator
            density_label = QLabel(f"Traffic Density: {density}")
            density_label.setStyleSheet(f"font-weight: bold; color: {self.get_density_color(density)};")
            zone_layout.addWidget(density_label, 0, 0, 1, 2)

            # Add all vehicle counts with consistent styling
            for row, (vehicle_type, count) in enumerate(counts.items(), 1):
                count_style = "font-weight: bold; color: #4a90e2;" if count > 0 else "color: gray;"
                self.add_count_row(zone_layout, vehicle_type.capitalize(), count, count_style, row)

            zone_group.setLayout(zone_layout)
            self.vehicle_zones_layout.addWidget(zone_group)

    def update_zone_pedestrian_counts(self, zone_counts: Dict[str, int]):
        """Updates statistics for pedestrian zones, showing all zones even if empty."""
        # Clear previous widgets
        self.clear_layout(self.pedestrian_zones_layout)

        if not zone_counts:
            self.pedestrian_zones_layout.addWidget(self.create_no_zones_message("pedestrian"))
            return

        for zone_name, count in zone_counts.items():
            zone_group = QGroupBox(zone_name)
            zone_layout = QGridLayout()

            density = self.calculate_pedestrian_density(count)

            density_label = QLabel(f"Pedestrian Density: {density}")
            density_label.setStyleSheet(f"font-weight: bold; color: {self.get_density_color(density)};")
            zone_layout.addWidget(density_label, 0, 0, 1, 2)

            count_style = "font-weight: bold; color: #4a90e2;" if count > 0 else "color: gray;"
            self.add_count_row(zone_layout, "Count", count, count_style, 1)

            zone_group.setLayout(zone_layout)
            self.pedestrian_zones_layout.addWidget(zone_group)

    def create_no_zones_message(self, zone_type):
        """Creates a standardized 'no zones' message."""
        no_zones_label = QLabel(f"No {zone_type} zones configured")
        no_zones_label.setStyleSheet("font-style: italic; color: gray;")
        return no_zones_label

    def add_count_row(self, layout, label_text, count, style, row):
        """Adds a standardized count row to a layout."""
        label = QLabel(f"{label_text}:")
        count_label = QLabel(str(count))
        label.setStyleSheet(style)
        count_label.setStyleSheet(style)
        layout.addWidget(label, row, 0)
        layout.addWidget(count_label, row, 1)

    def calculate_traffic_density(self, total_vehicles: int) -> str:
        if total_vehicles < 5:
            return "Low"
        elif total_vehicles < 10:
            return "Medium"
        return "High"

    def calculate_pedestrian_density(self, count: int) -> str:
        if count < 3:
            return "Low"
        elif count < 7:
            return "Medium"
        return "High"

    def get_density_color(self, density: str) -> str:
        colors = {
            "Low": "green",
            "Medium": "orange",
            "High": "red"
        }
        return colors.get(density, "black")

    def clear_layout(self, layout):
        """Clears all widgets from a layout."""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def set_emergency_detected(self, detected):
        self.emergency_detected = detected
        color = "#0000FF" if detected else "#444444"
        self.emergency_indicator.setStyleSheet(f"""
            QFrame {{
                border: 2px solid gray;
                border-radius: 15px;
                background-color: {color};
            }}
        """)

    def set_accident_detected(self, detected):
        self.accident_detected = detected
        color = "#FF0000" if detected else "#444444"
        self.accident_indicator.setStyleSheet(f"""
            QFrame {{
                border: 2px solid gray;
                border-radius: 15px;
                background-color: {color};
            }}
        """)

    def update_traffic_light_status(self, intersection_data):
        """Updates traffic light status display."""
        self.clear_layout(self.traffic_light_layout)

        if not intersection_data:
            self._show_no_lights_message()
            return

        for intersection_id, data in intersection_data.items():
            intersection_widget = self._create_intersection_widget(intersection_id, data)
            self.traffic_light_layout.addWidget(intersection_widget)

    def _show_no_lights_message(self):
        """Display a message when no traffic lights are configured."""
        no_lights_label = QLabel("No traffic lights configured")
        no_lights_label.setStyleSheet("font-style: italic; color: gray;")
        self.traffic_light_layout.addWidget(no_lights_label)

    def _create_intersection_widget(self, intersection_id, data):
        """Create a widget for displaying an intersection's traffic lights."""
        intersection_group = QGroupBox(f"Intersection: {intersection_id}")
        intersection_layout = QGridLayout()

        # Add emergency and accident indicators if present
        row_offset = 0
        if data.get('is_emergency_active', False):
            emergency_label = QLabel("EMERGENCY VEHICLE PRIORITY ACTIVE")
            emergency_label.setStyleSheet("font-weight: bold; color: blue; background-color: yellow;")
            intersection_layout.addWidget(emergency_label, 0, 0, 1, 3)
            row_offset += 1

        if data.get('is_accident_mode', False):
            accident_label = QLabel("ACCIDENT RESPONSE ACTIVE - ALL LIGHTS RED")
            accident_label.setStyleSheet("font-weight: bold; color: white; background-color: red;")
            intersection_layout.addWidget(accident_label, row_offset, 0, 1, 3)
            row_offset += 1

        # Handle pedestrian phase indicator
        if data.get('is_pedestrian_phase', False):
            ped_label = QLabel("PEDESTRIAN CROSSING ACTIVE")
            ped_label.setStyleSheet("font-weight: bold; color: blue;")
            intersection_layout.addWidget(ped_label, row_offset, 0, 1, 3)
            row_offset += 1

        # Add traffic light indicators
        self._add_traffic_light_indicators(intersection_layout, data['lights'], row_offset)

        intersection_group.setLayout(intersection_layout)
        return intersection_group

    def _add_pedestrian_phase_indicator(self, layout, data):
        """Add pedestrian phase indicator to layout if active."""
        is_pedestrian_phase = data.get('is_pedestrian_phase', False)
        if is_pedestrian_phase:
            ped_label = QLabel("PEDESTRIAN CROSSING ACTIVE")
            ped_label.setStyleSheet("font-weight: bold; color: blue;")
            layout.addWidget(ped_label, 0, 0, 1, 3)
            return 1
        return 0

    def _add_traffic_light_indicators(self, layout, lights, row_offset):
        """Add traffic light indicators to the layout."""
        row = row_offset
        for light_info in lights:
            # Create indicator components
            light_indicator = self._create_light_indicator(light_info['state'])
            name_label, name_style = self._create_name_label(light_info)

            # Add to layout
            layout.addWidget(light_indicator, row, 0)
            layout.addWidget(name_label, row, 1)

            # Add time remaining label if active
            if light_info['is_active']:
                time_label = QLabel(f"{light_info.get('remaining', 0)}s")
                time_label.setStyleSheet(name_style)
                layout.addWidget(time_label, row, 2)

            row += 1

    def _create_light_indicator(self, state):
        """Create a colored indicator for a traffic light state."""
        light_indicator = QFrame()
        light_indicator.setFixedSize(20, 20)

        # Map state to color
        color_map = {
            'RED': "#FF0000",
            'GREEN': "#00FF00",
            'PEDESTRIAN': "#0000FF",
            'YELLOW': "#FFFF00"
        }
        color = color_map.get(state, "#FFFF00")

        light_indicator.setStyleSheet(f"""
            QFrame {{
                border: 2px solid gray;
                border-radius: 10px;
                background-color: {color};
            }}
        """)
        return light_indicator

    def _create_name_label(self, light_info):
        """Create a label for the traffic light name."""
        name_style = "font-weight: bold;" if light_info.get('is_active', False) else ""
        name_label = QLabel(light_info.get('name', 'Unknown'))
        name_label.setStyleSheet(name_style)
        return name_label, name_style
