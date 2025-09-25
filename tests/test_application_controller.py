import unittest
from unittest.mock import patch, MagicMock, call
import numpy as np
import time
from collections import deque
from threading import Event, Thread
import builtins

from src.core.application_controller import ApplicationController
from src.config.config import AppConfig
from src.hardware.camera import Camera
from src.hardware.serial_manager import SerialManager
from src.vision.image_processor import ImageProcessor
from src.vision.classifiers import ColorClassifier, ShapeClassifier, SizeClassifier, ServoCode

class TestApplicationController(unittest.TestCase):

    def setUp(self):
        self.mock_config = MagicMock(spec=AppConfig)
        self.mock_config.WEBCAM_INDEX = 0
        self.mock_config.CAMERA_RESOLUTION = (640, 480)
        self.mock_config.BAUDRATE = 9600
        self.mock_config.MAX_SAMPLES = 100
        self.mock_config.DETECTION_PROCESSING_TIME_SECONDS = 2
        self.mock_config.CALIBRATION_CIRCLE_DIAMETER_CM = 4.0
        self.mock_config.COLOR_AREA_THRESHOLD = 250
        self.mock_config.SHAPE_AREA_THRESHOLD = 150
        self.mock_config.RED_LOWER_HSV = (0, 120, 70)
        self.mock_config.RED_UPPER_HSV = (10, 255, 255)
        self.mock_config.YELLOW_LOWER_HSV = (20, 100, 100)
        self.mock_config.YELLOW_UPPER_HSV = (30, 255, 255)
        self.mock_config.GREEN_LOWER_HSV = (31, 16, 17)
        self.mock_config.GREEN_UPPER_HSV = (78, 255, 255)
        self.mock_config.MORPHOLOGY_KERNEL_SIZE = 5
        self.mock_config.OPENCV_FONT = 0 # cv2.FONT_HERSHEY_SIMPLEX
        self.mock_config.OPENCV_FONT_SCALE = 0.5
        self.mock_config.OPENCV_FONT_THICKNESS = 2
        self.mock_config.LARGE_SIZE_THRESHOLD_CM = 5.0
        self.mock_config.MEDIUM_SIZE_THRESHOLD_CM = 4.0
        self.mock_config.SMALL_SIZE_THRESHOLD_CM = 2.0
        self.mock_config.UI_UPDATE_INTERVAL_MS = 1

        self.patcher_print = patch.object(builtins, 'print')
        self.mock_print = self.patcher_print.start()

        self.patcher_camera = patch('src.core.application_controller.Camera')
        self.mock_camera_cls = self.patcher_camera.start()
        self.mock_camera_instance = MagicMock(spec=Camera)
        self.mock_camera_cls.return_value = self.mock_camera_instance

        self.patcher_serial = patch('src.core.application_controller.SerialManager')
        self.mock_serial_cls = self.patcher_serial.start()
        self.mock_serial_instance = MagicMock(spec=SerialManager)
        self.mock_serial_cls.return_value = self.mock_serial_instance
        self.mock_serial_instance.connect = MagicMock(return_value=True)
        self.mock_serial_instance.connected = True
        self.mock_serial_instance._get_arduino_port = MagicMock(return_value="/dev/ttyACM0")

        self.patcher_image_processor = patch('src.core.application_controller.ImageProcessor')
        self.mock_image_processor_cls = self.patcher_image_processor.start()
        self.mock_image_processor_instance = MagicMock(spec=ImageProcessor)
        self.mock_image_processor_cls.return_value = self.mock_image_processor_instance

        self.patcher_color_classifier_cls = patch('src.core.application_controller.ColorClassifier')
        self.mock_color_classifier_cls = self.patcher_color_classifier_cls.start()
        self.mock_color_classifier_instance = MagicMock(spec=ColorClassifier)
        self.mock_color_classifier_cls.return_value = self.mock_color_classifier_instance

        self.patcher_shape_classifier_cls = patch('src.core.application_controller.ShapeClassifier')
        self.mock_shape_classifier_cls = self.patcher_shape_classifier_cls.start()
        self.mock_shape_classifier_instance = MagicMock(spec=ShapeClassifier)
        self.mock_shape_classifier_cls.return_value = self.mock_shape_classifier_instance

        self.patcher_size_classifier_cls = patch('src.core.application_controller.SizeClassifier')
        self.mock_size_classifier_cls = self.patcher_size_classifier_cls.start()
        self.mock_size_classifier_instance = MagicMock(spec=SizeClassifier)
        self.mock_size_classifier_cls.return_value = self.mock_size_classifier_instance

        self.patcher_thread = patch('src.core.application_controller.Thread')
        self.mock_thread_cls = self.patcher_thread.start()
        self.mock_thread_instance = MagicMock(spec=Thread)
        self.mock_thread_cls.return_value = self.mock_thread_instance

        self.controller = ApplicationController(self.mock_config)
        
        self.mock_on_frame_update = MagicMock()
        self.mock_on_graph_update = MagicMock()
        self.mock_on_led_update = MagicMock()
        self.mock_on_calibration_update = MagicMock()
        self.mock_on_status_message = MagicMock()
        self.controller.register_ui_callbacks(
            self.mock_on_frame_update,
            self.mock_on_graph_update,
            self.mock_on_led_update,
            self.mock_on_calibration_update,
            self.mock_on_status_message
        )

    def tearDown(self):
        self.patcher_camera.stop()
        self.patcher_serial.stop()
        self.patcher_image_processor.stop()
        self.patcher_color_classifier_cls.stop()
        self.patcher_shape_classifier_cls.stop()
        self.patcher_size_classifier_cls.stop()
        self.patcher_thread.stop()
        self.patcher_print.stop()

    def test_init(self):
        self.mock_camera_cls.assert_called_once_with(self.mock_config.WEBCAM_INDEX, self.mock_config.CAMERA_RESOLUTION)
        self.mock_serial_cls.assert_called_once_with(self.mock_config.BAUDRATE)
        self.mock_image_processor_cls.assert_called_once_with(self.mock_config)
        self.mock_color_classifier_cls.assert_called_once_with(self.mock_config)
        self.mock_shape_classifier_cls.assert_called_once_with(self.mock_config)
        self.mock_size_classifier_cls.assert_called_once_with(self.mock_config)
        self.assertIsNone(self.controller.active_classifier_key)
        self.assertIsNone(self.controller.active_classifier)
        self.assertFalse(self.controller.calibrated)

    def test_start(self):
        self.controller.start()
        self.mock_camera_instance.initialize.assert_called_once()
        self.mock_thread_cls.assert_called_once_with(target=self.controller._read_serial_data_loop)
        self.mock_thread_instance.start.assert_called_once()
        self.mock_on_status_message.assert_called_once_with("Application started. Waiting for serial connection...")

    def test_stop(self):
        self.controller.serial_read_thread = self.mock_thread_instance
        self.controller.serial_read_thread.is_alive.return_value = True
        self.controller.stop_event = MagicMock(spec=Event)

        self.controller.stop()
        self.controller.stop_event.set.assert_called_once()
        self.controller.serial_read_thread.join.assert_called_once()
        self.mock_serial_instance.disconnect.assert_called_once()
        self.mock_camera_instance.release.assert_called_once()
        self.mock_on_status_message.assert_called_once_with("Application stopped.")

    def test_set_pwm(self):
        self.controller.set_pwm(150)
        self.assertEqual(self.controller.pwm_value, 150)
        self.mock_serial_instance.send_command.assert_called_once_with(150, ServoCode.UNKNOWN)

    def test_set_active_classifier_color(self):
        self.controller.set_active_classifier("color")
        self.assertEqual(self.controller.active_classifier_key, "color")
        self.assertEqual(self.controller.active_classifier, self.mock_color_classifier_instance)
        self.mock_on_status_message.assert_called_once_with("Classifier set to: color")

    def test_set_active_classifier_size_not_calibrated(self):
        self.controller.calibrated = False
        result = self.controller.set_active_classifier("size")
        self.assertFalse(result)
        self.assertIsNone(self.controller.active_classifier_key)
        self.mock_on_status_message.assert_called_once_with("Please calibrate the camera before using size detection.")

    def test_set_active_classifier_size_calibrated(self):
        self.controller.calibrated = True
        result = self.controller.set_active_classifier("size")
        self.assertTrue(result)
        self.assertEqual(self.controller.active_classifier_key, "size")
        self.assertEqual(self.controller.active_classifier, self.mock_size_classifier_instance)

    def test_calibrate_camera_success(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.mock_camera_instance.read_frame.return_value = frame
        self.mock_size_classifier_instance.calibrate.return_value = 10.5

        self.controller.calibrate_camera()

        self.mock_camera_instance.read_frame.assert_called_once()
        self.mock_size_classifier_instance.calibrate.assert_called_once_with(
            frame, self.mock_config.CALIBRATION_CIRCLE_DIAMETER_CM
        )
        self.assertTrue(self.controller.calibrated)
        self.assertEqual(self.controller.pixels_per_cm, 10.5)
        self.mock_on_calibration_update.assert_called_once_with(10.5)
        self.mock_on_status_message.assert_called_once_with("Camera calibrated: 10.50 px/cm")

    def test_calibrate_camera_failure(self):
        self.mock_camera_instance.read_frame.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
        self.mock_size_classifier_instance.calibrate.return_value = None

        self.controller.calibrate_camera()

        self.assertFalse(self.controller.calibrated)
        self.assertIsNone(self.controller.pixels_per_cm)
        self.mock_on_status_message.assert_called_once_with("Calibration failed. Ensure a circular object is in view.")

@patch("src.controllers.application_controller.cv2.VideoCapture")
@patch("src.controllers.application_controller.servo_classification")
@patch("src.controllers.application_controller.time.time", side_effect=[0, 1, 2.1])
def test_process_video_frame_obstacle_detection_and_classification(
    self, mock_time, mock_servo_classification, mock_video_capture
):
    mock_capture = MagicMock()
    mock_video_capture.return_value = mock_capture
    mock_capture.isOpened.return_value = True
    mock_capture.read.return_value = (True, MagicMock())
    mock_servo_classification.classify_frame.return_value = ServoCode.RED

    # Forzar el deque con obstáculo presente
    self.controller.data_deque.append((1, 105, 1))

    # Frame 1: empieza la detección
    self.controller.process_video_frame()
    self.assertIsNotNone(self.controller.detection_start_time)
    self.assertEqual(self.controller.servo_codes_buffer[ServoCode.RED], 1)

    # Frame 2: sigue en la ventana de detección (<2s), debe acumular más resultados
    self.controller.process_video_frame()
    self.assertGreaterEqual(self.controller.servo_codes_buffer[ServoCode.RED], 1)

    # Frame 3: pasa el tiempo de procesamiento (>=2s), debería enviar comando y resetear buffer
    self.controller.process_video_frame()
    mock_servo_classification.send_servo_command.assert_called_once()
    self.assertEqual(self.controller.servo_codes_buffer[ServoCode.RED], 0)
    self.assertIsNone(self.controller.detection_start_time)

    # Frame 4: no hay obstáculo, no debería enviar comando
    self.controller.process_video_frame()
    mock_servo_classification.send_servo_command.assert_called_once()

    @patch('time.time', side_effect=[0, 0.1, 0.2, 0.3, 0.4])
    @patch('time.sleep', return_value=None)
    def test_read_serial_data_loop(self, mock_sleep, mock_time):
        self.mock_serial_instance.read_data.side_effect = [(100, 1), (120, 0), None]
        self.controller.stop_event = MagicMock(spec=Event)
        self.controller.stop_event.is_set.side_effect = [False, False, False, True]

        self.controller._read_serial_data_loop()

        self.mock_serial_instance.connect.assert_called_once()
        
        expected_graph_calls = [call([0.1], [100]), call([0.1, 0.2], [100, 120])]
        self.assertEqual(self.mock_on_graph_update.call_args_list, expected_graph_calls)

        # FIX: Assert against call_args_list for the LED update mock as well
        expected_led_calls = [call(1), call(0)]
        self.assertEqual(self.mock_on_led_update.call_args_list, expected_led_calls)
        
        self.assertEqual(len(self.controller.data_deque), 2)
        self.assertEqual(self.controller.data_deque[0], (0.1, 100, 1))
        self.assertEqual(self.controller.data_deque[1], (0.2, 120, 0))
        self.mock_print.assert_not_called()

if __name__ == '__main__':
    unittest.main()