import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import cv2
from src.vision.classifiers import ColorClassifier, ShapeClassifier, SizeClassifier, ServoCode
from src.config.config import AppConfig

class TestColorClassifier(unittest.TestCase):

    def setUp(self):
        self.config = AppConfig()
        self.classifier = ColorClassifier(self.config)
        # Create a dummy frame for testing
        self.dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)

    @patch('cv2.cvtColor')
    @patch('cv2.inRange')
    @patch('cv2.morphologyEx')
    @patch('cv2.countNonZero')
    @patch('cv2.bitwise_or')
    @patch('cv2.findContours')
    @patch('cv2.contourArea')
    @patch('cv2.boundingRect')
    @patch('cv2.rectangle')
    @patch('cv2.putText')
    def test_classify_red(self, mock_putText, mock_rectangle, mock_boundingRect, mock_contourArea, mock_findContours, mock_bitwise_or, mock_countNonZero, mock_morphologyEx, mock_inRange, mock_cvtColor):
        # Mock return values to simulate red detection
        mock_cvtColor.return_value = self.dummy_frame # HSV frame
        mock_inRange.side_effect = [MagicMock(), MagicMock(), MagicMock()] # Red, Yellow, Green masks
        mock_morphologyEx.side_effect = [MagicMock(), MagicMock(), MagicMock(), MagicMock()] # Open ops
        mock_countNonZero.side_effect = [1000, 100, 50] # Red > Yellow, Green
        mock_bitwise_or.side_effect = [MagicMock(), MagicMock()] # Combined masks
        mock_findContours.return_value = ([MagicMock()], MagicMock()) # Contours
        mock_contourArea.return_value = 300 # Area above threshold
        mock_boundingRect.return_value = (10, 10, 50, 50) # Bounding box

        servo_code, processed_frame = self.classifier.classify(self.dummy_frame)

        self.assertEqual(servo_code, ServoCode.RED)
        mock_putText.assert_called_once()
        mock_rectangle.assert_called_once()

    @patch('cv2.cvtColor')
    @patch('cv2.inRange')
    @patch('cv2.morphologyEx')
    @patch('cv2.countNonZero')
    @patch('cv2.bitwise_or')
    @patch('cv2.findContours')
    @patch('cv2.contourArea')
    @patch('cv2.boundingRect')
    @patch('cv2.rectangle')
    @patch('cv2.putText')
    def test_classify_yellow(self, mock_putText, mock_rectangle, mock_boundingRect, mock_contourArea, mock_findContours, mock_bitwise_or, mock_countNonZero, mock_morphologyEx, mock_inRange, mock_cvtColor):
        # Mock return values to simulate yellow detection
        mock_cvtColor.return_value = self.dummy_frame
        mock_inRange.side_effect = [MagicMock(), MagicMock(), MagicMock()]
        mock_morphologyEx.side_effect = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_countNonZero.side_effect = [100, 1000, 50] # Yellow > Red, Green
        mock_bitwise_or.side_effect = [MagicMock(), MagicMock()]
        mock_findContours.return_value = ([MagicMock()], MagicMock())
        mock_contourArea.return_value = 300
        mock_boundingRect.return_value = (10, 10, 50, 50)

        servo_code, processed_frame = self.classifier.classify(self.dummy_frame)

        self.assertEqual(servo_code, ServoCode.YELLOW)
        mock_putText.assert_called_once()
        mock_rectangle.assert_called_once()

    @patch('cv2.cvtColor')
    @patch('cv2.inRange')
    @patch('cv2.morphologyEx')
    @patch('cv2.countNonZero')
    @patch('cv2.bitwise_or')
    @patch('cv2.findContours')
    @patch('cv2.contourArea')
    @patch('cv2.boundingRect')
    @patch('cv2.rectangle')
    @patch('cv2.putText')
    def test_classify_green(self, mock_putText, mock_rectangle, mock_boundingRect, mock_contourArea, mock_findContours, mock_bitwise_or, mock_countNonZero, mock_morphologyEx, mock_inRange, mock_cvtColor):
        # Mock return values to simulate green detection
        mock_cvtColor.return_value = self.dummy_frame
        mock_inRange.side_effect = [MagicMock(), MagicMock(), MagicMock()]
        mock_morphologyEx.side_effect = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_countNonZero.side_effect = [50, 100, 1000] # Green > Red, Yellow
        mock_bitwise_or.side_effect = [MagicMock(), MagicMock()]
        mock_findContours.return_value = ([MagicMock()], MagicMock())
        mock_contourArea.return_value = 300
        mock_boundingRect.return_value = (10, 10, 50, 50)

        servo_code, processed_frame = self.classifier.classify(self.dummy_frame)

        self.assertEqual(servo_code, ServoCode.GREEN)
        mock_putText.assert_called_once()
        mock_rectangle.assert_called_once()

    @patch('cv2.cvtColor')
    @patch('cv2.inRange')
    @patch('cv2.morphologyEx')
    @patch('cv2.countNonZero')
    @patch('cv2.bitwise_or')
    @patch('cv2.findContours')
    @patch('cv2.contourArea')
    @patch('cv2.boundingRect')
    @patch('cv2.rectangle')
    @patch('cv2.putText')
    def test_classify_unknown_color(self, mock_putText, mock_rectangle, mock_boundingRect, mock_contourArea, mock_findContours, mock_bitwise_or, mock_countNonZero, mock_morphologyEx, mock_inRange, mock_cvtColor):
        # Mock return values to simulate no dominant color
        mock_cvtColor.return_value = self.dummy_frame
        mock_inRange.side_effect = [MagicMock(), MagicMock(), MagicMock()]
        mock_morphologyEx.side_effect = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_countNonZero.side_effect = [0, 0, 0] # No color detected
        mock_bitwise_or.side_effect = [MagicMock(), MagicMock()]
        mock_findContours.return_value = ([MagicMock()], MagicMock())
        mock_contourArea.return_value = 0 # No significant contour
        mock_boundingRect.return_value = (0, 0, 0, 0)

        servo_code, processed_frame = self.classifier.classify(self.dummy_frame)

        self.assertEqual(servo_code, ServoCode.UNKNOWN)
        mock_putText.assert_called_once()
        mock_rectangle.assert_not_called()

class TestShapeClassifier(unittest.TestCase):

    def setUp(self):
        self.config = AppConfig()
        self.classifier = ShapeClassifier(self.config)
        self.dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)

    @patch('cv2.cvtColor')
    @patch('cv2.GaussianBlur')
    @patch('cv2.threshold')
    @patch('cv2.medianBlur')
    @patch('cv2.findContours')
    @patch('cv2.arcLength')
    @patch('cv2.approxPolyDP')
    @patch('cv2.contourArea')
    @patch('cv2.minEnclosingCircle')
    @patch('cv2.drawContours')
    @patch('cv2.putText')
    @patch('cv2.minAreaRect')
    @patch('cv2.boxPoints')
    @patch('cv2.circle')
    @patch('cv2.moments') # Mock cv2.moments
    def test_classify_triangle(self, mock_moments, mock_circle, mock_boxPoints, mock_minAreaRect, mock_putText, mock_drawContours, mock_minEnclosingCircle, mock_contourArea, mock_approxPolyDP, mock_arcLength, mock_findContours, mock_medianBlur, mock_threshold, mock_GaussianBlur, mock_cvtColor):
        mock_cvtColor.return_value = self.dummy_frame
        mock_GaussianBlur.return_value = self.dummy_frame
        mock_threshold.return_value = (None, MagicMock())
        mock_medianBlur.return_value = MagicMock()
        # Ensure findContours returns a list of actual numpy arrays for contours
        mock_findContours.return_value = ([np.array([[[0,0]],[[0,50]],[[50,0]]])], MagicMock())
        mock_arcLength.return_value = 100
        mock_approxPolyDP.return_value = np.array([[[0,0]],[[0,50]],[[50,0]]]) # 3 vertices for triangle
        mock_contourArea.return_value = 1000
        mock_moments.return_value = {"m00": 1, "m10": 50, "m01": 50} # Mock moments

        servo_code, processed_frame = self.classifier.classify(self.dummy_frame)

        self.assertEqual(servo_code, ServoCode.TRIANGLE)
        mock_drawContours.assert_called_once()
        mock_putText.assert_called_once()

    @patch('cv2.cvtColor')
    @patch('cv2.GaussianBlur')
    @patch('cv2.threshold')
    @patch('cv2.medianBlur')
    @patch('cv2.findContours')
    @patch('cv2.arcLength')
    @patch('cv2.approxPolyDP')
    @patch('cv2.contourArea')
    @patch('cv2.minEnclosingCircle')
    @patch('cv2.drawContours')
    @patch('cv2.putText')
    @patch('cv2.minAreaRect')
    @patch('cv2.boxPoints')
    @patch('cv2.circle')
    @patch('cv2.moments') # Mock cv2.moments
    def test_classify_square(self, mock_moments, mock_circle, mock_boxPoints, mock_minAreaRect, mock_putText, mock_drawContours, mock_minEnclosingCircle, mock_contourArea, mock_approxPolyDP, mock_arcLength, mock_findContours, mock_medianBlur, mock_threshold, mock_GaussianBlur, mock_cvtColor):
        mock_cvtColor.return_value = self.dummy_frame
        mock_GaussianBlur.return_value = self.dummy_frame
        mock_threshold.return_value = (None, MagicMock())
        mock_medianBlur.return_value = MagicMock()
        # Ensure findContours returns a list of actual numpy arrays for contours
        mock_findContours.return_value = ([np.array([[[0,0]],[[0,50]],[[50,50]],[[50,0]]])], MagicMock())
        mock_arcLength.return_value = 100
        mock_approxPolyDP.return_value = np.array([[[0,0]],[[0,50]],[[50,50]],[[50,0]]]) # 4 vertices for square
        mock_contourArea.return_value = 1000
        mock_minAreaRect.return_value = ((25,25),(50,50),0)
        mock_boxPoints.return_value = np.array([[[0,0]],[[0,50]],[[50,50]],[[50,0]]])
        mock_moments.return_value = {"m00": 1, "m10": 50, "m01": 50} # Mock moments

        servo_code, processed_frame = self.classifier.classify(self.dummy_frame)

        self.assertEqual(servo_code, ServoCode.SQUARE)
        mock_drawContours.assert_called_once()
        mock_putText.assert_called_once()

    @patch('cv2.cvtColor')
    @patch('cv2.GaussianBlur')
    @patch('cv2.threshold')
    @patch('cv2.medianBlur')
    @patch('cv2.findContours')
    @patch('cv2.arcLength')
    @patch('cv2.approxPolyDP')
    @patch('cv2.contourArea')
    @patch('cv2.minEnclosingCircle')
    @patch('cv2.drawContours')
    @patch('cv2.putText')
    @patch('cv2.minAreaRect')
    @patch('cv2.boxPoints')
    @patch('cv2.circle')
    @patch('cv2.moments') # Mock cv2.moments
    def test_classify_circle(self, mock_moments, mock_circle, mock_boxPoints, mock_minAreaRect, mock_putText, mock_drawContours, mock_minEnclosingCircle, mock_contourArea, mock_approxPolyDP, mock_arcLength, mock_findContours, mock_medianBlur, mock_threshold, mock_GaussianBlur, mock_cvtColor):
        mock_cvtColor.return_value = self.dummy_frame
        mock_GaussianBlur.return_value = self.dummy_frame
        mock_threshold.return_value = (None, MagicMock())
        mock_medianBlur.return_value = MagicMock()
        # Ensure findContours returns a list of actual numpy arrays for contours
        mock_findContours.return_value = ([np.array([[[0,0]]]*10)], MagicMock())
        mock_arcLength.return_value = 100
        mock_approxPolyDP.return_value = np.array([[[0,0]]]*10) # > 4 vertices
        mock_contourArea.return_value = 1000
        mock_minEnclosingCircle.return_value = ((50,50), 20) # Center, radius
        mock_moments.return_value = {"m00": 1, "m10": 50, "m01": 50} # Mock moments

        servo_code, processed_frame = self.classifier.classify(self.dummy_frame)

        self.assertEqual(servo_code, ServoCode.CIRCLE)
        mock_circle.assert_called_once()
        mock_putText.assert_called_once()

class TestSizeClassifier(unittest.TestCase):

    def setUp(self):
        self.config = AppConfig()
        self.classifier = SizeClassifier(self.config)
        self.dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)

    @patch('cv2.cvtColor')
    @patch('cv2.GaussianBlur')
    @patch('cv2.Canny')
    @patch('cv2.findContours')
    @patch('cv2.contourArea')
    @patch('cv2.arcLength')
    @patch('cv2.approxPolyDP')
    @patch('cv2.minEnclosingCircle')
    @patch('cv2.boundingRect')
    def test_calibrate_success(self, mock_boundingRect, mock_minEnclosingCircle, mock_approxPolyDP, mock_arcLength, mock_contourArea, mock_findContours, mock_Canny, mock_GaussianBlur, mock_cvtColor):
        mock_cvtColor.return_value = self.dummy_frame
        mock_GaussianBlur.return_value = self.dummy_frame
        mock_Canny.return_value = self.dummy_frame
        # Ensure findContours returns a list of actual numpy arrays for contours
        mock_findContours.return_value = ([np.array([[[0,0]]]*10)], MagicMock())
        mock_contourArea.return_value = 1000 # Adjusted to make circle_ratio valid
        mock_arcLength.return_value = 100
        mock_approxPolyDP.return_value = np.array([[[0,0]]]*10) # Simulate circle
        mock_minEnclosingCircle.return_value = ((50,50), 20) # Center, radius
        mock_boundingRect.return_value = (0, 0, 40, 40) # w = 40 pixels

        known_diameter_cm = 4.0
        pixels_per_cm = self.classifier.calibrate(self.dummy_frame, known_diameter_cm)

        self.assertIsNotNone(pixels_per_cm)
        self.assertAlmostEqual(pixels_per_cm, 40 / 4.0) # 10 pixels/cm
        self.assertTrue(self.classifier.pixels_per_cm is not None)

    @patch('cv2.cvtColor')
    @patch('cv2.GaussianBlur')
    @patch('cv2.Canny')
    @patch('cv2.findContours')
    @patch('cv2.contourArea')
    @patch('cv2.arcLength')
    @patch('cv2.approxPolyDP')
    @patch('cv2.minEnclosingCircle')
    @patch('cv2.boundingRect')
    @patch('cv2.putText')
    @patch('cv2.moments')
    def test_classify_large_circle(self, mock_moments, mock_putText, mock_boundingRect, mock_minEnclosingCircle, mock_approxPolyDP, mock_arcLength, mock_contourArea, mock_findContours, mock_Canny, mock_GaussianBlur, mock_cvtColor):
        self.classifier.pixels_per_cm = 10.0 # Calibrated

        mock_cvtColor.return_value = self.dummy_frame
        mock_GaussianBlur.return_value = self.dummy_frame
        mock_Canny.return_value = self.dummy_frame
        # Ensure findContours returns a list of actual numpy arrays for contours
        mock_findContours.return_value = ([np.array([[[0,0]]]*10)], MagicMock())
        mock_contourArea.return_value = 1000 # Adjusted to make circle_ratio valid
        mock_arcLength.return_value = 100
        mock_approxPolyDP.return_value = np.array([[[0,0]]]*10) # Simulate circle
        mock_minEnclosingCircle.return_value = ((50,50), 30) # Center, radius
        mock_boundingRect.return_value = (0, 0, 60, 60) # w = 60 pixels (6cm)
        mock_moments.return_value = {"m00": 1, "m10": 50, "m01": 50}

        servo_code, processed_frame = self.classifier.classify(self.dummy_frame)

        self.assertEqual(servo_code, ServoCode.LARGE)
        mock_putText.assert_called_once()

    @patch('cv2.cvtColor')
    @patch('cv2.GaussianBlur')
    @patch('cv2.Canny')
    @patch('cv2.findContours')
    @patch('cv2.contourArea')
    @patch('cv2.arcLength')
    @patch('cv2.approxPolyDP')
    @patch('cv2.minEnclosingCircle')
    @patch('cv2.boundingRect')
    @patch('cv2.putText')
    @patch('cv2.moments')
    def test_classify_medium_square(self, mock_moments, mock_putText, mock_boundingRect, mock_minEnclosingCircle, mock_approxPolyDP, mock_arcLength, mock_contourArea, mock_findContours, mock_Canny, mock_GaussianBlur, mock_cvtColor):
        self.classifier.pixels_per_cm = 10.0 # Calibrated

        mock_cvtColor.return_value = self.dummy_frame
        mock_GaussianBlur.return_value = self.dummy_frame
        mock_Canny.return_value = self.dummy_frame
        # Ensure findContours returns a list of actual numpy arrays for contours
        mock_findContours.return_value = ([np.array([[[0,0]],[[0,40]],[[40,40]],[[40,0]]])], MagicMock())
        mock_contourArea.return_value = 1000 # Adjusted to make circle_ratio valid
        mock_arcLength.return_value = 100
        mock_approxPolyDP.return_value = np.array([[[0,0]],[[0,40]],[[40,40]],[[40,0]]]) # Simulate square
        mock_minEnclosingCircle.return_value = ((50,50), 20) # Not used for square size
        mock_boundingRect.return_value = (0, 0, 40, 40) # w = 40 pixels (4cm), h = 40 pixels (4cm)
        mock_moments.return_value = {"m00": 1, "m10": 50, "m01": 50}

        servo_code, processed_frame = self.classifier.classify(self.dummy_frame)

        self.assertEqual(servo_code, ServoCode.MEDIUM)
        mock_putText.assert_called_once()

    @patch('cv2.cvtColor')
    @patch('cv2.GaussianBlur')
    @patch('cv2.Canny')
    @patch('cv2.findContours')
    @patch('cv2.contourArea')
    @patch('cv2.arcLength')
    @patch('cv2.approxPolyDP')
    @patch('cv2.minEnclosingCircle')
    @patch('cv2.boundingRect')
    @patch('cv2.putText')
    @patch('cv2.moments')
    def test_classify_small_triangle(self, mock_moments, mock_putText, mock_boundingRect, mock_minEnclosingCircle, mock_approxPolyDP, mock_arcLength, mock_contourArea, mock_findContours, mock_Canny, mock_GaussianBlur, mock_cvtColor):
        self.classifier.pixels_per_cm = 10.0 # Calibrated

        mock_cvtColor.return_value = self.dummy_frame
        mock_GaussianBlur.return_value = self.dummy_frame
        mock_Canny.return_value = self.dummy_frame
        # Ensure findContours returns a list of actual numpy arrays for contours
        mock_findContours.return_value = ([np.array([[[0,0]],[[0,20]],[[20,0]]])], MagicMock())
        mock_contourArea.return_value = 1000 # Adjusted to make circle_ratio valid
        mock_arcLength.return_value = 100
        mock_approxPolyDP.return_value = np.array([[[0,0]],[[0,20]],[[20,0]]]) # Simulate triangle
        mock_minEnclosingCircle.return_value = ((50,50), 10) # Not used for triangle size
        mock_boundingRect.return_value = (0, 0, 20, 20) # w = 20 pixels (2cm)
        mock_moments.return_value = {"m00": 1, "m10": 50, "m01": 50}

        servo_code, processed_frame = self.classifier.classify(self.dummy_frame)

        self.assertEqual(servo_code, ServoCode.SMALL)
        mock_putText.assert_called_once()

    @patch('cv2.putText')
    def test_classify_not_calibrated(self, mock_putText):
        # Ensure pixels_per_cm is None
        self.classifier.pixels_per_cm = None

        servo_code, processed_frame = self.classifier.classify(self.dummy_frame)

        self.assertEqual(servo_code, ServoCode.UNKNOWN)
        mock_putText.assert_called_once_with(processed_frame, "Calibrate first!", (50, 50), self.config.OPENCV_FONT, 1, (0, 0, 255), 2, cv2.LINE_AA)

if __name__ == '__main__':
    unittest.main()