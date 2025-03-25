from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QGroupBox, QGridLayout,
                             QLabel, QLineEdit, QPushButton, QSpinBox, QDoubleSpinBox,
                             QComboBox, QCheckBox, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt
from utils.constants import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import ZoneManagerGUI

class SettingsTab(QScrollArea):
    def __init__(self, parent: 'ZoneManagerGUI'):
        super().__init__(parent)
        self.main_window = parent
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content_widget = QWidget()
        self.setWidget(content_widget)
        self.settings_layout = QVBoxLayout(content_widget)
        self.setup_ui()

    def setup_ui(self):
        settings_group_layout = QVBoxLayout()
        settings_group_layout.addWidget(self.create_model_paths_group())
        settings_group_layout.addWidget(self.create_inference_settings_group())
        settings_group_layout.addWidget(self.create_heatmap_settings_group())
        settings_group_layout.addWidget(self.create_display_settings_group())

        self.settings_layout.addLayout(settings_group_layout)

        # Add Telegram notification settings
        self.add_telegram_notification_settings()

        # Move save settings button to bottom
        save_settings_btn = QPushButton("Save Settings")
        save_settings_btn.setToolTip("Save all settings to configuration file")
        save_settings_btn.clicked.connect(self.save_settings_gui)
        self.settings_layout.addWidget(save_settings_btn)

    def create_model_paths_group(self):
        """Creates the model paths settings group box with support for multiple model formats."""
        model_paths_group = QGroupBox("Model Paths")
        model_paths_grid = QGridLayout()
        model_paths_group.setLayout(model_paths_grid)

        model_paths_grid.addWidget(QLabel("Object:"), 0, 0)
        self.zone_model_path_edit = QLineEdit(self.main_window.settings["model_paths"][MODEL_TYPE_ZONE])
        self.zone_model_path_edit.setToolTip("Path to the object detection model used for vehicles and pedestrians")
        model_paths_grid.addWidget(self.zone_model_path_edit, 0, 1)
        zone_model_path_button = QPushButton("Browse")
        zone_model_path_button.setToolTip("Select object detection model file")
        zone_model_path_button.clicked.connect(lambda: self.main_window.browse_model_path(self.zone_model_path_edit, MODEL_TYPE_ZONE))
        model_paths_grid.addWidget(zone_model_path_button, 0, 2)

        model_paths_grid.addWidget(QLabel("Emergency:"), 1, 0)
        self.emergency_model_path_edit = QLineEdit(self.main_window.settings["model_paths"][MODEL_TYPE_EMERGENCY])
        self.emergency_model_path_edit.setToolTip("Path to the model used for emergency vehicle detection")
        model_paths_grid.addWidget(self.emergency_model_path_edit, 1, 1)
        emergency_model_path_button = QPushButton("Browse")
        emergency_model_path_button.setToolTip("Select emergency vehicle detection model file")
        emergency_model_path_button.clicked.connect(lambda: self.main_window.browse_model_path(self.emergency_model_path_edit, MODEL_TYPE_EMERGENCY))
        model_paths_grid.addWidget(emergency_model_path_button, 1, 2)

        model_paths_grid.addWidget(QLabel("Accident:"), 2, 0)
        self.accident_model_path_edit = QLineEdit(self.main_window.settings["model_paths"][MODEL_TYPE_ACCIDENT])
        self.accident_model_path_edit.setToolTip("Path to the model used for accident detection")
        model_paths_grid.addWidget(self.accident_model_path_edit, 2, 1)
        accident_model_path_button = QPushButton("Browse")
        accident_model_path_button.setToolTip("Select accident detection model file")
        accident_model_path_button.clicked.connect(lambda: self.main_window.browse_model_path(self.accident_model_path_edit, MODEL_TYPE_ACCIDENT))
        model_paths_grid.addWidget(accident_model_path_button, 2, 2)

        return model_paths_group

    def create_model_specific_settings_group(self, model_type, title):
        """Creates a settings group for a specific model type."""
        settings_group = QGroupBox(title)
        settings_grid = QGridLayout()
        settings_group.setLayout(settings_grid)

        # Get the current settings or defaults
        model_settings = self.main_window.settings["inference_settings"].get(
            model_type, {"confidence_threshold": DEFAULT_CONFIDENCE_THRESHOLD, "iou_threshold": DEFAULT_IOU_THRESHOLD}
        )

        # Create confidence threshold setting
        settings_grid.addWidget(QLabel("Confidence Threshold:"), 0, 0)
        conf_spin = QDoubleSpinBox()
        conf_spin.setRange(0.0, 1.0)
        conf_spin.setSingleStep(0.05)
        conf_spin.setValue(model_settings.get("confidence_threshold", DEFAULT_CONFIDENCE_THRESHOLD))
        conf_spin.setToolTip("Minimum confidence score required for a detection to be considered valid")
        settings_grid.addWidget(conf_spin, 0, 1)

        # Create IOU threshold setting
        settings_grid.addWidget(QLabel("IOU Threshold:"), 1, 0)
        iou_spin = QDoubleSpinBox()
        iou_spin.setRange(0.0, 1.0)
        iou_spin.setSingleStep(0.05)
        iou_spin.setValue(model_settings.get("iou_threshold", DEFAULT_IOU_THRESHOLD))
        iou_spin.setToolTip("Intersection over Union threshold for filtering overlapping detections")
        settings_grid.addWidget(iou_spin, 1, 1)

        # Store the spin boxes for later access
        setattr(self, f"{model_type}_conf_threshold_spin", conf_spin)
        setattr(self, f"{model_type}_iou_threshold_spin", iou_spin)

        return settings_group

    def create_inference_settings_group(self):
        """Creates the inference settings group box."""
        inference_settings_group = QGroupBox("Inference Settings")
        inference_settings_layout = QVBoxLayout()
        inference_settings_layout.addSpacing(10)
        inference_settings_group.setLayout(inference_settings_layout)

        # Create model-specific settings groups
        inference_settings_layout.addWidget(self.create_model_specific_settings_group(
            MODEL_TYPE_ZONE, "Object Model"
        ))
        inference_settings_layout.addWidget(self.create_model_specific_settings_group(
            MODEL_TYPE_EMERGENCY, "Emergency Model"
        ))
        inference_settings_layout.addWidget(self.create_model_specific_settings_group(
            MODEL_TYPE_ACCIDENT, "Accident Model"
        ))
        inference_settings_layout.addWidget(self.create_common_inference_settings_group())

        return inference_settings_group

    def create_common_inference_settings_group(self):
        """Creates common inference settings group box."""
        common_inference_settings_group = QGroupBox("Common Settings")
        common_inference_settings_grid = QGridLayout()
        common_inference_settings_group.setLayout(common_inference_settings_grid)
        row_idx = 0

        common_inference_settings_grid.addWidget(QLabel("Image Size:"), row_idx, 0)
        self.imgsz_spin = QSpinBox()
        self.imgsz_spin.setRange(320, 1920)
        self.imgsz_spin.setSingleStep(32)
        self.imgsz_spin.setValue(self.main_window.settings["inference_settings"]["imgsz"])
        self.imgsz_spin.setToolTip("Input image size for the model (larger = more accurate but slower)")
        common_inference_settings_grid.addWidget(self.imgsz_spin, row_idx, 1)
        row_idx += 1

        common_inference_settings_grid.addWidget(QLabel("Max Detections:"), row_idx, 0)
        self.max_det_spin = QSpinBox()
        self.max_det_spin.setRange(1, 1000)
        self.max_det_spin.setSingleStep(50)
        self.max_det_spin.setValue(self.main_window.settings["inference_settings"]["max_det"])
        self.max_det_spin.setToolTip("Maximum number of detections per frame")
        common_inference_settings_grid.addWidget(self.max_det_spin, row_idx, 1)
        row_idx += 1

        common_inference_settings_grid.addWidget(QLabel("Video Stride:"), row_idx, 0)
        self.vid_stride_spin = QSpinBox()
        self.vid_stride_spin.setRange(1, 10)
        self.vid_stride_spin.setToolTip("Process every nth frame (higher values improve performance but reduce accuracy)")

        # Ensure a valid default value
        vid_stride = self.main_window.settings["inference_settings"].get("vid_stride", DEFAULT_VIDEO_STRIDE)
        if not isinstance(vid_stride, int) or vid_stride < 1 or vid_stride > 10:
            vid_stride = DEFAULT_VIDEO_STRIDE
        self.vid_stride_spin.setValue(vid_stride)

        common_inference_settings_grid.addWidget(self.vid_stride_spin, row_idx, 1)
        row_idx += 1
        common_inference_settings_grid.setRowMinimumHeight(row_idx, 30)
        row_idx += 1

        common_inference_settings_grid.addWidget(QLabel("Half Precision:"), row_idx, 0)
        self.half_check = QCheckBox()
        self.half_check.setChecked(self.main_window.settings["inference_settings"]["half"])
        self.half_check.setToolTip("Use half-precision floating point (FP16) for faster inference")
        common_inference_settings_grid.addWidget(self.half_check, row_idx, 1)
        common_inference_settings_grid.setRowMinimumHeight(row_idx, 30)
        row_idx += 1

        common_inference_settings_grid.addWidget(QLabel("Agnostic NMS:"), row_idx, 0)
        self.agnostic_nms_check = QCheckBox()
        self.agnostic_nms_check.setChecked(self.main_window.settings["inference_settings"]["agnostic_nms"])
        self.agnostic_nms_check.setToolTip("Class-agnostic NMS for better multi-class detection")
        common_inference_settings_grid.addWidget(self.agnostic_nms_check, row_idx, 1)
        common_inference_settings_grid.setRowMinimumHeight(row_idx, 30)
        row_idx += 1

        common_inference_settings_grid.addWidget(QLabel("Stream Buffer:"), row_idx, 0)
        self.stream_buffer_check = QCheckBox()
        self.stream_buffer_check.setChecked(self.main_window.settings["inference_settings"]["stream_buffer"])
        self.stream_buffer_check.setToolTip("Buffer frames for smoother video playback")
        common_inference_settings_grid.addWidget(self.stream_buffer_check, row_idx, 1)
        common_inference_settings_grid.setRowMinimumHeight(row_idx, 30)
        row_idx += 1
        return common_inference_settings_group

    def create_heatmap_settings_group(self):
        """Creates the heatmap settings group box."""
        heatmap_settings_group = QGroupBox("Heatmap Settings")
        heatmap_settings_grid = QGridLayout()
        heatmap_settings_group.setLayout(heatmap_settings_grid)

        heatmap_settings_grid.addWidget(QLabel("Kernel Sigma:"), 0, 0)
        self.heatmap_sigma_spin = QSpinBox()
        self.heatmap_sigma_spin.setRange(1, 200)
        self.heatmap_sigma_spin.setValue(self.main_window.settings["heatmap_settings"]["kernel_sigma"])
        self.heatmap_sigma_spin.setToolTip("Gaussian kernel size for heatmap smoothing (larger = more blur)")
        heatmap_settings_grid.addWidget(self.heatmap_sigma_spin, 0, 1)

        heatmap_settings_grid.addWidget(QLabel("Intensity Factor:"), 1, 0)
        self.heatmap_intensity_spin = QDoubleSpinBox()
        self.heatmap_intensity_spin.setRange(0.0, 1.0)
        self.heatmap_intensity_spin.setSingleStep(0.05)
        self.heatmap_intensity_spin.setValue(self.main_window.settings["heatmap_settings"]["intensity_factor"])
        self.heatmap_intensity_spin.setToolTip("Intensity multiplier for heatmap visualization")
        heatmap_settings_grid.addWidget(self.heatmap_intensity_spin, 1, 1)

        heatmap_settings_grid.addWidget(QLabel("Opacity:"), 2, 0)
        self.heatmap_opacity_spin = QDoubleSpinBox()
        self.heatmap_opacity_spin.setRange(0.0, 1.0)
        self.heatmap_opacity_spin.setSingleStep(0.05)
        self.heatmap_opacity_spin.setValue(self.main_window.settings["heatmap_settings"]["heatmap_opacity"])
        self.heatmap_opacity_spin.setToolTip("Opacity of the heatmap overlay (0 = transparent, 1 = opaque)")
        heatmap_settings_grid.addWidget(self.heatmap_opacity_spin, 2, 1)

        heatmap_settings_grid.addWidget(QLabel("Heatmap Decay:"), 3, 0)
        self.heatmap_decay_spin = QDoubleSpinBox()
        self.heatmap_decay_spin.setRange(0.0, 1.0)
        self.heatmap_decay_spin.setSingleStep(0.05)
        self.heatmap_decay_spin.setValue(self.main_window.settings["heatmap_settings"]["heatmap_decay"])
        self.heatmap_decay_spin.setToolTip("Rate at which heatmap points fade over time")
        heatmap_settings_grid.addWidget(self.heatmap_decay_spin, 3, 1)

        heatmap_settings_grid.addWidget(QLabel("Colormap:"), 4, 0)
        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems(AVAILABLE_COLORMAPS)
        self.colormap_combo.setCurrentText(self.main_window.settings["heatmap_settings"]["colormap"])
        self.colormap_combo.setToolTip("Color scheme used for the heatmap visualization")
        heatmap_settings_grid.addWidget(self.colormap_combo, 4, 1)
        return heatmap_settings_group

    def create_display_settings_group(self):
        """Creates the display settings group box."""
        display_settings_group = QGroupBox("Display Settings")
        display_settings_grid = QGridLayout()
        display_settings_group.setLayout(display_settings_grid)

        display_settings_grid.addWidget(QLabel("Aspect Ratio Mode:"), 0, 0)
        self.aspect_ratio_combo = QComboBox()
        self.aspect_ratio_combo.addItems(AVAILABLE_ASPECT_RATIO_MODES)
        self.aspect_ratio_combo.setCurrentText(self.main_window.settings["display_settings"]["aspect_ratio_mode"])
        display_settings_grid.addWidget(self.aspect_ratio_combo, 0, 1)
        return display_settings_group

    def add_telegram_notification_settings(self):
        """Add Telegram notification settings to the settings tab."""
        telegram_group = QGroupBox("Telegram Notifications")
        telegram_layout = QVBoxLayout()

        # Enabled checkbox
        self.telegram_enabled = QCheckBox("Enable Telegram Notifications")
        self.telegram_enabled.setToolTip("Enable/Disable sending notifications via Telegram bot")
        telegram_enabled_value = self.main_window.settings.get("telegram_settings", {}).get(
            TELEGRAM_ENABLED_KEY, TELEGRAM_ENABLED_DEFAULT)
        self.telegram_enabled.setChecked(telegram_enabled_value)

        # API Token input
        token_layout = QHBoxLayout()
        token_label = QLabel("API Token:")
        self.telegram_api_token = QLineEdit()
        self.telegram_api_token.setEchoMode(QLineEdit.EchoMode.Password)
        self.telegram_api_token.setPlaceholderText("Enter Telegram Bot API Token")
        self.telegram_api_token.setToolTip("Bot API token obtained from @BotFather")
        telegram_api_token_value = self.main_window.settings.get("telegram_settings", {}).get(
            TELEGRAM_API_TOKEN_KEY, TELEGRAM_API_TOKEN_DEFAULT)
        self.telegram_api_token.setText(telegram_api_token_value)
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.telegram_api_token)

        # Chat ID input
        chat_id_layout = QHBoxLayout()
        chat_id_label = QLabel("Chat ID:")
        self.telegram_chat_id = QLineEdit()
        self.telegram_chat_id.setPlaceholderText("Enter Telegram Chat ID")
        self.telegram_chat_id.setToolTip("Chat ID where notifications will be sent")
        telegram_chat_id_value = self.main_window.settings.get("telegram_settings", {}).get(
            TELEGRAM_CHAT_ID_KEY, TELEGRAM_CHAT_ID_DEFAULT)
        self.telegram_chat_id.setText(telegram_chat_id_value)
        chat_id_layout.addWidget(chat_id_label)
        chat_id_layout.addWidget(self.telegram_chat_id)

        # Test notification button
        self.test_notification_btn = QPushButton("Test Notification")
        self.test_notification_btn.setToolTip("Send a test notification to verify configuration")
        self.test_notification_btn.clicked.connect(self.test_telegram_notification)

        # Help text
        help_text = QLabel(
            "1. Create a bot with @BotFather in Telegram\n"
            "2. Copy the API token provided\n"
            "3. Send a message to your bot\n"
            "4. Get your Chat ID from https://api.telegram.org/bot<YourBOTToken>/getUpdates"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: gray; font-size: 10px;")

        # Add all widgets to layout
        telegram_layout.addWidget(self.telegram_enabled)
        telegram_layout.addLayout(token_layout)
        telegram_layout.addLayout(chat_id_layout)
        telegram_layout.addWidget(self.test_notification_btn)
        telegram_layout.addWidget(help_text)

        telegram_group.setLayout(telegram_layout)
        self.settings_layout.addWidget(telegram_group)

    def test_telegram_notification(self):
        """Test Telegram notification functionality."""
        if not self.telegram_api_token.text() or not self.telegram_chat_id.text():
            QMessageBox.warning(self, "Configuration Error",
                               "Please enter both API Token and Chat ID before testing.")
            return

        # Create a test notification
        from utils.notifier import TelegramNotifier
        notifier = TelegramNotifier(
            api_token=self.telegram_api_token.text(),
            chat_id=self.telegram_chat_id.text()
        )

        # Send a test message (without image)
        success = notifier.send_accident_notification(
            image=None,
            location="Test Location",
            details="This is a test notification from Traffic Vision."
        )

        if success:
            QMessageBox.information(self, "Test Successful",
                                   "Test notification sent successfully!")
        else:
            QMessageBox.critical(self, "Test Failed",
                               "Failed to send test notification. Please check your API token and chat ID.")

    def save_settings_gui(self):
        """Saves settings from GUI elements to settings.json and restarts the application."""
        # Model paths
        self.main_window.settings["model_paths"][MODEL_TYPE_ZONE] = self.zone_model_path_edit.text()
        self.main_window.settings["model_paths"][MODEL_TYPE_EMERGENCY] = self.emergency_model_path_edit.text()
        self.main_window.settings["model_paths"][MODEL_TYPE_ACCIDENT] = self.accident_model_path_edit.text()

        # Model-specific inference settings using a loop for each model type
        for model_type in [MODEL_TYPE_ZONE, MODEL_TYPE_EMERGENCY, MODEL_TYPE_ACCIDENT]:
            conf_spin = getattr(self, f"{model_type}_conf_threshold_spin")
            iou_spin = getattr(self, f"{model_type}_iou_threshold_spin")
            self.main_window.settings["inference_settings"][model_type]["confidence_threshold"] = conf_spin.value()
            self.main_window.settings["inference_settings"][model_type]["iou_threshold"] = iou_spin.value()

        # Common inference settings
        self.main_window.settings["inference_settings"]["imgsz"] = self.imgsz_spin.value()
        self.main_window.settings["inference_settings"]["max_det"] = self.max_det_spin.value()
        self.main_window.settings["inference_settings"]["vid_stride"] = self.vid_stride_spin.value()
        self.main_window.settings["inference_settings"]["half"] = self.half_check.isChecked()
        self.main_window.settings["inference_settings"]["agnostic_nms"] = self.agnostic_nms_check.isChecked()
        self.main_window.settings["inference_settings"]["stream_buffer"] = self.stream_buffer_check.isChecked()

        # Heatmap settings
        self.main_window.settings["heatmap_settings"]["kernel_sigma"] = self.heatmap_sigma_spin.value()
        self.main_window.settings["heatmap_settings"]["intensity_factor"] = self.heatmap_intensity_spin.value()
        self.main_window.settings["heatmap_settings"]["heatmap_opacity"] = self.heatmap_opacity_spin.value()
        self.main_window.settings["heatmap_settings"]["colormap"] = self.colormap_combo.currentText()
        self.main_window.settings["heatmap_settings"]["heatmap_decay"] = self.heatmap_decay_spin.value()

        # Display settings
        self.main_window.settings["display_settings"]["aspect_ratio_mode"] = self.aspect_ratio_combo.currentText()

        # Save Telegram notification settings
        if "telegram_settings" not in self.main_window.settings:
            self.main_window.settings["telegram_settings"] = {}

        self.main_window.settings["telegram_settings"][TELEGRAM_ENABLED_KEY] = self.telegram_enabled.isChecked()
        self.main_window.settings["telegram_settings"][TELEGRAM_API_TOKEN_KEY] = self.telegram_api_token.text()
        self.main_window.settings["telegram_settings"][TELEGRAM_CHAT_ID_KEY] = self.telegram_chat_id.text()

        # Save to file
        self.main_window.save_settings()

        from PyQt6.QtWidgets import QMessageBox
        # Ask the user if they want to restart the application
        restart_msg = QMessageBox()
        restart_msg.setIcon(QMessageBox.Icon.Question)
        restart_msg.setWindowTitle("Restart Required")
        restart_msg.setText("Settings saved. Some settings require a restart to take effect.")
        restart_msg.setInformativeText("Would you like to restart the application now?")
        restart_msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        restart_msg.setDefaultButton(QMessageBox.StandardButton.Yes)

        if restart_msg.exec() == QMessageBox.StandardButton.Yes:
            self.main_window.restart_application()
        else:
            # Just apply what we can without restart
            self.main_window.apply_settings_to_models()
            QMessageBox.information(self, "Settings Saved", "Settings saved successfully. Some changes may require restarting the application to take full effect.")
            self.main_window.status_bar.showMessage("Settings saved", 3000)
