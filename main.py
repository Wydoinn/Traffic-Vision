import sys
import os
import time
import json
import torch
import cv2
from typing import Dict
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                            QHBoxLayout, QLabel, QWidget, QMessageBox,
                            QTabWidget, QFileDialog, QSizePolicy)
from PyQt6.QtGui import QImage, QPixmap, QIcon
from PyQt6.QtCore import Qt

from inference import InferenceThread
from manager import ZoneManager
from utils.constants import *
from static.styles.styles import get_stylesheet, is_system_dark_theme
from ui.controls import ControlPanel
from ui.settings import SettingsTab
from ui.monitoring import MonitoringTab
from ui.traffic_light import TrafficLightConfigTab
from db.data_collector import TrafficDataCollector

class ZoneManagerGUI(QMainWindow):
    """
    Main application window for the Traffic Management System.
    Handles GUI interactions, settings, and video processing.
    Includes separate vehicle and pedestrian zones.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Traffic Management System")

        # Initialize the data collector
        self.data_collector = TrafficDataCollector()

        # Initialize monitoring tab first
        self.monitoring_tab = MonitoringTab()

        # Get the screen size
        screen = self.screen().geometry()
        window_width = int(screen.width() * 0.90)
        window_height = int(screen.height() * 0.90)

        self.resize(window_width, window_height)
        self.center()

        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        self.settings = self.load_settings()
        self.apply_settings_to_models()
        self.setup_ui()

        self.video_path = None
        self.zone_manager = None
        self.is_inferencing = False
        self.last_update_time = time.time()
        self.update_interval = 1.0 / 30.0

        self.inference_thread = None

    def setup_ui(self):
        """Sets up the user interface of the application."""
        self.setStyleSheet(get_stylesheet(is_system_dark_theme()))
        central_widget = QWidget()
        main_layout = QHBoxLayout()

        tabs = QTabWidget()
        self.control_panel = ControlPanel(self)
        tabs.addTab(self.control_panel, "Controls")
        self.settings_tab = SettingsTab(self)
        tabs.addTab(self.settings_tab, "Settings")

        # Add Traffic Light Config tab
        self.traffic_light_tab = TrafficLightConfigTab(self)
        tabs.addTab(self.traffic_light_tab, "Traffic Lights")

        # Add Monitoring tab
        if self.monitoring_tab:
            tabs.addTab(self.monitoring_tab, "Monitoring")

        displays_layout = self.create_displays_layout()

        main_layout.addWidget(tabs, 0)
        main_layout.addLayout(displays_layout, 1)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def create_displays_layout(self):
        """Creates the layout for video and heatmap displays."""
        displays_layout = QVBoxLayout()
        # Set margins to minimize wasted space
        displays_layout.setContentsMargins(0, 0, 0, 0)
        displays_layout.setSpacing(4)

        # Replace scroll areas with simple containers
        video_container = QWidget()
        video_container.setObjectName("videoDisplay")
        video_layout = QVBoxLayout(video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_label.setMinimumSize(320, 240)
        video_layout.addWidget(self.video_label)

        heatmap_container = QWidget()
        heatmap_container.setObjectName("heatmapDisplay")
        heatmap_layout = QVBoxLayout(heatmap_container)
        heatmap_layout.setContentsMargins(0, 0, 0, 0)
        self.heatmap_label = QLabel()
        self.heatmap_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heatmap_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.heatmap_label.setMinimumSize(320, 240)
        heatmap_layout.addWidget(self.heatmap_label)

        # Set layout stretch factors to maintain equal height ratio (1:1)
        displays_layout.addWidget(video_container, 1)
        displays_layout.addWidget(heatmap_container, 1)

        return displays_layout

    def center(self):
        """Centers the application window on the screen."""
        screen = self.screen().geometry()
        window = self.geometry()
        self.move(
            screen.center().x() - window.width() // 2,
            screen.center().y() - window.height() // 2
        )

    def load_settings(self) -> Dict:
        """Loads settings from settings.json or uses default settings."""
        default_settings = self.get_default_settings()
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    full_settings = default_settings.copy()
                    full_settings.update(settings)
                    return self.ensure_settings_compatibility(full_settings, default_settings)
            else:
                return default_settings
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Settings Error", f"Error decoding {SETTINGS_FILE}. Using default settings. Error: {e}")
            return default_settings
        except Exception as e:
            QMessageBox.critical(self, "Settings Error", f"Failed to load settings. Using default settings. Error: {e}")
            return default_settings

    def get_default_settings(self) -> Dict:
        """Returns the default settings dictionary."""
        return {
            "model_paths": {
                MODEL_TYPE_ZONE: "",
                MODEL_TYPE_EMERGENCY: "",
                MODEL_TYPE_ACCIDENT: ""
            },
            "inference_settings": {
                MODEL_TYPE_ZONE: {
                    "confidence_threshold": 0.35,
                    "iou_threshold": 0.45,
                },
                MODEL_TYPE_EMERGENCY: {
                    "confidence_threshold": 0.6,
                    "iou_threshold": 0.40,
                },
                MODEL_TYPE_ACCIDENT: {
                    "confidence_threshold": 0.6,
                    "iou_threshold": 0.40,
                },
                "imgsz": DEFAULT_IMG_SIZE,
                "half": DEFAULT_HALF_PRECISION,
                "agnostic_nms": DEFAULT_AGNOSTIC_NMS,
                "max_det": DEFAULT_MAX_DETECTIONS,
                "vid_stride": DEFAULT_VIDEO_STRIDE,
                "stream_buffer": DEFAULT_STREAM_BUFFER
            },
            "heatmap_settings": {
                "kernel_sigma": DEFAULT_KERNEL_SIGMA,
                "intensity_factor": DEFAULT_INTENSITY_FACTOR,
                "heatmap_opacity": DEFAULT_HEATMAP_OPACITY,
                "colormap": DEFAULT_COLORMAP,
                "heatmap_decay": DEFAULT_HEATMAP_DECAY
            },
            "display_settings": {
                "aspect_ratio_mode": DEFAULT_ASPECT_RATIO_MODE
            },
            "telegram_settings": {
                TELEGRAM_ENABLED_KEY: TELEGRAM_ENABLED_DEFAULT,
                TELEGRAM_API_TOKEN_KEY: TELEGRAM_API_TOKEN_DEFAULT,
                TELEGRAM_CHAT_ID_KEY: TELEGRAM_CHAT_ID_DEFAULT
            }
        }

    def ensure_settings_compatibility(self, loaded_settings: Dict, default_settings: Dict) -> Dict:
        """Ensures backward compatibility of settings by adding missing keys from default settings."""
        full_settings = default_settings.copy()

        # Recursive function to deeply update nested dictionaries
        def deep_update(target, source):
            for key, value in source.items():
                if key in target and isinstance(value, dict) and isinstance(target[key], dict):
                    deep_update(target[key], value)
                else:
                    target[key] = value

        # Deep update with loaded settings
        deep_update(full_settings, loaded_settings)

        # Ensure vid_stride is valid
        vid_stride = full_settings["inference_settings"].get("vid_stride", DEFAULT_VIDEO_STRIDE)
        if not isinstance(vid_stride, int) or vid_stride < 1:
            full_settings["inference_settings"]["vid_stride"] = DEFAULT_VIDEO_STRIDE
            print(f"Warning: Invalid video stride value in settings, using default: {DEFAULT_VIDEO_STRIDE}")

        return full_settings

    def save_settings(self):
        """Saves current settings to settings.json."""
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Settings Error", f"Failed to save settings. Error: {e}")

    def save_settings_gui(self):
        """Saves settings from GUI elements to settings.json and reloads models."""
        self.settings_tab.save_settings_gui()

    def apply_settings_to_models(self):
        """Loads models based on paths from settings.json, supporting multiple formats."""
        model_paths = self.settings["model_paths"]

        # Determine the optimal device for inference
        if torch.cuda.is_available():
            inference_device = "cuda"
            print(f"CUDA available: {torch.cuda.get_device_name(0)}")
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            inference_device = "mps"
            print("Apple Silicon MPS acceleration available")
        else:
            inference_device = "cpu"
            print("Using CPU for inference")

        print(f"Using device for inference: {inference_device}")

        # Reset models first
        self.zone_model = None
        self.emergency_model = None
        self.accident_model = None

        # Load all models with status reporting
        self.zone_model = self.load_model_with_status(model_paths[MODEL_TYPE_ZONE], "zone", inference_device)
        self.emergency_model = self.load_model_with_status(model_paths[MODEL_TYPE_EMERGENCY], "emergency", inference_device)
        self.accident_model = self.load_model_with_status(model_paths[MODEL_TYPE_ACCIDENT], "accident", inference_device)

        # Update ZoneManager with new models if it exists
        if hasattr(self, 'zone_manager') and self.zone_manager:
            self.zone_manager.zone_model = self.zone_model
            self.zone_manager.emergency_model = self.emergency_model
            self.zone_manager.accident_model = self.accident_model
            self.zone_manager.inference_settings = self.settings["inference_settings"]
            self.zone_manager.heatmap_settings = self.settings["heatmap_settings"]

        models_loaded = any([self.zone_model, self.emergency_model, self.accident_model])
        status_msg = "Models loaded successfully" if models_loaded else "No models loaded - please check settings"
        self.status_bar.showMessage(status_msg, 3000)

    def load_model_with_status(self, model_path, model_type, inference_device):
        """Loads a model with status reporting."""
        if model_path and os.path.exists(model_path):
            self.status_bar.showMessage(f"Loading {model_type} model...", 0)
            model = self.load_model(model_path, inference_device)
            if not model:
                self.status_bar.showMessage(f"Failed to load {model_type} model", 3000)
            return model
        elif model_path:
            self.status_bar.showMessage(f"{model_type.capitalize()} model path not found: {model_path}", 3000)
        else:
            print(f"{model_type.capitalize()} model path not set")
        return None

    def load_model(self, model_path, device):
        """
        Loads a model based on its file extension.
        """
        if not model_path:
            return None

        try:
            from ultralytics import YOLO
            model = YOLO(model_path, task="detect")

            # Apply device settings based on format
            if os.path.splitext(model_path)[1].lower() in ['.pt', '.pth']:
                model.to(device)

            return model
        except Exception as e:
            QMessageBox.critical(self, "Model Load Error", f"Failed to load model {model_path}: {str(e)}")
            print(f"Error loading model {model_path}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def browse_model_path(self, line_edit, setting_key):
        """Opens a file dialog to browse for model files with extended format support."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Model File", "",
            "Model Files (*.pt *.pth *.onnx *.engine *.mlpackage);;PyTorch Models (*.pt *.pth);;ONNX Models (*.onnx);;TensorRT Engines (*.engine);;CoreML Models (*.mlpackage);;All Files (*)"
        )
        if file_path:
            line_edit.setText(file_path)

    def select_video(self):
        """Opens a file dialog to select a video file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Video File",
                                                   "", "Video Files (*.mp4 *.avi *.mov)")
        if file_path:
            self.video_path = file_path
            filename = os.path.basename(file_path)
            self.control_panel.video_path_label.setText(f"Selected: {filename}")
            self.control_panel.start_inference_btn.setEnabled(False)
            self.control_panel.save_zones_btn.setEnabled(False)

            # Stop any running inference thread
            if self.inference_thread and self.is_inferencing:
                self.stop_inference()

            self.video_label.clear()
            self.heatmap_label.clear()
            self.status_bar.showMessage(f"Video selected: {filename}", 3000)

            # Create Zone Manager with current settings
            self.zone_manager = ZoneManager(
                frame_width=-1,
                frame_height=-1,
                video_path=self.video_path,
                zone_model=self.zone_model,
                emergency_model=self.emergency_model,
                accident_model=self.accident_model,
                inference_settings=self.settings["inference_settings"],
                heatmap_settings=self.settings["heatmap_settings"]
            )

            # Set up inference thread
            self.inference_thread = InferenceThread(self.zone_manager, self.video_path, self.settings["inference_settings"])
            self.inference_thread.frame_processed_signal.connect(self.update_displays_from_thread)
            self.inference_thread.status_message_signal.connect(self.status_bar.showMessage)

        else:
            self.status_bar.showMessage("Video selection cancelled", 3000)

    def start_create_vehicle_zones(self):
        """Starts vehicle zone creation, disabling UI elements."""
        self._start_zone_creation(ZONE_TYPE_VEHICLE)

    def start_create_pedestrian_zones(self):
        """Starts pedestrian zone creation, disabling UI elements."""
        self._start_zone_creation(ZONE_TYPE_PEDESTRIAN)

    def _start_zone_creation(self, zone_type: str):
        """Starts zone creation process for a given zone type."""
        if not self.video_path:
            QMessageBox.warning(self, "Error", "Please select a video first!")
            self.status_bar.showMessage("Error: No video selected for zone creation", 3000)
            return

        num_zones = self.control_panel.vehicle_zone_spinbox.value() if zone_type == ZONE_TYPE_VEHICLE else self.control_panel.pedestrian_zone_spinbox.value()
        if num_zones == 0:
            QMessageBox.warning(self, "Error", f"You must create at least one {zone_type} zone!")
            self.status_bar.showMessage(f"Error: No {zone_type} zones specified for creation", 3000)
            return

        self.disable_zone_creation_buttons()
        self.status_bar.showMessage(f"Initializing {zone_type} zone creation...", 0)

        try:
            if self.zone_manager is None:
                self.zone_manager = ZoneManager(
                    frame_width=-1,
                    frame_height=-1,
                    video_path=self.video_path,
                    zone_model=self.zone_model,
                    emergency_model=self.emergency_model,
                    accident_model=self.accident_model,
                    inference_settings=self.settings["inference_settings"],
                    heatmap_settings=self.settings["heatmap_settings"]
                )
            self.zone_manager.create_zones_interactive(
                num_zones,
                zone_type=zone_type,
                callback=self.zone_creation_callback
            )
        except Exception as e:
            self.enable_zone_creation_buttons()
            error_message = f"Zone Manager Initialization Error: {str(e)}"
            QMessageBox.warning(self, "Error", error_message)
            self.status_bar.showMessage("Zone manager initialization failed!", 3000)
            print(error_message)

    def disable_zone_creation_buttons(self):
        """Disables zone creation buttons."""
        self.control_panel.create_vehicle_zones_btn.setEnabled(False)
        self.control_panel.create_pedestrian_zones_btn.setEnabled(False)

    def enable_zone_creation_buttons(self):
        """Enables zone creation buttons."""
        self.control_panel.create_vehicle_zones_btn.setEnabled(True)
        self.control_panel.create_pedestrian_zones_btn.setEnabled(True)

    def zone_creation_callback(self, success: bool, zone_type: str):
        """Callback function after zone creation is completed."""
        self.enable_zone_creation_buttons()

        if success:
            self.control_panel.start_inference_btn.setEnabled(True)
            self.control_panel.save_zones_btn.setEnabled(True)
            QMessageBox.information(self, "Success", f"{zone_type.capitalize()} Zones created successfully!")
            self.status_bar.showMessage(f"{zone_type.capitalize()} Zones created successfully!", 3000)
        else:
            QMessageBox.warning(self, "Error", f"Failed to create {zone_type} zones.")
            self.status_bar.showMessage(f"{zone_type.capitalize()} zone creation failed!", 3000)

    def save_zones(self):
        """Saves zone configuration to a JSON file."""
        if not self.zone_manager or (not self.zone_manager.zones[ZONE_TYPE_VEHICLE] and not self.zone_manager.zones[ZONE_TYPE_PEDESTRIAN]):
            QMessageBox.warning(self, "Warning", "No zones to save. Create zones first.")
            self.status_bar.showMessage("Warning: No zones to save", 3000)
            return
        self.control_panel.save_zones_btn.setEnabled(False)
        self.control_panel.save_zones_btn.setEnabled(True)

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Zone Configuration", "", "JSON Files (*.json)"
        )
        if file_path:
            if not file_path.endswith(".json"):
                file_path += ".json"
            try:
                self.status_bar.showMessage("Saving zones...", 0)
                self.zone_manager.save_zones(file_path)
                QMessageBox.information(self, "Success", f"Zones saved to {file_path}")
                self.status_bar.showMessage(f"Zones saved to {file_path}", 3000)
            except Exception as e:
                error_message = f"Failed to save zones: {str(e)}"
                QMessageBox.critical(self, "Error", error_message)
                self.status_bar.showMessage("Failed to save zones!", 3000)
                print(error_message)
        else:
            self.status_bar.showMessage("Save zones cancelled", 3000)

    def load_zones(self):
        """Loads zone configuration from a JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Zone Configuration", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                self.status_bar.showMessage("Loading zones...", 0)
                self.zone_manager = ZoneManager(
                    frame_width=-1,
                    frame_height=-1,
                    video_path=self.video_path,
                    zone_model=self.zone_model,
                    emergency_model=self.emergency_model,
                    accident_model=self.accident_model,
                    inference_settings=self.settings["inference_settings"],
                    heatmap_settings=self.settings["heatmap_settings"]
                )
                success = self.zone_manager.load_zones(file_path)
                if success:
                    self.control_panel.start_inference_btn.setEnabled(True)
                    self.control_panel.save_zones_btn.setEnabled(True)
                    QMessageBox.information(self, "Success", f"Zones loaded from {file_path}")
                    self.status_bar.showMessage(f"Zones loaded from {file_path}", 3000)
                else:
                    QMessageBox.warning(self, "Error", "Failed to load zones.")
                    self.status_bar.showMessage("Failed to load zones!", 3000)
            except Exception as e:
                error_message = f"Failed to load zones: {str(e)}"
                QMessageBox.critical(self, "Error", error_message)
                self.status_bar.showMessage("Error loading zones!", 3000)
                print(error_message)
        else:
            self.status_bar.showMessage("Load zones cancelled", 3000)

    def toggle_inference(self):
        """Starts or stops real-time inference."""
        if not self.is_inferencing:
            self.start_inference()
        else:
            self.stop_inference()

    def start_inference(self):
        """Starts real-time inference process."""
        if not self.video_path:
            QMessageBox.warning(self, "Error", "Please select a video first!")
            self.status_bar.showMessage("Error: No video selected for inference", 3000)
            return
        if not self.zone_manager or (not self.zone_manager.zones[ZONE_TYPE_VEHICLE] and not self.zone_manager.zones[ZONE_TYPE_PEDESTRIAN]):
            QMessageBox.warning(self, "Error", "Please create or load zones first!")
            self.status_bar.showMessage("Error: No zones defined for inference", 3000)
            return

        # Always make sure we have an updated inference thread
        if not self.inference_thread:
            self.inference_thread = InferenceThread(self.zone_manager, self.video_path, self.settings["inference_settings"])
            self.inference_thread.frame_processed_signal.connect(self.update_displays_from_thread)
            self.inference_thread.status_message_signal.connect(self.status_bar.showMessage)
        else:
            # Update inference thread with latest settings
            self.inference_thread.zone_manager = self.zone_manager
            self.inference_thread.video_path = self.video_path
            self.inference_thread.inference_settings = self.settings["inference_settings"]

        self.is_inferencing = True
        self.control_panel.start_inference_btn.setText("Stop Inference")
        self.status_bar.showMessage("Inference started", 0)

        # Ensure zone manager has latest settings before starting inference
        self.zone_manager.inference_settings = self.settings["inference_settings"]
        self.zone_manager.heatmap_settings = self.settings["heatmap_settings"]

        # Set traffic light controller in zone manager
        if hasattr(self, 'traffic_light_tab'):
            traffic_controller = self.traffic_light_tab.get_controller()
            self.zone_manager.set_traffic_light_controller(traffic_controller)

            # Enable or disable traffic light controls based on configuration
            has_traffic_lights = traffic_controller and bool(traffic_controller.traffic_lights)
            self.control_panel.enable_traffic_light_controls(has_traffic_lights)

            # Default to showing traffic lights if they are configured
            if has_traffic_lights:
                self.zone_manager.toggle_traffic_light_display()
                # Update the button text to reflect the traffic light state
                self.control_panel.update_traffic_light_button_text()

        # Connect zone manager with data collector
        self.zone_manager.set_data_collector(self.data_collector)

        # Automatically start data collection when inference begins
        if self.data_collector and not self.zone_manager.is_data_collection_active():
            self.zone_manager.start_data_collection(self.video_path, "Auto-started with inference")
            self.status_bar.showMessage("Data collection started automatically", 3000)

        # Configure Telegram notifications if enabled
        telegram_settings = self.settings.get("telegram_settings", {})
        if telegram_settings.get(TELEGRAM_ENABLED_KEY, False):
            api_token = telegram_settings.get(TELEGRAM_API_TOKEN_KEY, "")
            chat_id = telegram_settings.get(TELEGRAM_CHAT_ID_KEY, "")
            self.zone_manager.set_telegram_notifier(api_token, chat_id, enabled=True)
            self.status_bar.showMessage("Telegram notifications enabled", 3000)
        else:
            # Disable notifications if not enabled
            self.zone_manager.set_telegram_notifier("", "", enabled=False)

        self.inference_thread.start_inference()

    def stop_inference(self):
        """Stops real-time inference process."""
        self.is_inferencing = False
        self.control_panel.start_inference_btn.setText("Start Inference")
        self.video_label.clear()
        self.heatmap_label.clear()
        if self.zone_manager:
            self.zone_manager.reset_heatmap()
            self.zone_manager.reset_trackers()
        self.status_bar.showMessage("Inference stopping...", 0)
        if self.inference_thread:
            self.inference_thread.stop_inference()
            self.inference_thread.wait()

        # Stop data collection if active
        if self.zone_manager and self.zone_manager.is_data_collection_active():
            self.zone_manager.stop_data_collection()
            self.status_bar.showMessage("Data collection stopped", 3000)

        self.status_bar.showMessage("Inference stopped", 3000)

    def update_displays_from_thread(self, annotated_frame, heatmap_frame, detection_data):
        """Updates video and heatmap display labels with processed frames, throttled."""
        current_time = time.time()
        if current_time - self.last_update_time >= self.update_interval:
            self.update_display_labels(annotated_frame, heatmap_frame)

            # Update zone-specific counts and alerts in monitoring tab
            if self.monitoring_tab:
                # Update zone-specific counts
                self.monitoring_tab.update_zone_vehicle_counts(
                    detection_data.get("zone_vehicle_counts", {})
                )
                self.monitoring_tab.update_zone_pedestrian_counts(
                    detection_data.get("zone_pedestrian_counts", {})
                )

                # Update alert indicators
                self.monitoring_tab.set_emergency_detected(
                    detection_data.get("emergency_detected", False)
                )
                self.monitoring_tab.set_accident_detected(
                    detection_data.get("accident_detected", False)
                )

                # Update traffic light status if available
                if "intersections" in detection_data:
                    self.monitoring_tab.update_traffic_light_status(
                        detection_data.get("intersections", {})
                    )
                    # Enable traffic light toggle button if traffic lights are configured
                    has_traffic_lights = bool(detection_data.get("intersections", {}))
                    if has_traffic_lights:
                        self.control_panel.enable_traffic_light_controls(True)

            self.last_update_time = current_time

    def update_display_labels(self, annotated_frame, heatmap_frame):
        """Updates video and heatmap display labels with processed frames."""
        video_pixmap = self.convert_cv_frame_to_pixmap(annotated_frame)
        heatmap_pixmap = self.convert_cv_frame_to_pixmap(heatmap_frame)
        # Scale pixmaps to fit the available space while respecting aspect ratio
        aspect_ratio_mode = self.get_aspect_ratio_mode()
        video_container_size = self.video_label.size()
        heatmap_container_size = self.heatmap_label.size()

        scaled_video_pixmap = video_pixmap.scaled(
            video_container_size.width(),
            video_container_size.height(),
            aspect_ratio_mode,
            Qt.TransformationMode.SmoothTransformation
        )

        scaled_heatmap_pixmap = heatmap_pixmap.scaled(
            heatmap_container_size.width(),
            heatmap_container_size.height(),
            aspect_ratio_mode,
            Qt.TransformationMode.SmoothTransformation
        )

        self.video_label.setPixmap(scaled_video_pixmap)
        self.heatmap_label.setPixmap(scaled_heatmap_pixmap)

    def convert_cv_frame_to_pixmap(self, frame):
        """Converts a OpenCV frame to a QPixmap for display."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(qt_image)

    def get_aspect_ratio_mode(self):
        """Returns the Qt aspect ratio mode based on settings."""
        aspect_ratio_mode_str = self.settings["display_settings"]["aspect_ratio_mode"]
        if aspect_ratio_mode_str == "KeepAspectRatio":
            return Qt.AspectRatioMode.KeepAspectRatio
        elif aspect_ratio_mode_str == "IgnoreAspectRatio":
            return Qt.AspectRatioMode.IgnoreAspectRatio
        return Qt.AspectRatioMode.KeepAspectRatio

    def restart_application(self):
        """Restarts the application to apply settings changes."""
        self.status_bar.showMessage("Restarting application...", 1000)

        # Clean up resources
        if self.is_inferencing:
            self.stop_inference()

        # Get the command that was used to start the program
        import sys
        import os
        import subprocess

        # Use Python executable to restart the application
        python = sys.executable
        script = os.path.abspath(sys.argv[0])
        args = sys.argv[1:]

        # Close the current instance
        self.close()

        # Start a new instance
        subprocess.Popen([python, script] + args)

        # Exit the current instance
        sys.exit(0)

    def show_data_viewer(self):
        """This functionality has been removed."""
        QMessageBox.information(self, "Information",
            "The data viewer has been removed. The data is still being collected in the SQLite database.")

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("static/icon/traffic-light.png"))
    zone_manager_gui = ZoneManagerGUI()
    zone_manager_gui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
