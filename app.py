"""
Traffic Vision: AI-Powered Traffic Monitoring System and Signal Optimization
Main application entry point with initialization and error handling.
"""
import os
import sys
import argparse
from pathlib import Path
import signal
import faulthandler
from typing import List

from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QTimer

# Enable faulthandler to help debug segfaults
faulthandler.enable()

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import our modules
from version import get_version_string, get_version_info
from logger import info, error, exception
from config_manager import ConfigManager
from utils.error_handler import show_error_dialog
from utils.health_monitor import HealthMonitor
from main import ZoneManagerGUI

# Application metadata
APP_NAME = "Traffic Vision"
APP_ORGANIZATION = "Unkown"
APP_DOMAIN = "github.com/Wydoinn/Traffic-Vision"

# Constants
CONFIG_FILENAME = "configs/settings.json"
DEFAULT_LOG_LEVEL = "INFO"

class Application:
    """Main application class that handles initialization and lifecycle."""
    def __init__(self, args: List[str]):
        self.args = self._parse_arguments(args)
        self.app = None
        self.main_window = None
        self.config_manager = None
        self.health_monitor = None
        self.splash = None

    def _parse_arguments(self, args: List[str]) -> argparse.Namespace:
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(description=f"{APP_NAME} - Traffic Management System")
        parser.add_argument("--version", action="store_true", help="Show version information and exit")
        parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
        parser.add_argument("--config", default=CONFIG_FILENAME, help="Path to configuration file")
        parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                          default=DEFAULT_LOG_LEVEL, help="Set logging level")

        return parser.parse_args(args)

    def run(self) -> int:
        """Run the application and return exit code."""
        # Show version and exit if requested
        if self.args.version:
            print(get_version_string(detailed=True))
            return 0

        try:
            # Initialize Qt Application
            self.app = QApplication([])
            self.app.setApplicationName(APP_NAME)
            self.app.setOrganizationName(APP_ORGANIZATION)
            self.app.setOrganizationDomain(APP_DOMAIN)
            self.app.setWindowIcon(QIcon("static/icons/traffic-light.png"))

            # Show splash screen
            self._show_splash()

            # Initialize configuration
            config_path = self.args.config
            self._init_configuration(config_path)

            # Setup signal handlers for clean shutdown
            self._setup_signal_handlers()

            # Initialize health monitoring
            self._init_health_monitoring()

            # Create and show the main window
            self._create_main_window()

            # Hide splash screen and show main window after a short delay
            QTimer.singleShot(1500, self._finish_startup)

            # Start the Qt event loop
            return self.app.exec()

        except Exception as e:
            exception(f"Error initializing application: {e}")
            self._cleanup_resources()
            if self.app:
                show_error_dialog("Initialization Error",
                                 f"Failed to initialize the application: {e}")
            return 1

    def _show_splash(self):
        """Show a splash screen while the app loads."""
        splash_path = os.path.join(os.path.dirname(__file__), "static/images/splash.png")

        # Check if splash image exists, otherwise use a simple splash
        if os.path.exists(splash_path):
            pixmap = QPixmap(splash_path)
        else:
            # Create a simple splash screen with version info
            from PyQt6.QtGui import QFont, QPainter, QColor, QLinearGradient
            pixmap = QPixmap(600, 400)

            # Create gradient background
            gradient = QLinearGradient(0, 0, 0, 400)
            gradient.setColorAt(0.0, QColor(40, 40, 80))
            gradient.setColorAt(1.0, QColor(30, 30, 60))

            painter = QPainter(pixmap)
            painter.fillRect(0, 0, 600, 400, gradient)

            # Draw application name
            title_font = QFont("Arial", 36, QFont.Weight.Bold)
            painter.setFont(title_font)
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(30, 80, APP_NAME)

            # Draw version info
            version_font = QFont("Arial", 14)
            painter.setFont(version_font)
            painter.drawText(30, 120, f"Version {get_version_info()['version']}")

            # Draw loading message
            status_font = QFont("Arial", 12)
            painter.setFont(status_font)
            painter.drawText(30, 360, "Initializing application...")

            painter.end()

        self.splash = QSplashScreen(pixmap, Qt.WindowType.WindowStaysOnTopHint)
        self.splash.show()
        self.splash.raise_()
        self.splash.activateWindow() 
        self.app.processEvents()

    def _init_configuration(self, config_path: str):
        """Initialize configuration manager."""
        self.config_manager = ConfigManager(config_path)

        # Set default config based on the main window's default settings
        from main import ZoneManagerGUI
        temp_main = ZoneManagerGUI.__new__(ZoneManagerGUI)
        default_config = temp_main.get_default_settings()
        self.config_manager.set_default_config(default_config)

        # Load config (this will create default if needed)
        config = self.config_manager.load_config()
        if self.splash:
            self.splash.showMessage("Configuration loaded...",
                                   Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
                                   Qt.GlobalColor.white)
            self.app.processEvents()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        # Handle Ctrl+C in console
        signal.signal(signal.SIGINT, self._signal_handler)
        if hasattr(signal, 'SIGBREAK'):  # Windows
            signal.signal(signal.SIGBREAK, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle OS signals for clean shutdown."""
        info(f"Received signal {signum}, shutting down...")
        self._cleanup_resources()
        self.app.quit()

    def _init_health_monitoring(self):
        """Initialize system health monitoring."""
        self.health_monitor = HealthMonitor(check_interval=60.0)

        # Setup alert callback
        self.health_monitor.set_alert_callback(self._health_alert_callback)

        # Start health monitoring
        self.health_monitor.start_monitoring()

        if self.splash:
            self.splash.showMessage("Health monitoring started...",
                                   Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
                                   Qt.GlobalColor.white)
            self.app.processEvents()

    def _health_alert_callback(self, title: str, data: dict):
        """Callback for health monitoring alerts."""
        # Create a non-blocking notification
        message = data.get("message", "System resource usage exceeding thresholds")
        try:
            if hasattr(self, 'main_window') and self.main_window:
                self.main_window.status_bar.showMessage(f"Alert: {message}", 8000)

                # For critical alerts, show dialog too
                if "cpu_percent" in data.get("metrics", {}) and data["metrics"]["cpu_percent"] > 95:
                    QMessageBox.warning(self.main_window, title,
                                       f"{message}\n\nThe system is under heavy load, which may affect performance.")
        except Exception as e:
            error(f"Failed to show health alert: {e}")

    def _create_main_window(self):
        """Create and initialize the main window."""
        if self.splash:
            self.splash.showMessage("Creating main window...",
                                   Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
                                   Qt.GlobalColor.white)
            self.app.processEvents()

        self.main_window = ZoneManagerGUI()

        # Connect to window close event for cleanup
        self.app.aboutToQuit.connect(self._cleanup_resources)

    def _finish_startup(self):
        """Finish startup by hiding splash and showing main window."""
        if self.splash:
            self.splash.finish(self.main_window)
        self.main_window.show()

        # Log startup complete
        info(f"{APP_NAME} started successfully")

    def _cleanup_resources(self):
        """Clean up all resources during shutdown."""
        info("Cleaning up resources...")

        # Stop health monitoring
        if self.health_monitor:
            self.health_monitor.stop_monitoring()

        # Stop inference if running
        if hasattr(self, 'main_window') and self.main_window:
            if hasattr(self.main_window, 'is_inferencing') and self.main_window.is_inferencing:
                self.main_window.stop_inference()

            # Close DB connections
            if hasattr(self.main_window, 'data_collector'):
                if self.main_window.data_collector:
                    self.main_window.data_collector.shutdown()

        info("Shutdown complete")


def main():
    """Application entry point."""
    try:
        app = Application(sys.argv[1:])
        sys.exit(app.run())
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
