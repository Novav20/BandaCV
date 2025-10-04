from enum import Enum
import cv2
import numpy as np
from src.config.config import AppConfig

class ServoCode(Enum):
    """Enum for representing the servo codes to be sent to the Arduino.
    
    IMPORTANT: When multiple members have the same value, the second and
    subsequent members are aliases for the first member. This means that
    `ServoCode.RED` is the same object as `ServoCode.TRIANGLE`.
    The value (e.g., '0') is used for hardware communication.
    """
    # These codes are examples and should be mapped to actual servo actions
    # based on the hardware setup.
    TRIANGLE = '0'
    SQUARE = '1'
    CIRCLE = '2'
    RED = '0'
    YELLOW = '1'
    GREEN = '2'
    SMALL = '0'
    MEDIUM = '1'
    LARGE = '2'
    UNKNOWN = '9' # Default for unclassified or error

class BaseClassifier:
    """Base class for all classifiers."""
    def __init__(self, config: AppConfig):
        self.config = config

    def _draw_text(self, frame: np.ndarray, text: str, position: tuple, color: tuple = (255, 255, 255)):
        """Draws text on a frame."""
        cv2.putText(frame, text, position, self.config.OPENCV_FONT,
                    self.config.OPENCV_FONT_SCALE, color, self.config.OPENCV_FONT_THICKNESS, cv2.LINE_AA)

    def classify(self, frame: np.ndarray) -> tuple[ServoCode, np.ndarray, str]:
        """Abstract method for classifying an object in a frame.

        Returns:
            tuple[ServoCode, np.ndarray, str]: A tuple containing:
                - The servo code for the hardware.
                - The processed frame with annotations.
                - The friendly name of the classification result (e.g., "Red").
        """
        raise NotImplementedError

class ColorClassifier(BaseClassifier):
    """Classifier for detecting objects based on their color."""
    def __init__(self, config: AppConfig):
        super().__init__(config)
        self.red_lower = np.array(self.config.RED_LOWER_HSV)
        self.red_upper = np.array(self.config.RED_UPPER_HSV)
        self.yellow_lower = np.array(self.config.YELLOW_LOWER_HSV)
        self.yellow_upper = np.array(self.config.YELLOW_UPPER_HSV)
        self.green_lower = np.array(self.config.GREEN_LOWER_HSV)
        self.green_upper = np.array(self.config.GREEN_UPPER_HSV)
        self.kernel = np.ones((self.config.MORPHOLOGY_KERNEL_SIZE, self.config.MORPHOLOGY_KERNEL_SIZE), np.uint8)

    def classify(self, frame: np.ndarray) -> tuple[ServoCode, np.ndarray, str]:
        processed_frame = frame.copy()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask_red = cv2.inRange(hsv, self.red_lower, self.red_upper)
        mask_yellow = cv2.inRange(hsv, self.yellow_lower, self.yellow_upper)
        mask_green = cv2.inRange(hsv, self.green_lower, self.green_upper)

        mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, self.kernel)
        mask_yellow = cv2.morphologyEx(mask_yellow, cv2.MORPH_OPEN, self.kernel)
        mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, self.kernel)

        red_count = cv2.countNonZero(mask_red)
        yellow_count = cv2.countNonZero(mask_yellow)
        green_count = cv2.countNonZero(mask_green)

        color = "Unknown"
        color_code = (0, 0, 0) # Black for unknown
        servo_code = ServoCode.UNKNOWN

        if red_count > yellow_count and red_count > green_count:
            color = "Red"
            color_code = (0, 0, 255)
            servo_code = ServoCode.RED
        elif yellow_count > red_count and yellow_count > green_count:
            color = "Yellow"
            color_code = (0, 255, 255)
            servo_code = ServoCode.YELLOW
        elif green_count > red_count and green_count > yellow_count:
            color = "Green"
            color_code = (0, 255, 0)
            servo_code = ServoCode.GREEN

        mask = cv2.bitwise_or(mask_red, mask_yellow)
        mask = cv2.bitwise_or(mask, mask_green)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        max_area = 0
        max_c = None
        for c in contours:
            area = cv2.contourArea(c)
            if area > self.config.COLOR_AREA_THRESHOLD and area > max_area:
                max_area = area
                max_c = c

        if max_c is not None:
            x,y,w,h = cv2.boundingRect(max_c)
            cv2.rectangle(processed_frame,(x,y),(x+w,y+h),color_code,2)
        self._draw_text(processed_frame, color, (processed_frame.shape[1]-100,50), color_code)

        return servo_code, processed_frame, color

class ShapeClassifier(BaseClassifier):
    """Classifier for detecting objects based on their shape."""
    def classify(self, frame: np.ndarray) -> tuple[ServoCode, np.ndarray, str]:
        processed_frame = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, mask = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)

        if mask is None or mask.size == 0:
            return ServoCode.UNKNOWN, processed_frame, "Unknown"

        mask = cv2.medianBlur(mask, 7)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return ServoCode.UNKNOWN, processed_frame, "Unknown"

        contour = sorted(contours, key=cv2.contourArea, reverse=True)[0]

        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * peri, True)

        shape = "Unknown"
        servo_code = ServoCode.UNKNOWN

        if len(approx) == 3:
            shape = "Triangle"
            servo_code = ServoCode.TRIANGLE
        elif len(approx) == 4:
            shape = "Square"
            servo_code = ServoCode.SQUARE
        elif len(approx) > 4:
            area = cv2.contourArea(contour)
            (x, y), radius = cv2.minEnclosingCircle(contour)
            circle_area = np.pi * (radius ** 2)
            circle_ratio = area / circle_area

            if 0.7 <= circle_ratio <= 1.3:
                shape = "Circle"
                servo_code = ServoCode.CIRCLE

        if shape == "Triangle":
            cv2.drawContours(processed_frame, [approx], -1, (0, 255, 0), 2)
        elif shape == "Square":
            rotated_rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rotated_rect)
            box = np.int32(box)
            cv2.drawContours(processed_frame, [box], 0, (0, 255, 0), 2)
        elif shape == "Circle":
            (x, y), radius = cv2.minEnclosingCircle(approx)
            center = (int(x), int(y))
            radius = int(radius)
            cv2.circle(processed_frame, center, radius, (0, 255, 0), 2)

        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            self._draw_text(processed_frame, shape, (cX, cY), (255, 255, 255))

        return servo_code, processed_frame, shape

class SizeClassifier(BaseClassifier):
    """Classifier for detecting objects based on their size."""
    def __init__(self, config: AppConfig):
        super().__init__(config)
        self.pixels_per_cm = None

    def calibrate(self, frame: np.ndarray, known_diameter_cm: float) -> float:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 100)

        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            c = max(contours, key=cv2.contourArea)
            if cv2.contourArea(c) > self.config.SHAPE_AREA_THRESHOLD:
                (_, _, w, _) = cv2.boundingRect(c)
                if w > 0:
                    self.pixels_per_cm = w / known_diameter_cm
                    return self.pixels_per_cm
        return None

    def classify(self, frame: np.ndarray) -> tuple[ServoCode, np.ndarray, str]:
        processed_frame = frame.copy()
        size_text = "Unknown"
        servo_code = ServoCode.UNKNOWN

        if self.pixels_per_cm is None:
            self._draw_text(processed_frame, "Calibrate first!", (50, 50), (0, 0, 255))
            return servo_code, processed_frame, "Needs Calibration"

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 100)

        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            c = max(contours, key=cv2.contourArea)
            if cv2.contourArea(c) > self.config.SHAPE_AREA_THRESHOLD:
                M = cv2.moments(c)
                cX, cY = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])) if M["m00"] != 0 else (0, 0)

                (x, y, w, h) = cv2.boundingRect(c)

                diameter = w / self.pixels_per_cm
                if diameter >= self.config.LARGE_SIZE_THRESHOLD_CM:
                    size_text = f"Large ({diameter:.1f} cm)"
                    servo_code = ServoCode.LARGE
                elif diameter >= self.config.MEDIUM_SIZE_THRESHOLD_CM:
                    size_text = f"Medium ({diameter:.1f} cm)"
                    servo_code = ServoCode.MEDIUM
                else:
                    size_text = f"Small ({diameter:.1f} cm)"
                    servo_code = ServoCode.SMALL

                self._draw_text(processed_frame, size_text, (cX - 20, cY - 20), (255, 255, 255))

        return servo_code, processed_frame, size_text