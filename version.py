"""
Version information for the Traffic Vision.
"""
import platform
from datetime import datetime

# Version information
__version__ = "1.0.0"
__build__ = "20250401"
__release__ = "stable"

def get_version_info():
    """Returns detailed version information as a dictionary."""
    return {
        "version": __version__,
        "build": __build__,
        "release": __release__,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "build_date": datetime.now().strftime("%Y-%m-%d"),
        "qt_version": get_qt_version()
    }

def get_qt_version():
    """Returns the Qt version being used."""
    try:
        from PyQt6.QtCore import QT_VERSION_STR
        return QT_VERSION_STR
    except ImportError:
        return "Unknown"

def get_version_string(detailed=False):
    """Returns a formatted version string."""
    if not detailed:
        return f"Traffic Vision v{__version__} ({__release__})"
    else:
        info = get_version_info()
        return (
            f"Traffic Vision v{info['version']} ({info['release']})\n"
            f"Build {info['build']} on {info['build_date']}\n"
            f"Python {info['python_version']} on {info['platform']}\n"
            f"Qt {info['qt_version']}"
        )
