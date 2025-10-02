import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QSlider,
                             QCheckBox, QLineEdit, QDialog, QDialogButtonBox)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from src.core.application_controller import ApplicationController
from src.config.config import AppConfig
from src.vision.classifiers import ServoCode


class ServoDebugDialog(QDialog):
    """
    A dialog window for manually sending servo commands for debugging.
    """
    def __init__(self, controller: ApplicationController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Servo Debugging")
        self.layout = QVBoxLayout(self)

        # Create buttons for each position
        btn_triangle = QPushButton("Triangle / Red / Small (Pos: 30°)")
        btn_triangle.clicked.connect(lambda: self.send_command(ServoCode.TRIANGLE))
        self.layout.addWidget(btn_triangle)

        btn_square = QPushButton("Square / Yellow / Medium (Pos: 90°)")
        btn_square.clicked.connect(lambda: self.send_command(ServoCode.SQUARE))
        self.layout.addWidget(btn_square)

        btn_circle = QPushButton("Circle / Green / Large (Pos: 150°)")
        btn_circle.clicked.connect(lambda: self.send_command(ServoCode.CIRCLE))
        self.layout.addWidget(btn_circle)

        btn_unknown = QPushButton("Unknown / Home (Pos: 0°)")
        btn_unknown.clicked.connect(lambda: self.send_command(ServoCode.UNKNOWN))
        self.layout.addWidget(btn_unknown)

        # Add a close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        self.layout.addWidget(button_box)

    def send_command(self, servo_code: ServoCode):
        """Sends the selected servo command via the controller."""
        self.controller.send_debug_servo_command(servo_code)


class MainWindow(QMainWindow):
    """The main window of the BandaCV application.

    This class is responsible for creating and managing the graphical user
    interface (GUI) using PyQt6. It displays the webcam feed, control widgets,
    and data visualizations. It communicates with the ApplicationController to
    send user commands and receive updates.

    Args:
        controller (ApplicationController): The main application controller.
    """
    # Define custom signals for updating UI from other threads
    frame_update_signal = pyqtSignal(np.ndarray)
    graph_update_signal = pyqtSignal(list, list)
    led_update_signal = pyqtSignal(int)
    calibration_update_signal = pyqtSignal(float)
    status_message_signal = pyqtSignal(str)
    pwm_update_signal = pyqtSignal(int)

    def __init__(self, controller: ApplicationController):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("CVBAND Project - VISABAT Inc.")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.setup_ui()
        self.connect_signals()
        self.controller.register_ui_callbacks(
            self.frame_update_signal.emit,
            self.graph_update_signal.emit,
            self.led_update_signal.emit,
            self.calibration_update_signal.emit,
            self.status_message_signal.emit,
            self.pwm_update_signal.emit
        )

        # Timer for processing video frames
        self.video_timer = QTimer(self)
        self.video_timer.timeout.connect(self.controller.process_video_frame)
        self.video_timer.start(AppConfig.UI_UPDATE_INTERVAL_MS if AppConfig.UI_UPDATE_INTERVAL_MS > 0 else 1)

        self.controller.start()

    def setup_ui(self):
        """Initializes and arranges all the UI widgets in the main window."""
        # Left Column: Controls and Graph
        left_column_layout = QVBoxLayout()

        # Title
        title_label = QLabel("CVBAND Project")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        left_column_layout.addWidget(title_label)

        # Graph
        self.figure, self.ax = plt.subplots(figsize=(5.3, 2.2))
        self.canvas = FigureCanvas(self.figure)
        left_column_layout.addWidget(self.canvas)
        self.setup_graph()

        # PWM Control
        pwm_label = QLabel("PWM")
        pwm_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        left_column_layout.addWidget(pwm_label)

        pwm_control_layout = QHBoxLayout()
        self.pwm_slider = QSlider(Qt.Orientation.Horizontal)
        self.pwm_slider.setRange(0, 255)
        self.pwm_slider.setValue(self.controller.pwm_value)
        self.pwm_slider.valueChanged.connect(self.update_pwm_from_slider)
        pwm_control_layout.addWidget(self.pwm_slider)

        self.pwm_text = QLineEdit(str(self.controller.pwm_value))
        self.pwm_text.setFixedWidth(50)
        self.pwm_text.returnPressed.connect(self.update_pwm_from_text)
        pwm_control_layout.addWidget(self.pwm_text)

        update_pwm_button = QPushButton("Update")
        update_pwm_button.clicked.connect(self.update_pwm_from_text)
        pwm_control_layout.addWidget(update_pwm_button)

        left_column_layout.addLayout(pwm_control_layout)

        # Obstacle Sensor State & Calibration
        sensor_calib_layout = QHBoxLayout()
        obstacle_label = QLabel("Obstacle Sensor State:")
        obstacle_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        sensor_calib_layout.addWidget(obstacle_label)

        self.led_label = QLabel()
        self.led_label.setFixedSize(40, 40)
        self.update_led(0) # Initial state
        sensor_calib_layout.addWidget(self.led_label)

        self.calibration_label = QLabel(f"px/cm: {self.controller.pixels_per_cm:.2f}" if self.controller.pixels_per_cm else "px/cm: N/A")
        self.calibration_label.setStyleSheet("font-size: 12px;")
        sensor_calib_layout.addWidget(self.calibration_label)

        left_column_layout.addLayout(sensor_calib_layout)

        # Classifier Selection
        classifier_label = QLabel("Classifier")
        classifier_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        left_column_layout.addWidget(classifier_label)

        self.color_checkbox = QCheckBox("Color")
        self.color_checkbox.toggled.connect(lambda checked: self.on_classifier_checkbox_toggled("color", checked))
        left_column_layout.addWidget(self.color_checkbox)

        self.shape_checkbox = QCheckBox("Shape")
        self.shape_checkbox.toggled.connect(lambda checked: self.on_classifier_checkbox_toggled("shape", checked))
        left_column_layout.addWidget(self.shape_checkbox)

        self.size_checkbox = QCheckBox("Size")
        self.size_checkbox.toggled.connect(lambda checked: self.on_classifier_checkbox_toggled("size", checked))
        left_column_layout.addWidget(self.size_checkbox)

        # Action Buttons
        button_layout = QHBoxLayout()
        calibrate_button = QPushButton("Calibrate Camera")
        calibrate_button.clicked.connect(self.controller.calibrate_camera)
        button_layout.addWidget(calibrate_button)

        stop_button = QPushButton("Stop")
        stop_button.clicked.connect(self.close)
        button_layout.addWidget(stop_button)

        left_column_layout.addLayout(button_layout)

        # Debug Buttons
        debug_layout = QHBoxLayout()
        servo_debug_button = QPushButton("Servo Debug")
        servo_debug_button.clicked.connect(self.open_servo_debug_dialog)
        debug_layout.addWidget(servo_debug_button)
        left_column_layout.addLayout(debug_layout)


        # Status Message
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Application Ready")

        self.main_layout.addLayout(left_column_layout)

        # Right Column: Webcam Feed
        right_column_layout = QVBoxLayout()
        self.webcam_label = QLabel("Webcam Feed")
        self.webcam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.webcam_label.setFixedSize(AppConfig.CAMERA_RESOLUTION[0], AppConfig.CAMERA_RESOLUTION[1])
        self.webcam_label.setStyleSheet("border: 2px solid black;")
        right_column_layout.addWidget(self.webcam_label)

        self.main_layout.addLayout(right_column_layout)

    def setup_graph(self):
        """Configures the appearance of the Matplotlib graph for RPM data."""
        self.ax.set_facecolor('#1A2835')
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')

        self.ax.set_ylim(0, AppConfig.GRAPH_RPM_MAX_LIMIT)
        self.ax.set_xlabel('time (s)')
        self.ax.set_ylabel('velocity (rpm)')
        self.ax.set_title('REAL-TIME RPM READING', color='white', fontname='DejaVu Sans', fontweight='bold', fontsize=12, fontstyle='italic')
        self.line, = self.ax.plot([], [], linewidth=2, linestyle='solid', color='white')
        self.figure.set_facecolor('#1A2835')
        self.figure.tight_layout()

    def connect_signals(self):
        """Connects the UI signals to their respective slots."""
        self.frame_update_signal.connect(self.update_webcam_feed)
        self.graph_update_signal.connect(self.update_graph)
        self.led_update_signal.connect(self.update_led)
        self.calibration_update_signal.connect(self.update_calibration_label)
        self.status_message_signal.connect(self.status_bar.showMessage)
        self.pwm_update_signal.connect(self.update_pwm_widgets)

    def open_servo_debug_dialog(self):
        """Opens the servo debugging dialog."""
        dialog = ServoDebugDialog(self.controller, self)
        dialog.exec()

    def update_pwm_widgets(self, value: int):
        """Updates the PWM slider and text box to a given value.

        This method is called programmatically from the controller, so it blocks
        signals to prevent creating a feedback loop.
        """
        # Block signals to prevent a feedback loop
        self.pwm_slider.blockSignals(True)
        self.pwm_text.blockSignals(True)

        self.pwm_slider.setValue(value)
        self.pwm_text.setText(str(value))

        # Unblock signals so user interaction works again
        self.pwm_slider.blockSignals(False)
        self.pwm_text.blockSignals(False)

    def update_webcam_feed(self, frame: np.ndarray):
        """Updates the webcam feed label with a new frame.

        Args:
            frame (np.ndarray): The new video frame to display.
        """
        if frame is None:
            return
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
        p = convert_to_qt_format.scaled(self.webcam_label.width(), self.webcam_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
        self.webcam_label.setPixmap(QPixmap.fromImage(p))

    def update_graph(self, time_values: list, rpm_values: list):
        """Updates the RPM graph with new data.

        Args:
            time_values (list): A list of timestamps.
            rpm_values (list): A list of RPM values.
        """
        window_size = 5
        if len(rpm_values) >= window_size:
            smoothed_rpm_values = np.convolve(rpm_values, np.ones(window_size)/window_size, mode='valid')
            self.line.set_data(time_values[window_size-1:], smoothed_rpm_values)
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()

    def update_led(self, state: int):
        """Updates the obstacle sensor LED indicator.

        Args:
            state (int): The state of the obstacle sensor (1 for detected, 0 for not).
        """
        if state == 1:
            self.led_label.setStyleSheet("background-color: red; border-radius: 20px;")
        else:
            self.led_label.setStyleSheet("background-color: gray; border-radius: 20px;")

    def update_calibration_label(self, pixels_per_cm: float):
        """Updates the calibration label with the new pixels-per-centimeter value.

        Args:
            pixels_per_cm (float): The new calibration value.
        """
        self.calibration_label.setText(f"px/cm: {pixels_per_cm:.2f}")

    def update_pwm_from_slider(self, value: int):
        """Updates the PWM value from the slider.

        Args:
            value (int): The new PWM value from the slider.
        """
        self.pwm_text.setText(str(value))
        self.controller.set_pwm(value)

    def update_pwm_from_text(self):
        """Updates the PWM value from the text input field."""
        try:
            value = int(self.pwm_text.text())
            if 0 <= value <= 255:
                self.pwm_slider.setValue(value)
                self.controller.set_pwm(value)
            else:
                self.status_bar.showMessage("PWM value must be between 0 and 255.")
        except ValueError:
            self.status_bar.showMessage("Invalid PWM value. Please enter a number.")

    def on_classifier_checkbox_toggled(self, classifier_key: str, checked: bool):
        """Handles the toggling of classifier checkboxes.

        This method ensures that only one classifier can be active at a time.

        Args:
            classifier_key (str): The key of the classifier that was toggled.
            checked (bool): The new state of the checkbox.
        """
        if checked:
            # Deactivate other checkboxes
            if classifier_key != "color":
                self.color_checkbox.setChecked(False)
            if classifier_key != "shape":
                self.shape_checkbox.setChecked(False)
            if classifier_key != "size":
                self.size_checkbox.setChecked(False)
            
            if not self.controller.set_active_classifier(classifier_key):
                # If setting the classifier fails (e.g., size not calibrated),
                # uncheck the box to reflect the inactive state.
                if classifier_key == "size":
                    self.size_checkbox.setChecked(False)

        else:
            # If unchecked, ensure no classifier is active if all are unchecked
            if not self.color_checkbox.isChecked() and \
               not self.shape_checkbox.isChecked() and \
               not self.size_checkbox.isChecked():
                self.controller.set_active_classifier(None) # Deactivate all

    def closeEvent(self, event):
        """Handles the window close event.

        This method stops the application controller before closing the window.

        Args:
            event: The close event.
        """
        self.controller.stop()
        event.accept()
