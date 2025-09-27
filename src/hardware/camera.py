import cv2
from src.config.config import AppConfig

class Camera:
    """A wrapper class for the OpenCV VideoCapture.

    This class provides a simple interface for initializing, reading frames from,
    and releasing a webcam.

    Args:
        camera_index (int): The index of the camera to use.
        resolution (tuple): The desired resolution of the camera feed.
    """
    def __init__(self, camera_index=AppConfig.WEBCAM_INDEX, resolution=AppConfig.CAMERA_RESOLUTION):
        self.camera_index = camera_index
        self.resolution = resolution
        self.cap = None

    def initialize(self):
        """Initializes the camera capture.

        Raises:
            IOError: If the camera cannot be opened.
        """
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise IOError(f"Cannot open webcam with index {self.camera_index}")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        print(f"Camera initialized with index {self.camera_index} and resolution {self.resolution}")

    def read_frame(self):
        """Reads a single frame from the camera.

        Returns:
            np.ndarray: The captured frame, or None if a frame could not be read.

        Raises:
            IOError: If the camera is not initialized or has been released.
        """
        if self.cap is None or not self.cap.isOpened():
            raise IOError("Camera not initialized or already released.")
        ret, frame = self.cap.read()
        if not ret:
            print("Warning: Could not read frame from camera.")
            return None
        return frame

    def release(self):
        """Releases the camera capture and cleans up resources."""
        if self.cap is not None:
            self.cap.release()
            print("Camera resources released.")
        self.cap = None
