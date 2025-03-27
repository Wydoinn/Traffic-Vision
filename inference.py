from PyQt6.QtCore import QThread, pyqtSignal
import cv2
import time

from logger import logger

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
        """Start the inference thread."""
        logger.info(f"Starting inference on video: {self.video_path}")
        self.is_running = True
        self.start()

    def stop_inference(self):
        """Stop the inference thread and release resources."""
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.wait()
        logger.info("Inference thread stopped")

    def run(self):
        """Main thread execution function for processing video frames."""
        try:
            self.cap = cv2.VideoCapture(self.video_path)
            if not self.cap.isOpened():
                error_msg = f"Error: Could not open video file: {self.video_path}"
                logger.error(error_msg)
                self.status_message_signal.emit(error_msg)
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
            fps_update_interval = 1
            last_fps_update = time.time()
            current_fps = 0

            logger.info(f"Inference started with vid_stride={vid_stride}")

            while self.is_running:
                ret, frame = self.cap.read()
                if not ret:
                    # End of video
                    logger.info("End of video reached")
                    self.status_message_signal.emit("End of video reached")
                    break

                frame_count += 1

                # Process only every vid_stride frames
                if (frame_count - 1) % vid_stride != 0:
                    continue

                start_time = time.time()

                # Process frame and collect detection data
                try:
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
                        intersections = self.zone_manager.traffic_light_controller.get_intersections_info()
                        detection_data["intersections"] = intersections

                    # Emit processed frame to main thread
                    self.frame_processed_signal.emit(annotated_frame, heatmap_frame, detection_data)

                    # Calculate and update FPS stats
                    if self.last_frame_time is not None:
                        frame_time = time.time() - start_time
                        self.fps_values.append(1.0 / frame_time if frame_time > 0 else 0)
                        # Keep only the last 30 frames for averaging
                        if len(self.fps_values) > 30:
                            self.fps_values.pop(0)
                        current_fps = sum(self.fps_values) / len(self.fps_values)

                    self.last_frame_time = start_time

                    # Update FPS in status bar periodically
                    if time.time() - last_fps_update > fps_update_interval:
                        self.status_message_signal.emit(f"Processing at {current_fps:.1f} FPS")
                        last_fps_update = time.time()

                except Exception as e:
                    logger.error(f"Error processing frame {frame_count}: {e}")
                    continue

        except Exception as e:
            error_message = f"Error processing video: {str(e)}"
            logger.error(error_message)
            logger.exception("Inference thread exception details")
            self.status_message_signal.emit("Error during inference!")
        finally:
            # Clean up resources
            if self.cap and self.cap.isOpened():
                self.cap.release()
                logger.debug("Video capture released")
            self.status_message_signal.emit("Inference stopped")
