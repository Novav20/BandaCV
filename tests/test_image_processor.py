import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import cv2
from src.vision.image_processor import ImageProcessor
from src.vision.classifiers import BaseClassifier, ServoCode
from src.config.config import AppConfig

class TestImageProcessor(unittest.TestCase):

    def setUp(self):
        self.config = AppConfig()
        self.image_processor = ImageProcessor(self.config)
        self.dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)

    def test_preprocess_frame(self):
        # Currently, preprocess_frame just returns the frame as is
        processed_frame = self.image_processor.preprocess_frame(self.dummy_frame)
        np.testing.assert_array_equal(processed_frame, self.dummy_frame)

    @patch.object(BaseClassifier, 'classify')
    def test_process_frame_with_classifier(self, mock_classify):
        mock_classifier = MagicMock(spec=BaseClassifier)
        mock_classify.return_value = (ServoCode.RED, self.dummy_frame)
        mock_classifier.classify = mock_classify

        servo_code, processed_frame = self.image_processor.process_frame(self.dummy_frame, mock_classifier)

        mock_classify.assert_called_once_with(self.dummy_frame)
        self.assertEqual(servo_code, ServoCode.RED)
        np.testing.assert_array_equal(processed_frame, self.dummy_frame)

    def test_process_frame_no_classifier(self):
        servo_code, processed_frame = self.image_processor.process_frame(self.dummy_frame, None)

        self.assertEqual(servo_code, ServoCode.UNKNOWN)
        np.testing.assert_array_equal(processed_frame, self.dummy_frame)

if __name__ == '__main__':
    unittest.main()
