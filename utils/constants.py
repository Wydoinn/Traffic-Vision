# Constants for settings and UI elements
SETTINGS_FILE = "configs/settings.json"
DEFAULT_CONFIDENCE_THRESHOLD = 0.40
DEFAULT_IOU_THRESHOLD = 0.45
DEFAULT_IMG_SIZE = 640
DEFAULT_MAX_DETECTIONS = 300
DEFAULT_VIDEO_STRIDE = 1
DEFAULT_HALF_PRECISION = False
DEFAULT_AGNOSTIC_NMS = False
DEFAULT_STREAM_BUFFER = False
DEFAULT_KERNEL_SIGMA = 10
DEFAULT_INTENSITY_FACTOR = 0.3
DEFAULT_HEATMAP_OPACITY = 0.6
DEFAULT_COLORMAP = "JET"
DEFAULT_HEATMAP_DECAY = 0.4
DEFAULT_ASPECT_RATIO_MODE = "KeepAspectRatio"

# Ensure settings directory exists
import os
os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)

AVAILABLE_COLORMAPS = ["JET", "PARULA", "TURBO", "VIRIDIS", "INFERNO"]
AVAILABLE_ASPECT_RATIO_MODES = ["KeepAspectRatio", "IgnoreAspectRatio"]

MODEL_TYPE_ZONE = "zone_model"
MODEL_TYPE_EMERGENCY = "emergency_model"
MODEL_TYPE_ACCIDENT = "accident_model"

ZONE_TYPE_VEHICLE = 'vehicle'
ZONE_TYPE_PEDESTRIAN = 'pedestrian'

# Model format constants
MODEL_FORMAT_PYTORCH = "pytorch"
MODEL_FORMAT_ONNX = "onnx"
MODEL_FORMAT_TENSORRT = "tensorrt"
MODEL_FORMAT_COREML = "coreml"

# Device handling constants
DEVICE_CPU = "cpu"
DEVICE_CUDA = "cuda"
DEVICE_MPS = "mps"

# Model format info with extension and recommended devices
MODEL_FORMAT_INFO = {
    MODEL_FORMAT_PYTORCH: {
        "extensions": ['.pt', '.pth'],
        "supported_devices": [DEVICE_CPU, DEVICE_CUDA, DEVICE_MPS]
    },
    MODEL_FORMAT_ONNX: {
        "extensions": ['.onnx'],
        "supported_devices": [DEVICE_CPU, DEVICE_CUDA]
    },
    MODEL_FORMAT_TENSORRT: {
        "extensions": ['.engine'],
        "supported_devices": [DEVICE_CUDA]
    },
    MODEL_FORMAT_COREML: {
        "extensions": ['.mlpackage'],
        "supported_devices": [DEVICE_MPS, DEVICE_CPU]
    }
}

# Get all supported extensions
SUPPORTED_EXTENSIONS = []
for format_info in MODEL_FORMAT_INFO.values():
    SUPPORTED_EXTENSIONS.extend(format_info["extensions"])

# Telegram notification settings
TELEGRAM_ENABLED_DEFAULT = False
TELEGRAM_API_TOKEN_DEFAULT = ""
TELEGRAM_CHAT_ID_DEFAULT = ""
TELEGRAM_ENABLED_KEY = "telegram_enabled"
TELEGRAM_API_TOKEN_KEY = "telegram_api_token"
TELEGRAM_CHAT_ID_KEY = "telegram_chat_id"
