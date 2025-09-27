import time
from collections import deque, Counter
from threading import Thread, Event

from src.config.config import AppConfig
from src.hardware.camera import Camera
from src.hardware.serial_manager import SerialManager
from src.vision.image_processor import ImageProcessor
from src.vision.classifiers import BaseClassifier, ServoCode, ColorClassifier, ShapeClassifier, SizeClassifier

class ApplicationController:
    """
    The main controller for the BandaCV application.

    This class orchestrates the entire application flow, connecting the hardware
    (camera, serial manager), vision processing modules, and the user interface.
    It manages the application state, handles user input, and runs the main
    processing loop.

    Args:
        config (AppConfig): The application configuration object.
    """
    def __init__(self, config: AppConfig):
        self.config = config
        self.camera = Camera(config.WEBCAM_INDEX, config.CAMERA_RESOLUTION)
        self.serial_manager = SerialManager(config.BAUDRATE)
        self.image_processor = ImageProcessor(config)

        self.classifiers = {
            "color": ColorClassifier(config),
            "shape": ShapeClassifier(config),
            "size": SizeClassifier(config)
        }
        self.active_classifier_key = None
        self.active_classifier: BaseClassifier = None

        self.data_deque = deque(maxlen=self.config.MAX_SAMPLES)
        self.stop_event = Event()
        self.serial_read_thread = None

        self.pwm_value = 0
        self.current_servo_code = ServoCode.UNKNOWN
        self.pixels_per_cm = None
        self.calibrated = False

        self.obstacle_detected = False
        self.detection_start_time = None
        self.servo_codes_buffer = Counter() # To store servo codes during detection window

        # Callbacks for UI updates (to be set by the GUI)
        self.on_frame_update = None
        self.on_graph_update = None
        self.on_led_update = None
        self.on_calibration_update = None
        self.on_status_message = None

    def register_ui_callbacks(self, on_frame_update, on_graph_update, on_led_update, on_calibration_update, on_status_message):
        """Registers UI callback functions for updating the GUI.

        This allows the controller to be decoupled from the GUI implementation.

        Args:
            on_frame_update (callable): Callback for updating the video frame.
            on_graph_update (callable): Callback for updating the RPM graph.
            on_led_update (callable): Callback for updating the obstacle LED.
            on_calibration_update (callable): Callback for updating calibration status.
            on_status_message (callable): Callback for displaying status messages.
        """
        self.on_frame_update = on_frame_update
        self.on_graph_update = on_graph_update
        self.on_led_update = on_led_update
        self.on_calibration_update = on_calibration_update
        self.on_status_message = on_status_message

    def _read_serial_data_loop(self):
        """Continuously reads data from the serial port in a separate thread.

        This method runs in a background thread to avoid blocking the main
        application. It reads RPM and obstacle sensor data from the Arduino,
        updates the data deque, and triggers UI callbacks for the graph and LED.
        """
        self.serial_manager.connect()
        start_time_read = time.time()
        while not self.stop_event.is_set():
            data = self.serial_manager.read_data()
            if data is not None:
                rpm_value, obstacle_sensor_state_value = data
                current_time = time.time() - start_time_read
                self.data_deque.append((current_time, rpm_value, obstacle_sensor_state_value))

                # Update UI via callback
                if self.on_graph_update:
                    time_values = [d[0] for d in self.data_deque]
                    rpm_values = [d[1] for d in self.data_deque]
                    self.on_graph_update(time_values, rpm_values)
                if self.on_led_update:
                    self.on_led_update(obstacle_sensor_state_value)
            time.sleep(0.01) # Small delay to prevent busy-waiting

    def start(self):
        """Initializes and starts the application's components.

        This method initializes the camera, starts the serial data reading
        thread, and sends a status message to the UI.
        """
        self.camera.initialize()
        self.serial_read_thread = Thread(target=self._read_serial_data_loop)
        self.serial_read_thread.start()
        if self.on_status_message:
            self.on_status_message("Application started. Waiting for serial connection...")

    def stop(self):
        """Stops the application, cleans up resources, and joins threads.

        This method sets the stop event to terminate background threads,
        joins the serial reading thread, disconnects the serial port, and
        releases the camera.
        """
        self.stop_event.set()
        if self.serial_read_thread and self.serial_read_thread.is_alive():
            self.serial_read_thread.join() # Wait for thread to finish
        self.serial_manager.disconnect()
        self.camera.release()
        if self.on_status_message:
            self.on_status_message("Application stopped.")

    def set_pwm(self, value: int):
        """Sets the PWM value for the conveyor belt motor.

        Args:
            value (int): The PWM value (0-255) to send to the Arduino.
        """
        self.pwm_value = value
        self.serial_manager.send_command(self.pwm_value, self.current_servo_code)

    def set_active_classifier(self, classifier_key: str) -> bool:
        """Sets the active object classifier.

        Args:
            classifier_key (str): The key of the classifier to activate
                                  ('color', 'shape', or 'size').

        Returns:
            bool: True if the classifier was set successfully, False otherwise.
        """
        """Sets the active classification mode (color, shape, size)."""
        if classifier_key in self.classifiers:
            if classifier_key == "size" and not self.calibrated:
                if self.on_status_message:
                    self.on_status_message("Please calibrate the camera before using size detection.")
                return False
            self.active_classifier_key = classifier_key
            self.active_classifier = self.classifiers[classifier_key]
            if self.on_status_message:
                self.on_status_message(f"Classifier set to: {classifier_key}")
            return True
        else:
            if self.on_status_message:
                self.on_status_message(f"Unknown classifier: {classifier_key}")
            return False

    def calibrate_camera(self):
        """Calibrates the camera for size detection.

        This method uses the size classifier to determine the pixels-per-centimeter
        ratio based on a calibration object of a known size. The result is stored
        in the `pixels_per_cm` attribute.
        """
        frame = self.camera.read_frame()
        if frame is None:
            if self.on_status_message:
                self.on_status_message("Cannot calibrate: No frame from camera.")
            return

        size_classifier: SizeClassifier = self.classifiers["size"]
        pixels_per_cm = size_classifier.calibrate(frame, self.config.CALIBRATION_CIRCLE_DIAMETER_CM)

        if pixels_per_cm is not None:
            self.pixels_per_cm = pixels_per_cm
            self.calibrated = True
            if self.on_calibration_update:
                self.on_calibration_update(pixels_per_cm)
            if self.on_status_message:
                self.on_status_message(f"Camera calibrated: {pixels_per_cm:.2f} px/cm")
        else:
            self.calibrated = False
            if self.on_status_message:
                self.on_status_message("Calibration failed. Ensure a circular object is in view.")

    def process_video_frame(self):
        """Processes a single video frame.

        This is the main processing loop for the application. It reads a frame
        from the camera, checks for obstacle detection, and if an obstacle is
        present, it uses the active classifier to process the frame and determine
        the object's classification. It also handles the logic for sending
        commands to the Arduino based on the classification results.
        """
        frame = self.camera.read_frame()
        if frame is None: # Handle case where camera might not be ready or disconnected
            return

        processed_frame = frame.copy()
        current_servo_code_for_frame = ServoCode.UNKNOWN

        # Check for obstacle detection state from serial data
        obstacle_sensor_state_value = 0
        if self.data_deque:
            _, _, obstacle_sensor_state_value = self.data_deque[-1]

        if obstacle_sensor_state_value == 1:
            if not self.obstacle_detected:
                self.obstacle_detected = True
                self.detection_start_time = time.time()
                self.servo_codes_buffer.clear()

            if self.active_classifier:
                current_servo_code_for_frame, processed_frame = self.image_processor.process_frame(frame, self.active_classifier)
                self.servo_codes_buffer[current_servo_code_for_frame] += 1

            if time.time() - self.detection_start_time >= self.config.DETECTION_PROCESSING_TIME_SECONDS:
                if self.servo_codes_buffer:
                    most_common_servo_code = self.servo_codes_buffer.most_common(1)[0][0]
                    self.current_servo_code = most_common_servo_code
                    self.serial_manager.send_command(self.pwm_value, self.current_servo_code)
                    if self.on_status_message:
                        self.on_status_message(f"Detected: {self.current_servo_code.name}")
                self.obstacle_detected = False
                self.detection_start_time = None
                self.servo_codes_buffer.clear()
        else:
            self.obstacle_detected = False
            self.detection_start_time = None
            self.servo_codes_buffer.clear()

        if self.on_frame_update:
            self.on_frame_update(processed_frame)

