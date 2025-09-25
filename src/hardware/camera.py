import cv2
from src.config.config import AppConfig

class Camera:
    def __init__(self, camera_index=AppConfig.WEBCAM_INDEX, resolution=AppConfig.CAMERA_RESOLUTION):
        self.camera_index = camera_index
        self.resolution = resolution
        self.cap = None

    def initialize(self):
        """Initializes the camera."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise IOError(f"Cannot open webcam with index {self.camera_index}")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        print(f"Camera initialized with index {self.camera_index} and resolution {self.resolution}")

    def read_frame(self):
        """Reads a frame from the camera."""
        if self.cap is None or not self.cap.isOpened():
            raise IOError("Camera not initialized or already released.")
        ret, frame = self.cap.read()
        if not ret:
            print("Warning: Could not read frame from camera.")
            return None
        return frame

    def release(self):
        """Releases the camera resources."""
        if self.cap is not None:
            self.cap.release()
            print("Camera resources released.")
        self.cap = None
