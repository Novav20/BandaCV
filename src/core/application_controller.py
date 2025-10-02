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
        self.serial_manager = SerialManager(config.BAUDRATE, on_disconnect=self.handle_serial_disconnection)
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
        self.heartbeat_thread = None

        self.pwm_value = 0
        self.current_servo_code = ServoCode.UNKNOWN
        self.pixels_per_cm = None
        self.calibrated = False

        self.is_classification_active = False
        self.previous_ir_state = 0
        self.detection_start_time = None
        self.servo_codes_buffer = Counter()  # To store servo codes during detection window

        # Callbacks for UI updates (to be set by the GUI)
        self.on_frame_update = None
        self.on_graph_update = None
        self.on_led_update = None
        self.on_calibration_update = None
        self.on_status_message = None
        self.on_pwm_update = None

    def register_ui_callbacks(self, on_frame_update, on_graph_update, on_led_update, on_calibration_update, on_status_message, on_pwm_update):
        """Registers UI callback functions for updating the GUI.

        This allows the controller to be decoupled from the GUI implementation.

        Args:
            on_frame_update (callable): Callback for updating the video frame.
            on_graph_update (callable): Callback for updating the RPM graph.
            on_led_update (callable): Callback for updating the obstacle LED.
            on_calibration_update (callable): Callback for updating calibration status.
            on_status_message (callable): Callback for displaying status messages.
            on_pwm_update (callable): Callback for updating PWM widgets.
        """
        self.on_frame_update = on_frame_update
        self.on_graph_update = on_graph_update
        self.on_led_update = on_led_update
        self.on_calibration_update = on_calibration_update
        self.on_status_message = on_status_message
        self.on_pwm_update = on_pwm_update

    def handle_serial_disconnection(self):
        """Handles the event of a serial disconnection."""
        if self.on_status_message:
            self.on_status_message("Serial device disconnected. Attempting to reconnect...")
        # Best-effort attempt to send a safe-state command. This will likely fail.
        self.serial_manager.send_command(0, ServoCode.UNKNOWN)

    def _read_serial_data_loop(self):
        """Continuously reads data from the serial port and handles reconnection."""
        start_time_read = time.time()
        while not self.stop_event.is_set():
            if not self.serial_manager.connected:
                # Attempt to reconnect
                if self.serial_manager.connect():
                    if self.on_status_message:
                        self.on_status_message("Serial device reconnected.")
                    # On successful reconnect, reset state to safe values
                    self.pwm_value = 0
                    self.current_servo_code = ServoCode.UNKNOWN
                    if self.on_pwm_update:
                        self.on_pwm_update(self.pwm_value)
                else:
                    # Wait before retrying to avoid spamming connection attempts
                    time.sleep(1)
                    continue  # Skip the rest of the loop and retry connection

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
            else:
                # A small sleep even if no data, to prevent busy-waiting
                time.sleep(0.05)

    def start(self):
        """Initializes and starts the application's components."""
        self.camera.initialize()
        self.serial_read_thread = Thread(target=self._read_serial_data_loop)
        self.serial_read_thread.start()
        self.heartbeat_thread = Thread(target=self._send_heartbeat_loop)
        self.heartbeat_thread.start()
        if self.on_status_message:
            self.on_status_message("Application started. Waiting for serial connection...")

    def stop(self):
        """Stops the application, cleans up resources, and joins threads."""
        self.stop_event.set()

        # Stop the motor before closing the connection
        print("Sending stop command to motor...")
        self.serial_manager.send_command(0, ServoCode.UNKNOWN)
        time.sleep(0.1)  # Give a moment for the command to be sent

        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join()
        if self.serial_read_thread and self.serial_read_thread.is_alive():
            self.serial_read_thread.join()  # Wait for thread to finish
        
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
        """Processes a single video frame using a rising-edge trigger state machine."""
        if self.stop_event.is_set():
            return

        frame = self.camera.read_frame()
        if frame is None:
            return

        processed_frame = frame.copy()

        # 1. Get current IR sensor state
        current_ir_state = 0
        if self.data_deque:
            _, _, current_ir_state = self.data_deque[-1]

        # 2. State Machine Logic
        # State: IDLE (classification is not active)
        if not self.is_classification_active:
            # Check for a rising edge on the IR sensor
            if current_ir_state == 1 and self.previous_ir_state == 0:
                if not self.active_classifier:
                    if self.on_status_message:
                        self.on_status_message("Obstacle detected. Select a classifier to begin.")
                else:
                    # Rising edge detected and classifier is active, start classification
                    self.is_classification_active = True
                    self.detection_start_time = time.time()
                    self.servo_codes_buffer.clear()
                    if self.on_status_message:
                        self.on_status_message("IR Triggered! Classifying...")
        
        # State: CLASSIFYING (classification is active)
        else:
            # Classification is active, so process the frame regardless of IR state
            if self.active_classifier:
                _, processed_frame = self.image_processor.process_frame(frame, self.active_classifier)
                self.servo_codes_buffer[_.value] += 1 # Use the enum value for the counter key

            # Check if classification time has elapsed
            if time.time() - self.detection_start_time >= self.config.DETECTION_PROCESSING_TIME_SECONDS:
                if self.servo_codes_buffer:
                    # Determine most common classification
                    most_common_code_value = self.servo_codes_buffer.most_common(1)[0][0]
                    self.current_servo_code = ServoCode(most_common_code_value)
                    self.serial_manager.send_command(self.pwm_value, self.current_servo_code)
                    if self.on_status_message:
                        self.on_status_message(f"Classification complete: {self.current_servo_code.name}")
                
                # Return to IDLE state
                self.is_classification_active = False
                self.detection_start_time = None
                self.servo_codes_buffer.clear()

        # 3. Update previous IR state for next frame's rising-edge detection
        self.previous_ir_state = current_ir_state

        # 4. Update the UI with the (potentially processed) frame
        if self.on_frame_update:
            self.on_frame_update(processed_frame)

    def send_debug_servo_command(self, servo_code: ServoCode):
        """
        Sends a direct command to the servo for debugging purposes.
        This method now also updates the controller's current servo state.

        Args:
            servo_code (ServoCode): The servo code to send.
        """
        if self.on_status_message:
            self.on_status_message(f"Sending debug servo command: {servo_code.name}")
        
        # Update the internal state to make it persistent
        self.current_servo_code = servo_code
        
        # Use the current PWM value and the new servo code
        self.serial_manager.send_command(self.pwm_value, self.current_servo_code)

    def _send_heartbeat_loop(self):
        """Periodically sends the current state to the Arduino as a heartbeat."""
        while not self.stop_event.is_set():
            if self.serial_manager.connected:
                # Send the current PWM and servo code as a heartbeat
                self.serial_manager.send_command(self.pwm_value, self.current_servo_code)
            
            # Wait for 1 second before sending the next heartbeat
            time.sleep(1)

