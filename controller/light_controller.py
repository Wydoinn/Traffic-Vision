import time
from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json
import os

class TrafficLightState(Enum):
    """Represents the possible states of a traffic light."""
    RED = 0
    YELLOW = 1
    GREEN = 2
    PEDESTRIAN = 3

@dataclass
class TrafficLightConfig:
    """Configuration settings for a traffic light."""
    id: str
    name: str
    zone_id: str
    min_green_time: int = 16
    max_green_time: int = 60
    yellow_duration: int = 3
    position: Tuple[int, int] = (0, 0)
    pedestrian_min_time: int = 10
    pedestrian_max_time: int = 30
    emergency_buffer_time: int = 5

    def asdict(self):
        """Converts the config to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "zone_id": self.zone_id,
            "min_green_time": self.min_green_time,
            "max_green_time": self.max_green_time,
            "yellow_duration": self.yellow_duration,
            "position": list(self.position),
            "pedestrian_min_time": self.pedestrian_min_time,
            "pedestrian_max_time": self.pedestrian_max_time,
            "emergency_buffer_time": self.emergency_buffer_time
        }

class TrafficLight:
    """Represents a single traffic light with timing control."""
    def __init__(self, config: TrafficLightConfig):
        self.config = config
        self.state = TrafficLightState.RED
        self.last_state_change = time.time()
        self.current_duration = config.min_green_time
        self.time_remaining = 0
        self.pedestrian_duration = config.pedestrian_min_time

    def set_state(self, state: TrafficLightState, duration: Optional[int] = None):
        """Sets the traffic light to a new state with optional duration."""
        self.state = state
        self.last_state_change = time.time()

        if state == TrafficLightState.GREEN and duration is not None:
            self.current_duration = max(self.config.min_green_time,
                                      min(duration, self.config.max_green_time))
        elif state == TrafficLightState.YELLOW:
            self.current_duration = self.config.yellow_duration
        elif state == TrafficLightState.PEDESTRIAN and duration is not None:
            self.current_duration = max(self.config.pedestrian_min_time,
                                       min(duration, self.config.pedestrian_max_time))
        else:
            self.current_duration = 0

    def update(self):
        """Updates the traffic light state based on timing."""
        if self.state in [TrafficLightState.GREEN, TrafficLightState.PEDESTRIAN]:
            elapsed = time.time() - self.last_state_change
            if elapsed >= self.current_duration:
                if self.state == TrafficLightState.GREEN:
                    self.set_state(TrafficLightState.YELLOW)
                else:  # PEDESTRIAN state
                    self.set_state(TrafficLightState.RED)
                return True

        elif self.state == TrafficLightState.YELLOW:
            elapsed = time.time() - self.last_state_change
            if elapsed >= self.config.yellow_duration:
                self.set_state(TrafficLightState.RED)
                return True

        # Calculate time remaining in current state
        if self.state in [TrafficLightState.GREEN, TrafficLightState.YELLOW, TrafficLightState.PEDESTRIAN]:
            self.time_remaining = max(0, self.current_duration -
                                    (time.time() - self.last_state_change))

        return False

    def get_state_color(self):
        """Returns the color associated with the current state."""
        colors = {
            TrafficLightState.RED: (0, 0, 255),
            TrafficLightState.YELLOW: (0, 255, 255),
            TrafficLightState.GREEN: (0, 255, 0),
            TrafficLightState.PEDESTRIAN: (255, 0, 0)
        }
        return colors[self.state]

class TrafficLightController:
    """
    Controls a system of traffic lights based on traffic flow data.
    Implements adaptive timing strategies for multiple intersections.
    """
    def __init__(self, config_file: str = None):
        self.traffic_lights: Dict[str, TrafficLight] = {}
        self.intersections: Dict[str, List[str]] = {}
        self.active_phase: Dict[str, str] = {}
        self.phase_start_time: Dict[str, float] = {}
        self.adaptive_mode = True
        self.last_traffic_data = {}
        self.pedestrian_phase_active = {}
        self.last_pedestrian_data = {}
        self.pedestrian_phase_complete = {}

        self.adaptive_mode_changed = False
        self.last_adaptive_mode = True

        self.emergency_active = {}
        self.emergency_vehicle_zone = {}
        self.emergency_start_time = {}
        self.emergency_buffer_active = {}
        self.accident_detected = False
        self.accident_zones = set()

        if config_file and os.path.exists(config_file):
            self.load_configuration(config_file)

    def add_traffic_light(self, config: TrafficLightConfig):
        """Adds a new traffic light to the controller."""
        light = TrafficLight(config)
        self.traffic_lights[config.id] = light
        return light

    def create_intersection(self, intersection_id: str, traffic_light_ids: List[str]):
        """Creates an intersection with the specified traffic lights."""
        valid_ids = [tid for tid in traffic_light_ids if tid in self.traffic_lights]
        if valid_ids:
            self.intersections[intersection_id] = valid_ids
            # Set the first light to green initially
            self.active_phase[intersection_id] = valid_ids[0]
            self.phase_start_time[intersection_id] = time.time()
            self.traffic_lights[valid_ids[0]].set_state(TrafficLightState.GREEN)
            self.pedestrian_phase_active[intersection_id] = False
            self.pedestrian_phase_complete[intersection_id] = False
            # Set all other lights to red
            for tid in valid_ids[1:]:
                self.traffic_lights[tid].set_state(TrafficLightState.RED)
        else:
            raise ValueError(f"No valid traffic lights for intersection {intersection_id}")

    def update_traffic_data(self, traffic_data: Dict[str, Dict[str, int]], pedestrian_data: Optional[Dict[str, int]] = None):
        """
        Updates traffic flow data used for adaptive timing.
        Now also accepts pedestrian count data.
        """
        self.last_traffic_data = traffic_data
        if pedestrian_data:
            self.last_pedestrian_data = pedestrian_data
            for intersection_id in self.intersections.keys():
                if not self.pedestrian_phase_active.get(intersection_id, False):
                    self.pedestrian_phase_complete[intersection_id] = False

    def report_emergency_vehicle(self, zone_id: str, is_present: bool):
        """
        Reports emergency vehicle presence in a specific zone.
        Activates emergency priority mode for the affected intersection.
        """
        if not zone_id:
            return False

        affected_intersection = None
        affected_light = None

        # Find which intersection and light this zone belongs to
        for light_id, light in self.traffic_lights.items():
            if light.config.zone_id == zone_id:
                affected_light = light_id
                # Find which intersection this light belongs to
                for intersection_id, light_ids in self.intersections.items():
                    if light_id in light_ids:
                        affected_intersection = intersection_id
                        break
                break

        if not affected_intersection or not affected_light:
            return False

        # Update emergency status
        if is_present and not self.emergency_active.get(affected_intersection, False):
            # Activate emergency mode
            self.emergency_active[affected_intersection] = True
            self.emergency_vehicle_zone[affected_intersection] = zone_id
            self.emergency_start_time[affected_intersection] = time.time()
            self.emergency_buffer_active[affected_intersection] = False

            # Set green light for emergency vehicle lane, red for all others
            self._set_emergency_priority(affected_intersection, affected_light)
            return True

        elif not is_present and self.emergency_active.get(affected_intersection, False):
            # Emergency vehicle has passed, start buffer timing
            if not self.emergency_buffer_active.get(affected_intersection, False):
                self.emergency_buffer_active[affected_intersection] = True
                self.emergency_start_time[affected_intersection] = time.time()

        return False

    def report_accident(self, accident_detected: bool, zone_id: Optional[str] = None):
        """
        Reports accident detection status.
        Sets all traffic lights to red when an accident is detected.
        """
        if accident_detected:
            if not self.accident_detected:
                self.accident_detected = True
                if zone_id:
                    self.accident_zones.add(zone_id)
                # Set all lights to red immediately
                self._handle_accident_response()
                return True
            elif zone_id:
                self.accident_zones.add(zone_id)
        else:
            # Clear accident state if all accident zones are clear
            if zone_id:
                self.accident_zones.discard(zone_id)

            if not self.accident_zones and self.accident_detected:
                self.accident_detected = False
                return True

        return False

    def _set_emergency_priority(self, intersection_id: str, priority_light_id: str):
        """Sets emergency priority for a specific light in an intersection."""
        for light_id in self.intersections[intersection_id]:
            if light_id == priority_light_id:
                # Set priority light to green
                self.traffic_lights[light_id].set_state(TrafficLightState.GREEN,
                                                      self.traffic_lights[light_id].config.max_green_time)
                self.active_phase[intersection_id] = light_id
            else:
                # Set all other lights to red
                self.traffic_lights[light_id].set_state(TrafficLightState.RED)

    def _handle_accident_response(self):
        """Sets all traffic lights to red in response to an accident."""
        for light_id in self.traffic_lights:
            self.traffic_lights[light_id].set_state(TrafficLightState.RED)

    def _check_emergency_buffer(self, intersection_id: str) -> bool:
        """
        Checks if the emergency buffer time has elapsed.
        Returns True if emergency mode should be deactivated.
        """
        if not self.emergency_buffer_active.get(intersection_id, False):
            return False

        buffer_time = 5
        # Get buffer time from first light in intersection
        if self.intersections[intersection_id]:
            first_light = self.traffic_lights[self.intersections[intersection_id][0]]
            buffer_time = first_light.config.emergency_buffer_time

        elapsed = time.time() - self.emergency_start_time.get(intersection_id, 0)
        if elapsed >= buffer_time:
            # Buffer time elapsed, deactivate emergency mode
            self.emergency_active[intersection_id] = False
            self.emergency_buffer_active[intersection_id] = False
            self.emergency_vehicle_zone.pop(intersection_id, None)
            return True

        return False

    def update_all_lights(self):
        """Updates all traffic lights and manages phase changes at intersections."""
        changes_occurred = False

        # Reset adaptive mode changed flag at the beginning of each update cycle
        self.adaptive_mode_changed = self.adaptive_mode != self.last_adaptive_mode
        self.last_adaptive_mode = self.adaptive_mode

        # First handle accident response - highest priority
        if self.accident_detected:
            # Keep all lights red during accident
            self._handle_accident_response()
            return False

        # Update emergency status for intersections with active emergency mode
        for intersection_id in list(self.emergency_active.keys()):
            if self.emergency_active[intersection_id]:
                if self._check_emergency_buffer(intersection_id):
                    changes_occurred = True

        for light_id, light in self.traffic_lights.items():
            if light.update():
                changes_occurred = True

        # Then check each intersection for phase changes
        for intersection_id, light_ids in self.intersections.items():
            # Skip intersections in emergency mode
            if self.emergency_active.get(intersection_id, False):
                continue

            if intersection_id not in self.active_phase:
                # Initialize phase if not set
                self.active_phase[intersection_id] = light_ids[0]
                self.phase_start_time[intersection_id] = time.time()
                self.traffic_lights[light_ids[0]].set_state(TrafficLightState.GREEN)
                self.pedestrian_phase_active[intersection_id] = False
                self.pedestrian_phase_complete[intersection_id] = False
                changes_occurred = True
                continue

            active_light_id = self.active_phase[intersection_id]
            active_light = self.traffic_lights[active_light_id]

            # Check if we're in pedestrian phase
            if self.pedestrian_phase_active.get(intersection_id, False):
                # If any light is still in PEDESTRIAN state, continue
                if active_light.state == TrafficLightState.PEDESTRIAN:
                    continue

                # All lights have finished pedestrian phase, start next regular cycle
                self.pedestrian_phase_active[intersection_id] = False
                self.pedestrian_phase_complete[intersection_id] = True

                # Find next light in sequence
                current_idx = light_ids.index(active_light_id)
                next_idx = (current_idx + 1) % len(light_ids)
                next_light_id = light_ids[next_idx]

                # Calculate adaptive timing for next light
                adaptive_duration = self.calculate_adaptive_timing(
                    intersection_id, next_light_id)

                # Activate next light
                self.traffic_lights[next_light_id].set_state(
                    TrafficLightState.GREEN, adaptive_duration)
                self.active_phase[intersection_id] = next_light_id
                self.phase_start_time[intersection_id] = time.time()
                changes_occurred = True

            elif active_light.state == TrafficLightState.RED:
                current_idx = light_ids.index(active_light_id)
                next_idx = (current_idx + 1) % len(light_ids)

                # Reset pedestrian phase flag when we complete a full cycle
                if next_idx == 0:
                    self.pedestrian_phase_complete[intersection_id] = False

                if next_idx == 0 and not self.pedestrian_phase_complete.get(intersection_id, False):
                    # Start pedestrian phase
                    self.pedestrian_phase_active[intersection_id] = True
                    self.pedestrian_phase_complete[intersection_id] = False

                    # Calculate pedestrian timing
                    ped_duration = self.calculate_pedestrian_timing(intersection_id)

                    # Set all lights in this intersection to pedestrian state
                    for light_id in light_ids:
                        self.traffic_lights[light_id].set_state(
                            TrafficLightState.PEDESTRIAN, ped_duration)

                    changes_occurred = True
                else:
                    # Normal light transition
                    next_light_id = light_ids[next_idx]

                    # If we're back at the first light, reset the pedestrian phase flag
                    if next_idx == 0:
                        self.pedestrian_phase_complete[intersection_id] = False

                    # Calculate adaptive timing for next light
                    adaptive_duration = self.calculate_adaptive_timing(
                        intersection_id, next_light_id)

                    # Activate next light
                    self.traffic_lights[next_light_id].set_state(
                        TrafficLightState.GREEN, adaptive_duration)
                    self.active_phase[intersection_id] = next_light_id
                    self.phase_start_time[intersection_id] = time.time()
                    changes_occurred = True

        return changes_occurred

    def calculate_adaptive_timing(self, intersection_id: str, next_light_id: str) -> int:
        """
        Calculates adaptive green light duration based on current traffic conditions.
        """
        if not self.adaptive_mode:
            # When adaptive mode is off, use max_green_time
            return self.traffic_lights[next_light_id].config.max_green_time

        if next_light_id not in self.traffic_lights:
            return self.traffic_lights[next_light_id].config.min_green_time

        zone_id = self.traffic_lights[next_light_id].config.zone_id

        # If no traffic data for this zone, use default timing
        if zone_id not in self.last_traffic_data:
            return self.traffic_lights[next_light_id].config.min_green_time

        # Calculate traffic volume for this zone
        zone_data = self.last_traffic_data[zone_id]

        # Weight different vehicle types differently
        weighted_sum = 0
        if isinstance(zone_data, dict):
            # Apply weights to different vehicle types
            weights = {
                "car": 1.0,
                "truck": 2.0,
                "bus": 2.0,
                "motorcycle": 0.5,
                "bicycle": 0.3
            }

            for vehicle_type, count in zone_data.items():
                weight = weights.get(vehicle_type.lower(), 1.0)
                weighted_sum += count * weight

        # Basic adaptive timing formula
        base_time = self.traffic_lights[next_light_id].config.min_green_time
        max_time = self.traffic_lights[next_light_id].config.max_green_time

        # Clamp timing between min and max
        if weighted_sum <= 2:
            return base_time
        elif weighted_sum >= 20:
            return max_time
        else:
            # Linear scaling between min and max based on weighted vehicle count
            factor = (weighted_sum - 2) / 18.0
            return int(base_time + factor * (max_time - base_time))

    def calculate_pedestrian_timing(self, intersection_id: str) -> int:
        """
        Calculates adaptive pedestrian crossing duration based on pedestrian counts.
        """
        if not self.adaptive_mode:
            # Use max pedestrian time when not in adaptive mode
            sample_light_id = self.intersections[intersection_id][0]
            return self.traffic_lights[sample_light_id].config.pedestrian_max_time

        # Get total pedestrian count across all pedestrian zones
        total_pedestrians = 0
        for zone_id, count in self.last_pedestrian_data.items():
            total_pedestrians += count

        # Sample light to get configuration values
        sample_light_id = self.intersections[intersection_id][0]
        min_time = self.traffic_lights[sample_light_id].config.pedestrian_min_time
        max_time = self.traffic_lights[sample_light_id].config.pedestrian_max_time

        # Calculate adaptive timing based on pedestrian count
        if total_pedestrians <= 2:
            return min_time
        elif total_pedestrians >= 15:
            return max_time
        else:
            # Linear scaling
            factor = (total_pedestrians - 2) / 13.0
            return int(min_time + factor * (max_time - min_time))

    def get_light_states(self):
        """Returns the current state of all traffic lights."""
        states = {}
        for light_id, light in self.traffic_lights.items():
            states[light_id] = {
                'state': light.state.name,
                'color': light.get_state_color(),
                'remaining': int(light.time_remaining),
                'position': light.config.position,
                'name': light.config.name
            }
        return states

    def toggle_adaptive_mode(self):
        """Toggles between adaptive and fixed timing modes."""
        self.adaptive_mode = not self.adaptive_mode
        self.adaptive_mode_changed = True
        return self.adaptive_mode

    def save_configuration(self, file_path: str):
        """Saves the current traffic light configuration to a file."""
        config_data = {
            "traffic_lights": [],
            "intersections": {}
        }

        # Save traffic light configurations
        for light_id, light in self.traffic_lights.items():
            config_data["traffic_lights"].append(light.config.asdict())

        # Save intersection configurations
        for intersection_id, light_ids in self.intersections.items():
            config_data["intersections"][intersection_id] = light_ids

        # Write to file
        with open(file_path, 'w') as f:
            json.dump(config_data, f, indent=4)

    def load_configuration(self, file_path: str):
        """Loads traffic light configuration from a file."""
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)

            # Clear existing configuration
            self.traffic_lights = {}
            self.intersections = {}
            self.active_phase = {}

            # Load traffic lights
            for light_config in config_data.get("traffic_lights", []):
                config = TrafficLightConfig(
                    id=light_config["id"],
                    name=light_config["name"],
                    zone_id=light_config["zone_id"],
                    min_green_time=light_config.get("min_green_time", 16),
                    max_green_time=light_config.get("max_green_time", 60),
                    yellow_duration=light_config.get("yellow_duration", 3),
                    pedestrian_min_time=light_config.get("pedestrian_min_time", 10),
                    pedestrian_max_time=light_config.get("pedestrian_max_time", 30),
                    position=tuple(light_config.get("position", [0, 0])),
                    emergency_buffer_time=light_config.get("emergency_buffer_time", 5)
                )
                self.add_traffic_light(config)

            # Load intersections
            for intersection_id, light_ids in config_data.get("intersections", {}).items():
                try:
                    self.create_intersection(intersection_id, light_ids)
                except ValueError as e:
                    print(f"Error creating intersection {intersection_id}: {e}")

            return True
        except Exception as e:
            print(f"Error loading traffic light configuration: {e}")
            return False

    def get_intersections_info(self):
        """Returns information about all intersections for display."""
        result = {}
        for intersection_id, light_ids in self.intersections.items():
            active_light_id = self.active_phase.get(intersection_id)
            lights_info = []
            is_pedestrian_phase = self.pedestrian_phase_active.get(intersection_id, False)
            is_emergency_active = self.emergency_active.get(intersection_id, False)
            is_accident_mode = self.accident_detected

            for light_id in light_ids:
                light = self.traffic_lights[light_id]
                lights_info.append({
                    'id': light_id,
                    'name': light.config.name,
                    'state': light.state.name,
                    'is_active': light_id == active_light_id,
                    'remaining': int(light.time_remaining),
                    'is_pedestrian_phase': is_pedestrian_phase
                })

            result[intersection_id] = {
                'lights': lights_info,
                'active_phase': active_light_id,
                'is_pedestrian_phase': is_pedestrian_phase,
                'is_emergency_active': is_emergency_active,
                'is_accident_mode': is_accident_mode,
                'is_adaptive_mode': self.adaptive_mode,
                'adaptive_mode_changed': self.adaptive_mode_changed
            }

        return result

    def visualize_traffic_lights(self, frame, scale_factor=1.0):
        """
        Draws traffic lights on the provided frame.
        """
        import cv2

        for light_id, light_info in self.get_light_states().items():
            position = light_info['position']
            scaled_pos = (int(position[0] * scale_factor), int(position[1] * scale_factor))
            color = light_info['color']
            state = light_info['state']
            remaining = light_info['remaining']
            name = light_info['name']

            # Draw traffic light indicator
            radius = int(15 * scale_factor)
            cv2.circle(frame, scaled_pos, radius, color, -1)
            cv2.circle(frame, scaled_pos, radius, (255, 255, 255), 2)

            # Add text for light name and remaining time
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5 * scale_factor
            text_pos = (scaled_pos[0] + radius + 5, scaled_pos[1])

            # Draw light name
            cv2.putText(frame, name, text_pos, font, font_scale,
                       (255, 255, 255), 2, cv2.LINE_AA)

            # Draw remaining time if applicable
            if state != 'RED':
                time_pos = (text_pos[0], text_pos[1] + int(20 * scale_factor))

                # Add "PED" indicator if in pedestrian phase
                if state == 'PEDESTRIAN':
                    ped_text = "PED: " + str(remaining) + "s"
                    cv2.putText(frame, ped_text, time_pos, font, font_scale,
                               color, 2, cv2.LINE_AA)
                else:
                    cv2.putText(frame, f"{remaining}s", time_pos, font, font_scale,
                               color, 2, cv2.LINE_AA)

        return frame
