import unittest
import cv2
import numpy as np
from unittest.mock import patch, MagicMock
from src.hardware.camera import Camera
from src.config.config import AppConfig

class TestCamera(unittest.TestCase):

    @patch('cv2.VideoCapture')
    def test_initialize_success(self, mock_video_capture):
        # Mock the VideoCapture object and its methods
        mock_cap_instance = MagicMock()
        mock_video_capture.return_value = mock_cap_instance
        mock_cap_instance.isOpened.return_value = True

        camera = Camera(camera_index=0, resolution=(640, 480))
        camera.initialize()

        mock_video_capture.assert_called_once_with(0)
        mock_cap_instance.isOpened.assert_called_once()
        mock_cap_instance.set.assert_any_call(cv2.CAP_PROP_FRAME_WIDTH, 640)
        mock_cap_instance.set.assert_any_call(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.assertIsNotNone(camera.cap)

    @patch('cv2.VideoCapture')
    def test_initialize_failure(self, mock_video_capture):
        mock_cap_instance = MagicMock()
        mock_video_capture.return_value = mock_cap_instance
        mock_cap_instance.isOpened.return_value = False

        camera = Camera(camera_index=99, resolution=(640, 480))
        with self.assertRaises(IOError) as cm:
            camera.initialize()
        self.assertIn("Cannot open webcam", str(cm.exception))

    @patch('cv2.VideoCapture')
    def test_read_frame_success(self, mock_video_capture):
        mock_cap_instance = MagicMock()
        mock_video_capture.return_value = mock_cap_instance
        mock_cap_instance.isOpened.return_value = True
        mock_cap_instance.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))

        camera = Camera(camera_index=0, resolution=(640, 480))
        camera.initialize()
        frame = camera.read_frame()

        mock_cap_instance.read.assert_called_once()
        self.assertIsNotNone(frame)
        self.assertTrue(isinstance(frame, np.ndarray))

    @patch('cv2.VideoCapture')
    def test_read_frame_failure(self, mock_video_capture):
        mock_cap_instance = MagicMock()
        mock_video_capture.return_value = mock_cap_instance
        mock_cap_instance.isOpened.return_value = True
        mock_cap_instance.read.return_value = (False, None)

        camera = Camera(camera_index=0, resolution=(640, 480))
        camera.initialize()
        frame = camera.read_frame()

        mock_cap_instance.read.assert_called_once()
        self.assertIsNone(frame)

    @patch('cv2.VideoCapture')
    def test_release(self, mock_video_capture):
        mock_cap_instance = MagicMock()
        mock_video_capture.return_value = mock_cap_instance
        mock_cap_instance.isOpened.return_value = True

        camera = Camera(camera_index=0, resolution=(640, 480))
        camera.initialize()
        camera.release()

        mock_cap_instance.release.assert_called_once()
        self.assertIsNone(camera.cap)

    def test_read_frame_not_initialized(self):
        camera = Camera(camera_index=0, resolution=(640, 480))
        with self.assertRaises(IOError) as cm:
            camera.read_frame()
        self.assertIn("Camera not initialized", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
