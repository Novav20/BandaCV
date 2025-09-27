import cv2

class AppConfig:
    """Configuration class for the BandaCV application.

    This class centralizes all the configuration parameters for the application,
    including camera settings, vision processing thresholds, serial communication
    settings, and other constants.
    """
    # Camera Settings
    WEBCAM_INDEX = 0
    CAMERA_RESOLUTION = (600, 600) # Renamed from CAMERA_ZISE for clarity

    # Vision Processing Thresholds
    MAX_SAMPLES = 100 # For data deque in main
    LARGE_SIZE_THRESHOLD_CM = 5.0
    MEDIUM_SIZE_THRESHOLD_CM = 4.0
    SMALL_SIZE_THRESHOLD_CM = 2.0 # Can be inferred, but kept for explicit definition
    CALIBRATION_CIRCLE_DIAMETER_CM = 5.0
    COLOR_AREA_THRESHOLD = 250
    SHAPE_AREA_THRESHOLD = 150

    # Serial Communication Settings
    BAUDRATE = 9600
    # List of known serial device identifiers (substrings to search in description or hwid)
    # Add common identifiers for Arduino, ESP32, Raspberry Pi, etc.
    SERIAL_DEVICE_IDENTIFIERS = [
        "VID:PID=2341:0043",  # Arduino Uno
        "Arduino",
        "VID:PID=10C4:EA60",  # CP210x (common for ESP32)
        "VID:PID=1A86:7523",  # CH340 (common for ESP32)
        "USB-SERIAL CH340",
        "ESP32",
        "ttyACM",             # Generic ACM device (often Arduinos)
        "ttyUSB"             # Generic USB serial (often various microcontrollers)
    ]

    # Application Logic Timings
    DETECTION_PROCESSING_TIME_SECONDS = 2 # Consolidated from DETECTION_DELAY and PROCESSING_TIME
    UI_UPDATE_INTERVAL_MS = 0 # INTERVAL from cvband.py, for UI refresh rate

    # Color Detection HSV Ranges (example, these should be fine-tuned)
    RED_LOWER_HSV = (0, 120, 70)
    RED_UPPER_HSV = (10, 255, 255)
    YELLOW_LOWER_HSV = (20, 100, 100)
    YELLOW_UPPER_HSV = (30, 255, 255)
    GREEN_LOWER_HSV = (31, 16, 17)
    GREEN_UPPER_HSV = (78, 255, 255)

    # Kernel sizes for morphology operations
    MORPHOLOGY_KERNEL_SIZE = 5

    # Font settings for OpenCV text
    OPENCV_FONT = cv2.FONT_HERSHEY_SIMPLEX
    OPENCV_FONT_SCALE = 0.5
    OPENCV_FONT_THICKNESS = 2
