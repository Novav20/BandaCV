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
    """
    def __init__(self, config: AppConfig):
        self.config = config
        self.camera = Camera(config.WEBCAM_INDEX, config.CAMERA_RESOLUTION)
        self.serial_manager = SerialManager(config, on_disconnect=self.handle_serial_disconnection)
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
        # Buffer for the hardware command value (e.g., '0', '1')
        self.servo_codes_buffer = Counter()
        # Buffer for the display-friendly name (e.g., "Red", "Triangle")
        self.classification_name_buffer = Counter()

        # Callbacks for UI updates
        self.on_frame_update = None
        self.on_graph_update = None
        self.on_led_update = None
        self.on_calibration_update = None
        self.on_status_message = None
        self.on_pwm_update = None

    def register_ui_callbacks(self, on_frame_update, on_graph_update, on_led_update, on_calibration_update, on_status_message, on_pwm_update):
        self.on_frame_update = on_frame_update
        self.on_graph_update = on_graph_update
        self.on_led_update = on_led_update
        self.on_calibration_update = on_calibration_update
        self.on_status_message = on_status_message
        self.on_pwm_update = on_pwm_update

    def handle_serial_disconnection(self):
        if self.on_status_message:
            self.on_status_message("Serial device disconnected. Attempting to reconnect...")
        self.serial_manager.send_command(0, ServoCode.UNKNOWN)

    def _read_serial_data_loop(self):
        start_time_read = time.time()
        while not self.stop_event.is_set():
            if not self.serial_manager.connected:
                if self.serial_manager.connect():
                    if self.on_status_message:
                        self.on_status_message("Serial device reconnected.")
                    self.pwm_value = 0
                    self.current_servo_code = ServoCode.UNKNOWN
                    if self.on_pwm_update:
                        self.on_pwm_update(self.pwm_value)
                else:
                    time.sleep(self.config.SERIAL_RECONNECT_DELAY_SECONDS)
                    continue

            data = self.serial_manager.read_data()
            if data is not None:
                rpm_value, obstacle_sensor_state_value = data
                current_time = time.time() - start_time_read
                self.data_deque.append((current_time, rpm_value, obstacle_sensor_state_value))

                if self.on_graph_update:
                    time_values = [d[0] for d in self.data_deque]
                    rpm_values = [d[1] for d in self.data_deque]
                    self.on_graph_update(time_values, rpm_values)
                if self.on_led_update:
                    self.on_led_update(obstacle_sensor_state_value)
            else:
                time.sleep(self.config.SERIAL_READ_LOOP_SLEEP_SECONDS)

    def start(self):
        self.camera.initialize()
        self.serial_read_thread = Thread(target=self._read_serial_data_loop)
        self.serial_read_thread.start()
        self.heartbeat_thread = Thread(target=self._send_heartbeat_loop)
        self.heartbeat_thread.start()
        if self.on_status_message:
            self.on_status_message("Application started. Waiting for serial connection...")

    def stop(self):
        self.stop_event.set()
        print("Sending stop command to motor...")
        self.serial_manager.send_command(0, ServoCode.UNKNOWN)
        time.sleep(self.config.APP_SHUTDOWN_DELAY_SECONDS)

        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join()
        if self.serial_read_thread and self.serial_read_thread.is_alive():
            self.serial_read_thread.join()
        
        self.serial_manager.disconnect()
        self.camera.release()
        if self.on_status_message:
            self.on_status_message("Application stopped.")

    def set_pwm(self, value: int):
        self.pwm_value = value
        self.serial_manager.send_command(self.pwm_value, self.current_servo_code)

    def set_active_classifier(self, classifier_key: str) -> bool:
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
            self.active_classifier_key = None
            self.active_classifier = None
            if self.on_status_message:
                self.on_status_message("Classifier deactivated.")
            return False

    def calibrate_camera(self):
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
        if self.stop_event.is_set(): return
        frame = self.camera.read_frame()
        if frame is None: return

        processed_frame = frame.copy()
        current_ir_state = self.data_deque[-1][2] if self.data_deque else 0

        if not self.is_classification_active:
            if current_ir_state == 1 and self.previous_ir_state == 0:
                if not self.active_classifier:
                    if self.on_status_message:
                        self.on_status_message("Obstacle detected. Select a classifier to begin.")
                else:
                    self.is_classification_active = True
                    self.detection_start_time = time.time()
                    self.servo_codes_buffer.clear()
                    self.classification_name_buffer.clear()
                    if self.on_status_message:
                        self.on_status_message("IR Triggered! Classifying...")
        else:
            if self.active_classifier:
                servo_code_result, processed_frame, friendly_name = self.image_processor.process_frame(frame, self.active_classifier)
                self.servo_codes_buffer[servo_code_result.value] += 1
                self.classification_name_buffer[friendly_name] += 1

            if time.time() - self.detection_start_time >= self.config.DETECTION_PROCESSING_TIME_SECONDS:
                if self.servo_codes_buffer:
                    most_common_code_value = self.servo_codes_buffer.most_common(1)[0][0]
                    most_common_name = self.classification_name_buffer.most_common(1)[0][0]
                    
                    self.current_servo_code = ServoCode(most_common_code_value)
                    self.serial_manager.send_command(self.pwm_value, self.current_servo_code)
                    
                    if self.on_status_message:
                        self.on_status_message(f"Classification complete: {most_common_name}")
                
                self.is_classification_active = False
                self.detection_start_time = None
                self.servo_codes_buffer.clear()
                self.classification_name_buffer.clear()

        self.previous_ir_state = current_ir_state

        if self.on_frame_update:
            self.on_frame_update(processed_frame)

    def send_debug_servo_command(self, servo_code: ServoCode):
        if self.on_status_message:
            self.on_status_message(f"Sending debug servo command: {servo_code.name}")
        self.current_servo_code = servo_code
        self.serial_manager.send_command(self.pwm_value, self.current_servo_code)

    def _send_heartbeat_loop(self):
        while not self.stop_event.is_set():
            if self.serial_manager.connected:
                self.serial_manager.send_command(self.pwm_value, self.current_servo_code)
            time.sleep(self.config.HEARTBEAT_INTERVAL_SECONDS)
