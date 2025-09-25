import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QCheckBox, QLineEdit
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt6agg import FigureCanvasQTAgg as FigureCanvas

from src.core.application_controller import ApplicationController
from src.config.config import AppConfig

class MainWindow(QMainWindow):
    # Define custom signals for updating UI from other threads
    frame_update_signal = pyqtSignal(np.ndarray)
    graph_update_signal = pyqtSignal(list, list)
    led_update_signal = pyqtSignal(int)
    calibration_update_signal = pyqtSignal(float)
    status_message_signal = pyqtSignal(str)

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
            self.status_message_signal.emit
        )

        # Timer for processing video frames
        self.video_timer = QTimer(self)
        self.video_timer.timeout.connect(self.controller.process_video_frame)
        self.video_timer.start(AppConfig.UI_UPDATE_INTERVAL_MS if AppConfig.UI_UPDATE_INTERVAL_MS > 0 else 1)

        self.controller.start()

    def setup_ui(self):
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
        left_column_column.addWidget(self.size_checkbox)

        # Action Buttons
        button_layout = QHBoxLayout()
        calibrate_button = QPushButton("Calibrate Camera")
        calibrate_button.clicked.connect(self.controller.calibrate_camera)
        button_layout.addWidget(calibrate_button)

        stop_button = QPushButton("Stop")
        stop_button.clicked.connect(self.close)
        button_layout.addWidget(stop_button)

        left_column_layout.addLayout(button_layout)

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
        self.ax.set_facecolor('#1A2835')
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')

        self.ax.set_ylim(0, 430)
        self.ax.set_xlabel('time (s)')
        self.ax.set_ylabel('velocity (rpm)')
        self.ax.set_title('REAL-TIME RPM READING', color='white', fontname='Arial', fontweight='bold', fontsize=12, fontstyle='italic')
        self.line, = self.ax.plot([], [], linewidth=2, linestyle='solid', color='white')
        self.figure.set_facecolor('#1A2835')
        self.figure.tight_layout()

    def connect_signals(self):
        self.frame_update_signal.connect(self.update_webcam_feed)
        self.graph_update_signal.connect(self.update_graph)
        self.led_update_signal.connect(self.update_led)
        self.calibration_update_signal.connect(self.update_calibration_label)
        self.status_message_signal.connect(self.status_bar.showMessage)

    def update_webcam_feed(self, frame: np.ndarray):
        if frame is None:
            return
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
        p = convert_to_qt_format.scaled(self.webcam_label.width(), self.webcam_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
        self.webcam_label.setPixmap(QPixmap.fromImage(p))

    def update_graph(self, time_values: list, rpm_values: list):
        window_size = 5
        if len(rpm_values) >= window_size:
            smoothed_rpm_values = np.convolve(rpm_values, np.ones(window_size)/window_size, mode='valid')
            self.line.set_data(time_values[window_size-1:], smoothed_rpm_values)
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()

    def update_led(self, state: int):
        if state == 1:
            self.led_label.setStyleSheet("background-color: red; border-radius: 20px;")
        else:
            self.led_label.setStyleSheet("background-color: gray; border-radius: 20px;")

    def update_calibration_label(self, pixels_per_cm: float):
        self.calibration_label.setText(f"px/cm: {pixels_per_cm:.2f}")

    def update_pwm_from_slider(self, value: int):
        self.pwm_text.setText(str(value))
        self.controller.set_pwm(value)

    def update_pwm_from_text(self):
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
        if checked:
            # Deactivate other checkboxes
            if classifier_key != "color":
                self.color_checkbox.setChecked(False)
            if classifier_key != "shape":
                self.shape_checkbox.setChecked(False)
            if classifier_key != "size":
                self.size_checkbox.setChecked(False)
            
            self.controller.set_active_classifier(classifier_key)
        else:
            # If unchecked, ensure no classifier is active if all are unchecked
            if not self.color_checkbox.isChecked() and \
               not self.shape_checkbox.isChecked() and \
               not self.size_checkbox.isChecked():
                self.controller.set_active_classifier(None) # Deactivate all

    def closeEvent(self, event):
        self.controller.stop()
        event.accept()
