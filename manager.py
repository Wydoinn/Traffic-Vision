import cv2
import numpy as np
import supervision as sv
import json
from typing import Dict, Tuple, Callable
import time
from collections import defaultdict

from utils.constants import *
from utils.notifier import TelegramNotifier

class ZoneManager:
    """
    Manages zones, performs object detection, tracking, and heatmap generation.
    Supports separate vehicle and pedestrian zones.
    """
    def __init__(self, frame_width: int, frame_height: int, video_path: str, zone_model,
                 emergency_model, accident_model, inference_settings, heatmap_settings):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.video_path = video_path
        self.zones: Dict[str, Dict[str, any]] = {ZONE_TYPE_VEHICLE: {}, ZONE_TYPE_PEDESTRIAN: {}}

        # Add zone-specific counters
        self.zone_vehicle_counts = {}
        self.zone_pedestrian_counts = {}

        self.zone_model = zone_model
        self.emergency_model = emergency_model
        self.accident_model = accident_model

        # Get FPS for tracker configuration
        self.fps = self.get_video_fps()

        # Initialize trackers with default settings
        self.zone_tracker = sv.ByteTrack()
        self.emergency_tracker = sv.ByteTrack()
        self.accident_tracker = sv.ByteTrack()

        self.inference_settings = inference_settings
        self.heatmap_settings = heatmap_settings

        self.vehicle_counts = {
            "bicycle": 0, "car": 0, "motorcycle": 0, "bus": 0, "truck": 0
        }
        self.pedestrian_count = 0
        self.emergency_detected = False
        self.accident_detected = False

        # Add accident notification attributes
        self.telegram_notifier = None
        self.last_accident_notification_time = 0
        self.accident_notification_cooldown = 30
        self.accident_frames = []

        # Speed estimation attributes
        self.track_history = {}
        self.emergency_track_history = {}
        self.vehicle_classes = ["bicycle", "car", "motorcycle", "bus", "truck"]
        self.ppm = 8.8
        self.speed_smoothing_window = 5
        self.speed_data = defaultdict(list)
        self.emergency_speed_data = defaultdict(list)

        if self.frame_width <= 0 or self.frame_height <= 0:
            self.infer_frame_dimensions_from_video()

        self.persistent_heatmap = np.zeros((self.frame_height, self.frame_width), dtype=np.float32)
        self.gaussian_kernels = {}

        # Track maintenance attributes
        self.last_track_cleanup_time = time.time()
        self.track_cleanup_interval = 5.0

        # Add traffic light integration
        self.traffic_light_controller = None
        self.show_traffic_lights = False

    def get_video_fps(self):
        """Gets the FPS of the video file."""
        try:
            cap = cv2.VideoCapture(self.video_path)
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS)
                cap.release()
                return fps if fps > 0 else 30.0
            return 30.0
        except Exception as e:
            print(f"Error getting FPS: {e}")
            return 30.0

    def infer_frame_dimensions_from_video(self):
        """Infers frame width and height from the video file."""
        cap = cv2.VideoCapture(self.video_path)
        if cap.isOpened():
            self.frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
        else:
            raise ValueError("Could not determine frame dimensions from video and no dimensions provided.")

    def reset_heatmap(self):
        """Resets the persistent heatmap to zero."""
        self.persistent_heatmap = np.zeros((self.frame_height, self.frame_width), dtype=np.float32)

    def create_zones_interactive(self, num_zones: int, zone_type: str, callback: Callable[[bool, str], None]):
        """
        Creates specified number of zones interactively in a single window.
        """
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print("Error opening video stream")
            callback(False, zone_type)
            return

        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("Failed to capture frame")
            callback(False, zone_type)
            return

        resized_frame = cv2.resize(frame, (self.frame_width, self.frame_height))
        zone_name_prefix = zone_type.capitalize() + " Zone"
        window_name = f"Creating {zone_type.capitalize()} Zones"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, self.frame_width, self.frame_height)

        all_polygons = []

        for i in range(1, num_zones + 1):
            current_zone_name = f"{zone_name_prefix} {i}"
            polygon = self.create_single_polygon(resized_frame, current_zone_name, window_name)
            if polygon is None:
                print(f"Zone creation cancelled for {current_zone_name}")
                cv2.destroyAllWindows()
                callback(False, zone_type)
                return
            all_polygons.append((current_zone_name, polygon))

        cv2.destroyAllWindows()

        # Store created zones
        for zone_name, polygon in all_polygons:
            self.zones[zone_type][zone_name] = {
                'zone': sv.PolygonZone(polygon=polygon)
            }
        callback(True, zone_type)

    def create_single_polygon(self, frame: np.ndarray, zone_name: str, window_name: str) -> np.ndarray:
        """
        Interactively creates a polygon zone using mouse clicks within a given window.
        """
        points = []
        clone = frame.copy()

        def mouse_callback(event, x, y, flags, param):
            nonlocal clone, points
            if event == cv2.EVENT_LBUTTONDOWN:
                points.append([x, y])
                clone = frame.copy()
                for pt in points:
                    cv2.circle(clone, tuple(pt), 5, (0, 255, 0), -1)
                if len(points) >= 2:
                    pts = np.array(points, np.int32)
                    pts = pts.reshape((-1,1,2))
                    cv2.polylines(clone, [pts], isClosed=False, color=(0, 255, 0), thickness=2)
                cv2.imshow(window_name, clone)

        cv2.setMouseCallback(window_name, mouse_callback)
        cv2.imshow(window_name, clone)

        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 13: # Enter key
                if len(points) >= 3:
                    return np.array(points)
                else:
                    print("At least 3 points required")

            elif key == 27: # Esc key
                return None

            elif key == 127 or key== 8: # Delete key
                if points:
                    points.pop()
                    clone = frame.copy()
                    for pt in points:
                        cv2.circle(clone, tuple(pt), 5, (0, 255, 0), -1)
                    if len(points) >= 2:
                        pts = np.array(points, np.int32)
                        pts = pts.reshape((-1,1,2))
                        cv2.polylines(clone, [pts], isClosed=False, color=(0, 255, 0), thickness=2)
                    cv2.imshow(window_name, clone)


    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Processes a single video frame for object detection, tracking, and heatmap, considering zone types.
        """
        resized_frame = cv2.resize(frame, (self.frame_width, self.frame_height))
        common_inference_params = self.get_common_inference_params()

        # Periodically clean up stale tracks
        current_time = time.time()
        if current_time - self.last_track_cleanup_time > self.track_cleanup_interval:
            self._cleanup_stale_tracks()
            self.last_track_cleanup_time = current_time

        # Run detections for available models
        zone_results = self.run_detection(self.zone_model, resized_frame, MODEL_TYPE_ZONE, common_inference_params) if self.zone_model else None
        emergency_results = self.run_detection(self.emergency_model, resized_frame, MODEL_TYPE_EMERGENCY, common_inference_params) if self.emergency_model else None
        accident_results = self.run_detection(self.accident_model, resized_frame, MODEL_TYPE_ACCIDENT, common_inference_params) if self.accident_model else None

        # Process detection results
        zone_detections, emergency_detections, accident_detections = self._process_detection_results(
            zone_results, emergency_results, accident_results)

        # Calculate speeds
        vehicle_speeds, emergency_speeds = self._calculate_speeds(zone_detections, emergency_detections)

        # Generate visual output
        heatmap_frame = self.generate_heatmap(resized_frame, zone_detections)
        annotated_frame = self._create_annotated_frame(
            resized_frame, zone_detections, emergency_detections,
            accident_detections, vehicle_speeds, emergency_speeds)

        if self.traffic_light_controller:
            self._update_traffic_light_system(annotated_frame)

        self.update_counts(zone_detections)

        # Check for accident and send notification if necessary
        self.emergency_detected = len(emergency_detections) > 0
        prev_accident_detected = self.accident_detected
        self.accident_detected = len(accident_detections) > 0

        # Handle accident notifications
        if self.accident_detected:
            if len(self.accident_frames) < 5:
                self.accident_frames.append(annotated_frame.copy())
            else:
                self.accident_frames.pop(0)
                self.accident_frames.append(annotated_frame.copy())

            # Send notification if this is a new accident detection or cooldown has passed
            if (not prev_accident_detected or
                (current_time - self.last_accident_notification_time > self.accident_notification_cooldown)):
                self._send_accident_notification(annotated_frame)
        else:
            self.accident_frames.clear()

        return annotated_frame, heatmap_frame

    def _send_accident_notification(self, frame: np.ndarray):
        """Send accident notification with the current frame."""
        # Check if notification is configured
        if not self.telegram_notifier:
            return

        # Get the best frame to send (middle frame of accident sequence if available)
        notification_frame = frame
        if len(self.accident_frames) >= 3:
            notification_frame = self.accident_frames[len(self.accident_frames) // 2]
        elif len(self.accident_frames) > 0:
            notification_frame = self.accident_frames[-1]

        # Get accident location information
        location_info = self._determine_accident_location()

        # Send notification
        success = self.telegram_notifier.send_accident_notification(
            image=notification_frame,
            location=location_info,
            details=f"Accident detected in video: {os.path.basename(self.video_path)}"
        )

        if success:
            self.last_accident_notification_time = time.time()
            print(f"Accident notification sent at {time.strftime('%H:%M:%S')}")

    def _determine_accident_location(self):
        """Determine the location of the accident based on active zones."""
        # If we have accident detections and zones, try to locate the accident in a specific zone
        if hasattr(self, 'accident_detections') and len(self.accident_detections) > 0:
            for zone_type in self.zones:
                for zone_name, zone_info in self.zones[zone_type].items():
                    if zone_info['zone'].trigger(self.accident_detections):
                        return f"Zone: {zone_name}"

        # Fall back to video filename if no specific zone
        if self.video_path:
            return f"Video: {os.path.basename(self.video_path)}"
        return "Unknown location"

    def set_telegram_notifier(self, api_token: str, chat_id: str, enabled: bool = True):
        """Configure the Telegram notifier for accident notifications."""
        if enabled and api_token and chat_id:
            self.telegram_notifier = TelegramNotifier(api_token, chat_id)
        else:
            self.telegram_notifier = None

    def _perform_maintenance(self):
        """Perform periodic maintenance tasks like cleaning up stale tracks."""
        current_time = time.time()
        if current_time - self.last_track_cleanup_time > self.track_cleanup_interval:
            self._cleanup_stale_tracks()
            self.last_track_cleanup_time = current_time

    def _detect_objects(self, frame, common_params):
        """Detect and track objects in the frame."""
        # Run object detection models
        zone_results = self.run_detection(self.zone_model, frame, MODEL_TYPE_ZONE, common_params) if self.zone_model else None
        emergency_results = self.run_detection(self.emergency_model, frame, MODEL_TYPE_EMERGENCY, common_params) if self.emergency_model else None
        accident_results = self.run_detection(self.accident_model, frame, MODEL_TYPE_ACCIDENT, common_params) if self.accident_model else None

        # Process detection results
        zone_detections, emergency_detections, accident_detections = self._process_detection_results(
            zone_results, emergency_results, accident_results)

        return zone_detections, emergency_detections, accident_detections

    def _process_detection_results(self, zone_results, emergency_results, accident_results):
        """Process raw detection results into filtered, tracked detections."""
        # Convert results to detections
        zone_detections = sv.Detections.from_ultralytics(zone_results) if zone_results is not None else sv.Detections.empty()
        emergency_detections = sv.Detections.from_ultralytics(emergency_results) if emergency_results is not None else sv.Detections.empty()
        accident_detections = sv.Detections.from_ultralytics(accident_results) if accident_results is not None else sv.Detections.empty()

        # Apply filtering
        zone_detections = self.filter_zone_detections_by_class(zone_detections)
        zone_detections = self.filter_detections_by_confidence(zone_detections, 0.25)
        emergency_detections = self.filter_detections_by_confidence(emergency_detections, 0.25)
        accident_detections = self.filter_detections_by_confidence(accident_detections, 0.4)

        # Apply tracking with default parameters
        tracked_zone = self.zone_tracker.update_with_detections(zone_detections)
        tracked_emergency = self.emergency_tracker.update_with_detections(emergency_detections)
        tracked_accident = self.accident_tracker.update_with_detections(accident_detections)

        # Store detections for data collector access
        self.zone_detections = tracked_zone
        self.emergency_detections = tracked_emergency

        return tracked_zone, tracked_emergency, tracked_accident

    def _calculate_speeds(self, zone_detections, emergency_detections):
        """Calculate speeds for detected objects."""
        # Clean up tracking history
        if len(zone_detections) > 0:
            self.clean_tracking_history(
                zone_detections.tracker_id, self.track_history, self.speed_data)
        if len(emergency_detections) > 0:
            self.clean_tracking_history(
                emergency_detections.tracker_id, self.emergency_track_history, self.emergency_speed_data)

        # Calculate vehicle speeds
        vehicle_speeds = {}
        if zone_detections and len(zone_detections) > 0:
            for i, (xyxy, tracker_id, class_id) in enumerate(
                    zip(zone_detections.xyxy, zone_detections.tracker_id, zone_detections.class_id)):
                class_name = self.zone_model.names[class_id] if self.zone_model else "unknown"
                if class_name in self.vehicle_classes:
                    center = self._get_bbox_center(xyxy)
                    speed = self.calculate_speed(
                        tracker_id, center, self.track_history, self.speed_data)
                    vehicle_speeds[tracker_id] = speed

        # Calculate emergency vehicle speeds
        emergency_speeds = {}
        if emergency_detections and len(emergency_detections) > 0:
            for i, (xyxy, tracker_id) in enumerate(
                    zip(emergency_detections.xyxy, emergency_detections.tracker_id)):
                center = self._get_bbox_center(xyxy)
                speed = self.calculate_speed(
                    tracker_id, center, self.emergency_track_history, self.emergency_speed_data)
                emergency_speeds[tracker_id] = speed

        return vehicle_speeds, emergency_speeds

    def _get_bbox_center(self, xyxy):
        """Calculate the center point of a bounding box."""
        x1, y1, x2, y2 = xyxy
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    def _create_annotated_frame(self, frame, zone_detections, emergency_detections,
                              accident_detections, vehicle_speeds, emergency_speeds):
        """Create a frame with all detections, zones, and data visualized."""
        annotated_frame = frame.copy()

        # Annotate all types of detections
        annotated_frame = self.annotate_detections(
            annotated_frame, zone_detections, self.zone_model, sv.Color.ROBOFLOW, vehicle_speeds)
        annotated_frame = self.annotate_detections(
            annotated_frame, emergency_detections, self.emergency_model, sv.Color.BLUE, emergency_speeds)
        annotated_frame = self.annotate_detections(
            annotated_frame, accident_detections, self.accident_model, sv.Color.RED)

        # Annotate zones
        annotated_frame = self.annotate_zones(annotated_frame, zone_detections)

        return annotated_frame

    def _update_traffic_light_system(self, frame):
        """Update traffic light system and visualize if enabled."""
        if not self.traffic_light_controller:
            return frame

        # Update traffic light controller with latest data
        self.traffic_light_controller.update_traffic_data(
            self.zone_vehicle_counts,
            self.zone_pedestrian_counts
        )

        # Process emergency vehicle priority
        if hasattr(self, 'emergency_detections') and len(self.emergency_detections) > 0:
            # Find zones with emergency vehicles
            emergency_zones = set()
            for zone_type in self.zones:
                for zone_name, zone_info in self.zones[zone_type].items():
                    for i in range(len(self.emergency_detections)):
                        if zone_info['zone'].trigger(self.emergency_detections[i:i+1]):
                            # Report emergency in this zone
                            self.traffic_light_controller.report_emergency_vehicle(zone_name, True)
                            emergency_zones.add(zone_name)

            for zone_type in self.zones:
                for zone_name in [name for name, info in self.zones[zone_type].items() if name not in emergency_zones]:
                    self.traffic_light_controller.report_emergency_vehicle(zone_name, False)
        else:
            # No emergency vehicles detected, clear any emergency state
            for zone_type in self.zones:
                for zone_name in self.zones[zone_type]:
                    self.traffic_light_controller.report_emergency_vehicle(zone_name, False)

        # Process accident detection
        if hasattr(self, 'zone_detections') and self.accident_detected:
            # Find zones where accidents are detected
            accident_zones = set()
            for zone_type in self.zones:
                for zone_name, zone_info in self.zones[zone_type].items():
                    if hasattr(self, 'accident_detections') and len(self.accident_detections) > 0:
                        for i in range(len(self.accident_detections)):
                            if zone_info['zone'].trigger(self.accident_detections[i:i+1]):
                                # Report accident in this zone
                                self.traffic_light_controller.report_accident(True, zone_name)
                                accident_zones.add(zone_name)

            # If accident is detected but no specific zone is identified
            if not accident_zones:
                self.traffic_light_controller.report_accident(True)
        else:
            # No accident detected, clear accident state
            self.traffic_light_controller.report_accident(False)

        self.traffic_light_controller.update_all_lights()

        # Visualize traffic lights if enabled
        if self.show_traffic_lights:
            return self.traffic_light_controller.visualize_traffic_lights(frame)
        return frame

    def get_common_inference_params(self) -> Dict:
        """Returns common inference parameters from settings."""
        if not self.inference_settings:
            print("Warning: inference_settings is None. Using defaults.")
            return {
                'imgsz': DEFAULT_IMG_SIZE,
                'half': DEFAULT_HALF_PRECISION,
                'agnostic_nms': DEFAULT_AGNOSTIC_NMS,
                'max_det': DEFAULT_MAX_DETECTIONS,
                'stream_buffer': DEFAULT_STREAM_BUFFER
            }

        return {
            'imgsz': self.inference_settings.get("imgsz", DEFAULT_IMG_SIZE),
            'half': self.inference_settings.get("half", DEFAULT_HALF_PRECISION),
            'agnostic_nms': self.inference_settings.get("agnostic_nms", DEFAULT_AGNOSTIC_NMS),
            'max_det': self.inference_settings.get("max_det", DEFAULT_MAX_DETECTIONS),
            'stream_buffer': self.inference_settings.get("stream_buffer", DEFAULT_STREAM_BUFFER)
        }

    def run_detection(self, model, frame, model_type, common_params):
        """Runs object detection using the given model."""
        if model is None:
            return None

        default_model_settings = {
            "confidence_threshold": DEFAULT_CONFIDENCE_THRESHOLD,
            "iou_threshold": DEFAULT_IOU_THRESHOLD
        }

        # Get model-specific settings with fallback
        model_settings = (self.inference_settings.get(model_type, {})
                          if isinstance(self.inference_settings, dict)
                          else default_model_settings)

        conf = model_settings.get("confidence_threshold", DEFAULT_CONFIDENCE_THRESHOLD)
        iou = model_settings.get("iou_threshold", DEFAULT_IOU_THRESHOLD)

        try:
            return model(
                frame,
                conf=conf,
                iou=iou,
                verbose=False,
                **common_params
            )[0]
        except Exception as e:
            print(f"Error during detection with {model_type}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def filter_zone_detections_by_class(self, detections: sv.Detections) -> sv.Detections:
        """Filters zone detections to include only specified classes."""
        if self.zone_model and len(detections) > 0:
            target_zone_classes = ["person", "bicycle", "car", "motorcycle", "bus", "truck"]
            target_zone_class_ids = [class_id for class_id, name in self.zone_model.names.items() if name in target_zone_classes]
            filtered_zone_indices = np.isin(detections.class_id, target_zone_class_ids)
            return detections[filtered_zone_indices]
        return detections

    def annotate_detections(self, frame, detections, model, color, speeds=None):
        """Annotates detections on the frame with optional speed information."""
        if model and len(detections) > 0:
            box_annotator = sv.BoxAnnotator(color=color)
            label_annotator = sv.LabelAnnotator(color=color, text_color=sv.Color.BLACK,
                                                text_scale=0.6, border_radius=10, smart_position=True)

            frame = box_annotator.annotate(frame, detections=detections)

            # Create labels with speed information if available
            labels = []
            for i, (tracker_id, class_id) in enumerate(zip(detections.tracker_id, detections.class_id)):
                class_name = model.names[class_id]
                # Add speed information if available
                if speeds and tracker_id in speeds:
                    speed = speeds[tracker_id]
                    labels.append(f"{class_name}: {speed:.1f} km/h")
                else:
                    labels.append(f"{class_name}")

            frame = label_annotator.annotate(frame, detections=detections, labels=labels)
        return frame

    def annotate_zones(self, frame, zone_detections):
        """Annotates vehicle and pedestrian zones on the frame."""
        for zone_name, zone_info in self.zones[ZONE_TYPE_VEHICLE].items():
            frame = self.annotate_single_zone(frame, zone_info['zone'], zone_detections, sv.Color.WHITE)
        for zone_name, zone_info in self.zones[ZONE_TYPE_PEDESTRIAN].items():
            frame = self.annotate_single_zone(frame, zone_info['zone'], zone_detections, sv.Color.YELLOW)
        return frame

    def annotate_single_zone(self, frame, zone, zone_detections, color):
        """Annotates a single zone on the frame."""
        zone.trigger(zone_detections)
        zone_annotator = sv.PolygonZoneAnnotator(
            zone=zone,
            color=color,
            opacity=0.1,
            display_in_zone_count=True,
        )
        return zone_annotator.annotate(frame)

    def _get_gaussian_kernel(self, sigma):
        """Cache and retrieve gaussian kernels for better performance."""
        sigma_key = round(sigma * 2) / 2

        if sigma_key not in self.gaussian_kernels:
            size = max(1, int(3 * sigma_key + 1) | 1)
            kernel_1d = cv2.getGaussianKernel(size, sigma_key)
            self.gaussian_kernels[sigma_key] = kernel_1d @ kernel_1d.T

        return self.gaussian_kernels[sigma_key]

    def _get_dynamic_kernel(self, obj_size):
        """Returns dynamic kernel sigma and kernel based on object dimensions."""
        dynamic_sigma = max(min(
            self.heatmap_settings["kernel_sigma"] * (obj_size / 100),
            50), 5)
        kernel = self._get_gaussian_kernel(dynamic_sigma)
        kernel_half_size = kernel.shape[0] // 2
        return dynamic_sigma, kernel, kernel_half_size

    def _get_object_intensity(self, class_id, obj_size):
        """Calculates intensity factor based on object class and size."""
        class_name = self.zone_model.names[class_id]
        base_intensity = self.heatmap_settings["intensity_factor"]

        # Class-specific intensity adjustments
        intensity_multiplier = {
            'truck': 1.5, 'bus': 1.5,
            'car': 1.2, 'motorcycle': 1.2,
            'person': 0.8, 'bicycle': 0.8
        }.get(class_name, 1.0)

        # Scale with object size, clamped to reasonable range
        size_factor = np.clip(obj_size / 100, 0.5, 2.0)
        return base_intensity * intensity_multiplier * size_factor

    def _calculate_object_dimensions(self, xyxy):
        """Calculate object dimensions from bounding box."""
        x1, y1, x2, y2 = xyxy
        obj_width = x2 - x1
        obj_height = y2 - y1
        return np.sqrt(obj_width * obj_height)

    def _apply_kernel_to_heatmap(self, center_x, center_y, kernel, kernel_half_size, intensity):
        """Apply a gaussian kernel to the heatmap at specified position."""
        # Calculate slices for the kernel and target matrix
        y_slice, x_slice, kernel_y_slice, kernel_x_slice = self._calculate_kernel_slices(
            center_x, center_y, kernel_half_size)

        # Check dimensions match before applying
        kernel_part = kernel[kernel_y_slice, kernel_x_slice]
        target_shape = self.persistent_heatmap[y_slice, x_slice].shape

        if kernel_part.shape == target_shape:
            self.persistent_heatmap[y_slice, x_slice] += kernel_part * intensity

    def _calculate_kernel_slices(self, center_x, center_y, kernel_half_size):
        """Calculate slices for applying a kernel to the heatmap."""
        y_slice = slice(max(0, center_y - kernel_half_size),
                    min(self.frame_height, center_y + kernel_half_size + 1))
        x_slice = slice(max(0, center_x - kernel_half_size),
                    min(self.frame_width, center_x + kernel_half_size + 1))

        kernel_y_slice = slice(max(0, kernel_half_size - center_y),
                            kernel_half_size + (self.frame_height - center_y)
                            if center_y + kernel_half_size + 1 > self.frame_height else None)
        kernel_x_slice = slice(max(0, kernel_half_size - center_x),
                            kernel_half_size + (self.frame_width - center_x)
                            if center_x + kernel_half_size + 1 > self.frame_width else None)

        return y_slice, x_slice, kernel_y_slice, kernel_x_slice

    def _render_heatmap(self, frame):
        """Convert the heatmap data to a viewable colored overlay and blend with the frame."""
        # Convert to viewable image
        heatmap = cv2.normalize(self.persistent_heatmap, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # Apply CLAHE for better contrast distribution
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        heatmap = clahe.apply(heatmap)

        # Apply colormap and blend
        colormap_name = self.heatmap_settings["colormap"].upper()
        colormap_flag = getattr(cv2, f"COLORMAP_{colormap_name}", cv2.COLORMAP_PARULA)
        heatmap_colored = cv2.applyColorMap(heatmap, colormap_flag)

        # Blend with original frame
        opacity = self.heatmap_settings["heatmap_opacity"]
        return cv2.addWeighted(frame, 1 - opacity, heatmap_colored, opacity, 0)

    def _filter_heatmap_detections(self, detections):
        """Filter detections to include only those relevant for the heatmap."""
        if len(detections) == 0:
            return detections

        target_heatmap_classes = ["person", "bicycle", "car", "motorcycle", "bus", "truck"]
        if self.zone_model:
            target_heatmap_class_ids = [class_id for class_id, name in self.zone_model.names.items()
                                    if name in target_heatmap_classes]
            filtered_heatmap_indices = np.isin(detections.class_id, target_heatmap_class_ids)
            return detections[filtered_heatmap_indices]
        return detections

    def _update_heatmap_with_detections(self, detections):
        """Update the heatmap with detected objects."""
        if len(detections) == 0:
            return

        # Process all relevant detections
        for i in range(len(detections)):
            xyxy = detections.xyxy[i].astype(int)
            class_id = detections.class_id[i]

            # Calculate object center and dimensions
            x1, y1, x2, y2 = xyxy
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            obj_size = self._calculate_object_dimensions(xyxy)

            # Get dynamic kernel based on object size
            _, kernel, kernel_half_size = self._get_dynamic_kernel(obj_size)

            # Calculate intensity factor based on object class
            intensity = self._get_object_intensity(class_id, obj_size)

            # Apply kernel to heatmap
            self._apply_kernel_to_heatmap(center_x, center_y, kernel, kernel_half_size, intensity)

    def generate_heatmap(self, frame: np.ndarray, detections: sv.Detections) -> np.ndarray:
        """
        Generates a heatmap based on object detections with
        intensity distribution and smoother transitions.
        """
        heatmap_frame = frame.copy()

        # Apply decay even without detections
        decay_mask = self.persistent_heatmap > 0.1
        self.persistent_heatmap[decay_mask] *= self.heatmap_settings["heatmap_decay"]

        # Filter detections for heatmap
        heatmap_detections = self._filter_heatmap_detections(detections)

        # Update heatmap with filtered detections
        self._update_heatmap_with_detections(heatmap_detections)

        # Apply gaussian blur for smoother transitions
        self.persistent_heatmap = cv2.GaussianBlur(self.persistent_heatmap, (5, 5), 0)

        # Render the heatmap
        return self._render_heatmap(heatmap_frame)

    def save_zones(self, file_path: str):
        """Saves zone configuration to a JSON file, including both vehicle and pedestrian zones."""
        zone_data = {'vehicle_zones': {}, 'pedestrian_zones': {}}
        for zone_name, zone_info in self.zones[ZONE_TYPE_VEHICLE].items():
            zone_data['vehicle_zones'][zone_name] = {
                'polygon': zone_info['zone'].polygon.tolist()
            }
        for zone_name, zone_info in self.zones[ZONE_TYPE_PEDESTRIAN].items():
            zone_data['pedestrian_zones'][zone_name] = {
                'polygon': zone_info['zone'].polygon.tolist()
            }
        try:
            with open(file_path, 'w') as f:
                json.dump(zone_data, f, indent=4)
        except Exception as e:
            raise Exception(f"Error saving zones to {file_path}: {e}")

    def load_zones(self, file_path: str) -> bool:
        """Loads zone configuration from a JSON file, loading both vehicle and pedestrian zones."""
        try:
            with open(file_path, 'r') as f:
                zone_data = json.load(f)
            self.zones = {ZONE_TYPE_VEHICLE: {}, ZONE_TYPE_PEDESTRIAN: {}}
            if 'vehicle_zones' in zone_data:
                for zone_name, data in zone_data['vehicle_zones'].items():
                    self.zones[ZONE_TYPE_VEHICLE][zone_name] = {
                        'zone': sv.PolygonZone(polygon=np.array(data['polygon']))
                    }
            if 'pedestrian_zones' in zone_data:
                for zone_name, data in zone_data['pedestrian_zones'].items():
                    self.zones[ZONE_TYPE_PEDESTRIAN][zone_name] = {
                        'zone': sv.PolygonZone(polygon=np.array(data['polygon']))
                    }
            return True
        except FileNotFoundError:
            print(f"Error: Zone configuration file not found: {file_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"Error decoding zone configuration file: {file_path}. Error: {e}")
            return False
        except Exception as e:
            print(f"Error loading zones from {file_path}: {e}")
            return False

    def update_counts(self, detections: sv.Detections):
        """Updates vehicle and pedestrian counts for each zone based on detections."""
        # Reset all counters
        self.vehicle_counts = {k: 0 for k in self.vehicle_counts}
        self.pedestrian_count = 0

        self.zone_vehicle_counts = {
            zone_name: {k: 0 for k in self.vehicle_counts}
            for zone_name in self.zones[ZONE_TYPE_VEHICLE]
        }
        self.zone_pedestrian_counts = {
            zone_name: 0 for zone_name in self.zones[ZONE_TYPE_PEDESTRIAN]
        }

        if len(detections) == 0:
            return

        # Count detections in each zone
        for i, (_, class_id) in enumerate(zip(detections.xyxy, detections.class_id)):
            class_name = self.zone_model.names[class_id]

            # Check vehicle zones
            for zone_name, zone_info in self.zones[ZONE_TYPE_VEHICLE].items():
                if zone_info['zone'].trigger(detections[i:i+1]):
                    if class_name in self.vehicle_counts:
                        self.zone_vehicle_counts[zone_name][class_name] += 1
                        self.vehicle_counts[class_name] += 1

            # Check pedestrian zones
            if class_name == "person":
                for zone_name, zone_info in self.zones[ZONE_TYPE_PEDESTRIAN].items():
                    if zone_info['zone'].trigger(detections[i:i+1]):
                        self.zone_pedestrian_counts[zone_name] += 1
                        self.pedestrian_count += 1

    def get_zone_vehicle_counts(self):
        """Returns vehicle counts for each vehicle zone."""
        return self.zone_vehicle_counts

    def get_zone_pedestrian_counts(self):
        """Returns pedestrian counts for each pedestrian zone."""
        return self.zone_pedestrian_counts

    def get_vehicle_counts(self):
        """Returns total vehicle counts across all zones."""
        return self.vehicle_counts

    def get_pedestrian_count(self):
        """Returns total pedestrian count across all zones."""
        return self.pedestrian_count

    def is_emergency_detected(self):
        """Returns whether any emergency vehicle is detected."""
        return self.emergency_detected

    def get_emergency_vehicles(self):
        """Returns detected emergency vehicle types (ambulance, firetruck)."""
        if not hasattr(self, 'emergency_detections') or not self.emergency_model:
            return {}

        emergency_counts = {'ambulance': 0, 'firetruck': 0}

        # Count emergency vehicles by type
        if hasattr(self, 'emergency_detections') and len(self.emergency_detections) > 0:
            for i, class_id in enumerate(self.emergency_detections.class_id):
                class_name = self.emergency_model.names[class_id]
                if class_name in emergency_counts:
                    emergency_counts[class_name] += 1

        return emergency_counts

    def is_accident_detected(self):
        """Returns whether an accident is detected."""
        return self.accident_detected

    def calculate_speed(self, track_id, center_point, history_dict, speed_data_dict):
        """Calculates speed of an object based on its movement history."""
        if track_id not in history_dict:
            history_dict[track_id] = []

        history_dict[track_id].append((center_point, time.time()))

        max_history = 30
        if len(history_dict[track_id]) > max_history:
            history_dict[track_id] = history_dict[track_id][-max_history:]

        if len(history_dict[track_id]) < 2:
            return 0.0

        # Calculate speed based on pixel distance and time difference
        prev_pos, prev_time = history_dict[track_id][-2]
        curr_pos, curr_time = history_dict[track_id][-1]
        time_diff = curr_time - prev_time
        if time_diff <= 0:
            return 0.0

        pixel_distance = np.sqrt((curr_pos[0] - prev_pos[0])**2 + (curr_pos[1] - prev_pos[1])**2)

        # Convert pixels to meters using pixels per meter ratio
        meters = pixel_distance / self.ppm

        # Calculate speed in m/s then convert to km/h
        speed_mps = meters / time_diff
        speed_kmh = speed_mps * 3.6

        # Apply smoothing using moving average
        speed_data_dict[track_id].append(speed_kmh)
        if len(speed_data_dict[track_id]) > self.speed_smoothing_window:
            speed_data_dict[track_id] = speed_data_dict[track_id][-self.speed_smoothing_window:]

        smoothed_speed = sum(speed_data_dict[track_id]) / len(speed_data_dict[track_id])
        return max(0, min(200, smoothed_speed))

    def clean_tracking_history(self, active_track_ids, history_dict, speed_data_dict):
        """Removes history for tracks that are no longer active."""
        tracked_ids = list(history_dict.keys())
        current_tracks = set(active_track_ids)

        for track_id in tracked_ids:
            if track_id not in current_tracks:
                if track_id in history_dict:
                    del history_dict[track_id]
                if track_id in speed_data_dict:
                    del speed_data_dict[track_id]

    def filter_detections_by_confidence(self, detections, threshold):
        """Filter detections based on confidence threshold."""
        if len(detections) == 0:
            return detections

        mask = detections.confidence >= threshold
        return detections[mask]

    def _cleanup_stale_tracks(self):
        """Performs periodic cleanup of tracking data structures to prevent memory leaks."""
        # Get current time for age-based cleanup
        current_time = time.time()
        max_age = 60

        # Clean track history dictionaries
        for history_dict in [self.track_history, self.emergency_track_history]:
            track_ids = list(history_dict.keys())
            for track_id in track_ids:
                if not history_dict[track_id]:
                    del history_dict[track_id]
                    continue

                # Check age of the most recent position
                _, last_update_time = history_dict[track_id][-1]
                if current_time - last_update_time > max_age:
                    del history_dict[track_id]

        # Clean speed data dictionaries
        for speed_dict in [self.speed_data, self.emergency_speed_data]:
            track_ids = list(speed_dict.keys())
            for track_id in track_ids:
                if (track_id not in self.track_history and
                    track_id not in self.emergency_track_history):
                    del speed_dict[track_id]

    def reset_trackers(self):
        """Resets all trackers to clear their internal state."""
        self.zone_tracker.reset()
        self.emergency_tracker.reset()
        self.accident_tracker.reset()
        self.track_history.clear()
        self.emergency_track_history.clear()
        self.speed_data.clear()
        self.emergency_speed_data.clear()

    def set_traffic_light_controller(self, controller):
        """Sets the traffic light controller for this zone manager."""
        self.traffic_light_controller = controller

    def toggle_traffic_light_display(self):
        """Toggles whether traffic lights should be shown on the video."""
        self.show_traffic_lights = not self.show_traffic_lights

    def is_showing_traffic_lights(self):
        """Returns whether traffic lights are currently shown."""
        return self.show_traffic_lights

    def set_data_collector(self, data_collector):
        """Sets the data collector for this zone manager."""
        self.data_collector = data_collector
        self.data_collector.set_zone_manager(self)

    def is_data_collection_active(self):
        """Returns whether data collection is active."""
        if hasattr(self, 'data_collector'):
            return self.data_collector and self.data_collector.is_collecting
        return False

    def start_data_collection(self, video_path=None, notes=None):
        """Starts data collection if a collector is available."""
        if hasattr(self, 'data_collector') and self.data_collector:
            return self.data_collector.start_collection(video_path, notes)
        return False

    def stop_data_collection(self):
        """Stops data collection if active."""
        if hasattr(self, 'data_collector') and self.data_collector:
            return self.data_collector.stop_collection()
        return False

    def get_latest_zone_detections(self):
        """Returns a reference to the latest zone detections."""
        return getattr(self, 'zone_detections', None)
