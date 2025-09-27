import cv2
import numpy as np
from src.config.config import AppConfig
from src.vision.classifiers import BaseClassifier, ServoCode

class ImageProcessor:
    """Processes image frames using a given classifier.

    This class is responsible for orchestrating the image processing pipeline.
    It can apply preprocessing steps to a frame and then use a classifier to
    detect and classify objects.

    Args:
        config (AppConfig): The application configuration object.
    """
    def __init__(self, config: AppConfig):
        self.config = config

    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Applies preprocessing steps to an image frame.

        This method can be extended to include steps like grayscale conversion,
        blurring, etc.

        Args:
            frame (np.ndarray): The input frame.

        Returns:
            np.ndarray: The preprocessed frame.
        """
        # Example: Convert to grayscale, apply blurring, etc.
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        return frame

    def process_frame(self, frame: np.ndarray, classifier: BaseClassifier) -> tuple[ServoCode, np.ndarray]:
        """Processes a frame using a given classifier.

        Args:
            frame (np.ndarray): The input frame.
            classifier (BaseClassifier): The classifier to use for processing.

        Returns:
            tuple[ServoCode, np.ndarray]: A tuple containing the servo code and the
                                           processed frame with annotations.
        """
        if classifier is None:
            return ServoCode.UNKNOWN, frame

        preprocessed_frame = self.preprocess_frame(frame)
        servo_code, annotated_frame = classifier.classify(preprocessed_frame)
        return servo_code, annotated_frame
