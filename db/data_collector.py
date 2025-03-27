import time
import threading
import numpy as np
from typing import Dict, List, Any, Optional
from queue import Queue
import cv2

from db.database import TrafficDatabase


class TrafficDataCollector:
    """
    Collects and stores traffic data for analysis and visualization.
    Runs continuously in a background thread and stores data in SQLite.
    """
    def __init__(self, db_path: str = "data/traffic_data.db", collection_interval: float = 5.0):
        """
        Initialize data collector with specified collection interval.
        """
        self.database = TrafficDatabase(db_path)
        self.collection_interval = collection_interval
        self.collection_thread = None
        self.is_collecting = False
        self.current_session_id = None
        self.last_collection_time = 0
        self.zone_manager = None
        self.data_queue = Queue()
        self.processing_thread = None
        self.stop_event = threading.Event()
        self.start_processing_thread()

    def start_processing_thread(self):
        """Start background thread for database operations."""
        self.processing_thread = threading.Thread(target=self._process_queue)
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def _process_queue(self):
        """Process queued data records in background."""
        while not self.stop_event.is_set():
            try:
                if self.data_queue.empty():
                    time.sleep(0.1)
                    continue

                record_type, data = self.data_queue.get()
                session_id = self.current_session_id

                if session_id is None:
                    self.data_queue.task_done()
                    continue

                if record_type == "vehicle_counts":
                    self.database.record_vehicle_counts(session_id, data)
                elif record_type == "pedestrian_counts":
                    self.database.record_pedestrian_counts(session_id, data)
                elif record_type == "vehicle_speeds":
                    self.database.record_vehicle_speeds(session_id, data)
                elif record_type == "traffic_lights":
                    self.database.record_traffic_light_states(session_id, data)
                elif record_type == "event":
                    event_type, details = data
                    self.database.record_event(session_id, event_type, details)
                elif record_type == "heatmap":
                    zone_name, avg, max_val = data
                    self.database.record_heatmap_data(session_id, zone_name, avg, max_val)

                self.data_queue.task_done()

            except Exception as e:
                print(f"Error processing data queue: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(1)

    def set_zone_manager(self, zone_manager):
        """Set reference to the ZoneManager instance."""
        self.zone_manager = zone_manager

    def start_collection(self, video_path: str = None, notes: str = None):
        """Start collecting traffic data."""
        if self.is_collecting:
            print("Data collection is already running")
            return False

        # Start a new database session
        self.current_session_id = self.database.start_new_session(video_path, notes)
        if self.current_session_id < 0:
            print("Failed to start database session")
            return False

        self.is_collecting = True
        self.collection_thread = threading.Thread(target=self._collection_loop)
        self.collection_thread.daemon = True
        self.collection_thread.start()

        print(f"Started traffic data collection (Session ID: {self.current_session_id})")
        return True

    def stop_collection(self):
        """Stop collecting traffic data."""
        if not self.is_collecting:
            return False

        self.is_collecting = False
        if self.collection_thread:
            self.collection_thread.join(timeout=2.0)
            self.collection_thread = None

        if self.current_session_id:
            self.database.end_session(self.current_session_id)
            session_id = self.current_session_id
            self.current_session_id = None
            print(f"Stopped traffic data collection (Session ID: {session_id})")

        return True

    def _collection_loop(self):
        """Main collection loop that runs in background thread."""
        while self.is_collecting:
            current_time = time.time()

            # Check if it's time to collect data
            if current_time - self.last_collection_time >= self.collection_interval:
                self._collect_data()
                self.last_collection_time = current_time
            # Sleep to avoid high CPU usage
            time.sleep(0.1)

    def _collect_data(self):
        """Collect and store all traffic metrics."""
        if not self.zone_manager:
            return

        try:
            self._collect_vehicle_counts()
            self._collect_pedestrian_counts()
            self._collect_vehicle_speeds()
            self._collect_traffic_light_states()
            self._collect_events()
            self._collect_heatmap_data()
        except Exception as e:
            print(f"Error collecting traffic data: {e}")
            import traceback
            traceback.print_exc()

    def _collect_vehicle_counts(self):
        """Collect and store vehicle counts by zone."""
        if not self.zone_manager:
            return

        try:
            zone_vehicle_counts = self.zone_manager.get_zone_vehicle_counts()
            if zone_vehicle_counts:
                self.data_queue.put(("vehicle_counts", zone_vehicle_counts))
        except Exception as e:
            print(f"Error collecting vehicle counts: {e}")

    def _collect_pedestrian_counts(self):
        """Collect and store pedestrian counts by zone."""
        if not self.zone_manager:
            return

        try:
            zone_pedestrian_counts = self.zone_manager.get_zone_pedestrian_counts()
            if zone_pedestrian_counts:
                self.data_queue.put(("pedestrian_counts", zone_pedestrian_counts))
        except Exception as e:
            print(f"Error collecting pedestrian counts: {e}")

    def _collect_vehicle_speeds(self):
        """Collect and store vehicle speed data."""
        if not self.zone_manager:
            return

        try:
            if hasattr(self.zone_manager, 'track_history') and hasattr(self.zone_manager, 'speed_data'):
                speeds_data = []

                # Match tracker_ids to class names and collect speed data
                for tracker_id, speed_values in self.zone_manager.speed_data.items():
                    if not speed_values:
                        continue

                    # Get the last speed value for this tracker
                    speed = speed_values[-1] if speed_values else 0

                    # Try to determine vehicle type if possible
                    vehicle_type = "unknown"

                    # Get the latest zone_detections from zone_manager
                    zone_detections = getattr(self.zone_manager, 'get_latest_zone_detections', lambda: None)()

                    if zone_detections is not None and hasattr(self.zone_manager, 'zone_model'):
                        # Look for the tracker_id in the current detections
                        for i, detection_id in enumerate(zone_detections.tracker_id):
                            if detection_id == tracker_id:
                                class_id = zone_detections.class_id[i]
                                vehicle_type = self.zone_manager.zone_model.names.get(class_id, "unknown")
                                break

                    speeds_data.append({
                        "tracker_id": tracker_id,
                        "vehicle_type": vehicle_type,
                        "speed": speed
                    })

                if speeds_data:
                    self.data_queue.put(("vehicle_speeds", speeds_data))
        except Exception as e:
            print(f"Error collecting vehicle speeds: {e}")

    def _collect_traffic_light_states(self):
        """Collect and store traffic light states."""
        if not self.zone_manager or not hasattr(self.zone_manager, 'traffic_light_controller'):
            return

        try:
            traffic_light_controller = self.zone_manager.traffic_light_controller
            if traffic_light_controller:
                intersection_data = traffic_light_controller.get_intersections_info()

                # Check if we have valid intersection data
                if intersection_data:
                    # Record the current state
                    self.data_queue.put(("traffic_lights", intersection_data))

                    # Explicitly record mode changes as separate events
                    for intersection_id, data in intersection_data.items():
                        if data.get('adaptive_mode_changed', False):
                            is_adaptive = data.get('is_adaptive_mode', True)
                            mode_str = "Adaptive" if is_adaptive else "Fixed"
                            self.data_queue.put((
                                "event",
                                ("traffic_light_mode_change", f"Traffic light mode changed to {mode_str}")
                            ))
        except Exception as e:
            print(f"Error collecting traffic light states: {e}")

    def _collect_events(self):
        """Collect and store emergency and accident events."""
        if not self.zone_manager:
            return

        try:
            # Check for emergency vehicles
            if self.zone_manager.is_emergency_detected():
                # Get specific emergency vehicle types and counts
                emergency_vehicles = self.zone_manager.get_emergency_vehicles()

                # Record each type of emergency vehicle detected
                for vehicle_type, count in emergency_vehicles.items():
                    if count > 0:
                        details = f"{vehicle_type.capitalize()} detected (count: {count})"
                        self.data_queue.put(("event", ("emergency", details)))

            # Check for accidents
            if self.zone_manager.is_accident_detected():
                self.data_queue.put(("event", ("accident", "Accident detected")))
        except Exception as e:
            print(f"Error collecting events: {e}")

    def _collect_heatmap_data(self):
        """Collect and store heatmap data for traffic density analysis."""
        if not self.zone_manager or not hasattr(self.zone_manager, 'persistent_heatmap'):
            return

        try:
            # Calculate heatmap stats per vehicle zone
            heatmap = self.zone_manager.persistent_heatmap

            for zone_type in self.zone_manager.zones:
                for zone_name, zone_info in self.zone_manager.zones[zone_type].items():
                    zone = zone_info['zone']
                    # Create a mask for this zone
                    mask = np.zeros_like(heatmap, dtype=np.uint8)
                    polygon = zone.polygon.reshape((-1, 1, 2))
                    cv2.fillPoly(mask, [polygon.astype(np.int32)], 1)

                    # Apply mask to heatmap
                    zone_heatmap = heatmap * mask

                    # Calculate statistics (ignore zeros)
                    nonzero = zone_heatmap[zone_heatmap > 0] if np.any(zone_heatmap > 0) else np.array([0])
                    avg_intensity = float(np.mean(nonzero))
                    max_intensity = float(np.max(nonzero)) if np.any(nonzero) else 0

                    # Record zone heatmap data
                    self.data_queue.put(("heatmap", (zone_name, avg_intensity, max_intensity)))
        except Exception as e:
            print(f"Error collecting heatmap data: {e}")

    def get_session_stats(self, session_id: Optional[int] = None) -> Dict[str, Any]:
        """Get statistics for current or specified session."""
        if session_id is None:
            session_id = self.current_session_id

        if session_id is None:
            return {}

        return self.database.get_session_stats(session_id)

    def get_available_sessions(self) -> List[Dict[str, Any]]:
        """Get list of all recording sessions."""
        return self.database.get_available_sessions()

    def shutdown(self):
        """Clean up resources and close database connection."""
        self.stop_collection()

        # Stop processing thread
        self.stop_event.set()
        if self.processing_thread:
            self.processing_thread.join(timeout=2.0)

        # Close database connection
        self.database.close()
