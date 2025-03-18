import time
import cv2
from PyQt6.QtCore import QThread, pyqtSignal

class InferenceThread(QThread):
    """
    Thread for running inference to avoid blocking the GUI.
    """
    frame_processed_signal = pyqtSignal(object, object, object)
    status_message_signal = pyqtSignal(str)

    def __init__(self, zone_manager, video_path, inference_settings):
        super().__init__()
        self.zone_manager = zone_manager
        self.video_path = video_path
        self.inference_settings = inference_settings
        self.cap = None
        self.is_running = False
        self.fps_values = []
        self.last_frame_time = None

    def start_inference(self):
        self.is_running = True
        self.start()

    def stop_inference(self):
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.wait()

    def run(self):
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            self.status_message_signal.emit("Error: Could not open video file!")
            return

        # Initialize state
        self.zone_manager.reset_heatmap()
        self.last_frame_time = None
        self.fps_values = []

        # Ensure settings are updated
        if hasattr(self.zone_manager, 'inference_settings'):
            self.zone_manager.inference_settings = self.inference_settings

        # Get video stride with safe default
        vid_stride = max(1, self.inference_settings.get("vid_stride", 1))

        frame_count = 0
        fps_update_interval = 10

        try:
            while self.is_running:
                ret, frame = self.cap.read()
                if not ret:
                    self.status_message_signal.emit("End of video stream")
                    break

                frame_count += 1

                # Process only every vid_stride frames
                if (frame_count - 1) % vid_stride != 0:
                    continue

                start_time = time.time()

                # Process frame and collect detection data
                annotated_frame, heatmap_frame = self.zone_manager.process_frame(frame)

                detection_data = {
                    "vehicle_counts": self.zone_manager.get_vehicle_counts(),
                    "pedestrian_count": self.zone_manager.get_pedestrian_count(),
                    "zone_vehicle_counts": self.zone_manager.get_zone_vehicle_counts(),
                    "zone_pedestrian_counts": self.zone_manager.get_zone_pedestrian_counts(),
                    "emergency_detected": self.zone_manager.is_emergency_detected(),
                    "accident_detected": self.zone_manager.is_accident_detected()
                }

                # Add traffic light information if available
                if (hasattr(self.zone_manager, 'traffic_light_controller') and
                    self.zone_manager.traffic_light_controller):
                    detection_data["traffic_light_states"] = self.zone_manager.traffic_light_controller.get_light_states()
                    detection_data["intersections"] = self.zone_manager.traffic_light_controller.get_intersections_info()

                self.frame_processed_signal.emit(annotated_frame, heatmap_frame, detection_data)

                # Calculate and update FPS stats
                frame_duration = time.time() - start_time

                if frame_duration > 0:
                    fps = 1 / frame_duration
                    self.fps_values.append(fps)
                    if len(self.fps_values) > 10:
                        self.fps_values.pop(0)

                # Only update FPS display periodically
                if frame_count % fps_update_interval == 0:
                    avg_fps = sum(self.fps_values) / max(len(self.fps_values), 1)
                    self.status_message_signal.emit(f"Inference running | FPS: {avg_fps:.2f}")

        except Exception as e:
            error_message = f"Error processing frame: {str(e)}"
            print(error_message)
            import traceback
            traceback.print_exc()
            self.status_message_signal.emit("Error during inference!")
        finally:
            # Clean up resources
            if self.cap and self.cap.isOpened():
                self.cap.release()
            self.status_message_signal.emit("Inference stopped")
