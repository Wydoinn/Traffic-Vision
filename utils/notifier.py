import requests
import cv2
import os
import time
import tempfile
import logging
from typing import Optional
from datetime import datetime

class TelegramNotifier:
    """
    Handles sending notifications with images to Telegram using the Telegram Bot API.
    """
    def __init__(self, api_token: str, chat_id: str):
        """Initialize the Telegram notifier."""
        self.api_token = api_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{api_token}"
        self.cooldown_period = 60
        self.last_notification_time = 0
        self.enabled = bool(api_token and chat_id)

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("TelegramNotifier")

        if self.enabled:
            self._validate_settings()

    def _validate_settings(self):
        """Validate that the API token and chat ID are properly configured."""
        try:
            # Make a simple request to check if token is valid
            response = requests.get(f"{self.base_url}/getMe", timeout=5)
            if not response.status_code == 200:
                self.logger.error(f"Invalid Telegram API token: {response.text}")
                self.enabled = False
                return

            # No direct way to validate chat ID without sending a message
            self.logger.info("Telegram notification system enabled and configured")
        except Exception as e:
            self.logger.error(f"Error validating Telegram settings: {e}")
            self.enabled = False

    def send_accident_notification(self, image: Optional[cv2.Mat] = None,
                                   location: str = "Unknown", details: str = None) -> bool:
        """
        Send an accident notification with image to the configured Telegram chat.
        """
        if not self.enabled:
            self.logger.warning("Telegram notifications are not properly configured or disabled")
            return False

        # Implement cooldown to prevent notification spam
        current_time = time.time()
        if current_time - self.last_notification_time < self.cooldown_period:
            self.logger.info("Notification cooldown active, skipping notification")
            return False

        try:
            # Prepare message text
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"🚨 ACCIDENT DETECTED 🚨\n\n"
            message += f"📍 Location: {location}\n"
            message += f"⏰ Time: {timestamp}\n"

            if details:
                message += f"\nDetails: {details}\n"

            if image is not None:
                # Save image temporarily
                temp_image_path = self._save_temp_image(image)

                # Send photo with caption
                with open(temp_image_path, "rb") as photo:
                    url = f"{self.base_url}/sendPhoto"
                    files = {"photo": photo}
                    data = {"chat_id": self.chat_id, "caption": message}
                    response = requests.post(url, files=files, data=data, timeout=10)

                self._remove_temp_file(temp_image_path)

            else:
                # Send text message if no image
                url = f"{self.base_url}/sendMessage"
                data = {"chat_id": self.chat_id, "text": message, "parse_mode": "HTML"}
                response = requests.post(url, json=data, timeout=10)

            # Check response
            if response.status_code == 200:
                self.last_notification_time = current_time
                self.logger.info("Telegram accident notification sent successfully")
                return True
            else:
                self.logger.error(f"Failed to send Telegram notification: {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Error sending Telegram notification: {e}")
            return False

    def _save_temp_image(self, image: cv2.Mat) -> str:
        """Save image to temporary file and return the path."""
        # Get system temp directory
        temp_dir = tempfile.gettempdir()

        # Create a subdirectory for our accident images
        accident_dir = os.path.join(temp_dir, "accident_images")
        os.makedirs(accident_dir, exist_ok=True)

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(accident_dir, f"accident_{timestamp}.jpg")
        cv2.imwrite(file_path, image)
        return file_path


    def _remove_temp_file(self, file_path: str):
        """Remove temporary file after sending."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            self.logger.error(f"Error removing temporary file {file_path}: {e}")
