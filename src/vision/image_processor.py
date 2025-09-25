import cv2
import numpy as np
from src.config.config import AppConfig
from src.vision.classifiers import BaseClassifier, ServoCode

class ImageProcessor:
    def __init__(self, config: AppConfig):
        self.config = config

    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Applies common preprocessing steps to the frame.
        For now, it just returns the frame, but can be extended later.
        """
        # Example: Convert to grayscale, apply blurring, etc.
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        return frame

    def process_frame(self, frame: np.ndarray, classifier: BaseClassifier) -> (ServoCode, np.ndarray):
        """Processes a frame using the provided classifier.
        Returns the detected servo code and the annotated frame.
        """
        if classifier is None:
            return ServoCode.UNKNOWN, frame

        preprocessed_frame = self.preprocess_frame(frame)
        servo_code, annotated_frame = classifier.classify(preprocessed_frame)
        return servo_code, annotated_frame
