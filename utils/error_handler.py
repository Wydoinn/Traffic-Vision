import sys
import traceback
from typing import Optional

from PyQt6.QtWidgets import QMessageBox, QApplication
from logger import logger

def show_error_dialog(title: str, message: str, details: Optional[str] = None):
    """Shows an error dialog to the user."""
    # Ensure we have a QApplication instance
    if not QApplication.instance():
        return

    try:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        if details:
            msg_box.setDetailedText(details)

        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    except Exception as e:
        # Last resort if we can't even show the error dialog
        logger.critical(f"Failed to show error dialog: {e}")
        print(f"ERROR: {title} - {message}")
        if details:
            print(f"DETAILS: {details}")

def global_exception_handler(exctype, value, tb):
    """
    Global unhandled exception handler that logs and shows dialog for unhandled exceptions.
    """
    # Log the error
    error_details = ''.join(traceback.format_exception(exctype, value, tb))
    logger.critical(f"Unhandled exception: {str(value)}\n{error_details}")

    # Show error dialog if we have a QApplication
    if QApplication.instance():
        show_error_dialog(
            title="Unhandled Error",
            message=f"An unexpected error occurred: {str(value)}",
            details=error_details
        )
    else:
        print(f"CRITICAL ERROR: {str(value)}\n{error_details}")

    # Call the original exception handler
    sys.__excepthook__(exctype, value, tb)

# Install the global exception handler
sys.excepthook = global_exception_handler
