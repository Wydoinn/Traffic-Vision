import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

class AppLogger:
    """
    Application-wide logger that provides consistent logging across all modules
    with file and console output.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, log_level=logging.INFO, log_dir="logs"):
        if self._initialized:
            return

        self._initialized = True
        self.logger = logging.getLogger("TrafficVision")
        self.logger.setLevel(log_level)
        self.log_dir = log_dir
        self.setup_logger()

    def setup_logger(self):
        """Set up logging to file and console."""
        # Create logs directory if it doesn't exist
        if not os.path.exists(self.log_dir):
            try:
                os.makedirs(self.log_dir)
            except OSError as e:
                sys.stderr.write(f"Error creating log directory: {e}\n")
                return

        # Log file path with timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(self.log_dir, f"traffic_vision_{timestamp}.log")

        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )

        # File handler with rotation (10MB max size, keep 10 backup files)
        try:
            file_handler = RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=10
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            sys.stderr.write(f"Error setting up log file: {e}\n")

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        """Returns the logger instance."""
        return self.logger

# Create a global logger instance
logger = AppLogger().get_logger()

# Define convenience methods
def debug(message):
    logger.debug(message)

def info(message):
    logger.info(message)

def warning(message):
    logger.warning(message)

def error(message):
    logger.error(message)

def critical(message):
    logger.critical(message)

def exception(message):
    logger.exception(message)
