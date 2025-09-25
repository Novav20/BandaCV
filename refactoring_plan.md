# Refactoring Plan for PruebasDeVision

This document outlines a plan to refactor the `cvband.py` and `main.py` files to improve scalability, modularity, flexibility, and maintainability, adhering to good practices and modern architectures for vision/embedded systems projects. The code will be written in English, but our conversation will remain in Spanish.

## Current State Analysis

### `cvband.py`

*   **Lack of Object-Oriented Design:** Functions are standalone, making it difficult to manage state, configuration, and dependencies.
*   **Hardcoded Thresholds and Constants:** Many magic numbers are scattered throughout the code, reducing configurability.
*   **Tight Coupling:** Functions are highly interdependent, hindering reusability and testing.
*   **Redundant Code:** Similar logic is repeated across different detection functions.
*   **Mixed Responsibilities:** Functions combine classification with control logic (e.g., returning both shape and servo code).
*   **Limited Error Handling:** Insufficient error handling, especially for hardware interactions.
*   **Global Variables:** Use of global constants instead of configurable parameters.
*   **Magic Strings:** Servo codes are represented as magic strings, impacting readability.

### `main.py`

*   **Monolithic Structure:** All application logic is contained within a single main loop, making it complex and hard to extend.
*   **Tight Coupling with GUI:** Direct updates to GUI elements from vision processing functions create strong dependencies.
*   **Excessive Global Variables:** Numerous global variables complicate state management.
*   **Absence of Clear Architecture:** Lack of separation of concerns (GUI, business logic, hardware abstraction).
*   **Potential Threading Issues:** While serial data is threaded, the main loop's synchronous operations can affect UI responsiveness.
*   **Hardcoded UI Elements:** Inflexible UI layout.
*   **PySimpleGUI Dependency:** The current GUI framework needs replacement.
*   **Repetitive Logic:** Duplicated code for classifier selection and obstacle detection.
*   **No Configuration Management:** Parameters are hardcoded or loosely managed.

## Refactoring Goals

*   **Modularity:** Decompose the application into smaller, independent, and reusable components.
*   **Scalability:** Enable easy extension and modification of components.
*   **Flexibility:** Facilitate swapping of components (e.g., GUI frameworks, camera sources, classification algorithms).
*   **Maintainability:** Enhance code readability, reduce redundancy, and simplify debugging.
*   **Testability:** Improve the ease of writing unit tests for individual components.
*   **Modern Architecture:** Implement suitable design patterns (e.g., MVC/MVVM, Strategy, Observer).
*   **Replace PySimpleGUI:** Integrate a new, modern GUI framework (e.g., PyQt, Kivy, or a web-based solution).

## Proposed Architecture

A layered architecture is recommended:

1.  **Hardware Abstraction Layer (HAL):** Manages interactions with the camera and serial port (Arduino).
2.  **Vision Processing Layer:** Contains all image processing and classification logic, independent of the GUI.
3.  **Business Logic Layer:** Orchestrates the flow between vision processing, hardware, and the GUI.
4.  **User Interface Layer:** Handles all GUI interactions and displays, decoupled from the core logic.
5.  **Configuration Layer:** Manages all application settings and parameters.

## Task Plan

### Phase 1: Setup and Configuration

1.  **Version Control Setup:**
    *   Initialize a Git repository in the project root.
    *   Create a corresponding GitHub repository and link it.
    *   **Commit Strategy:** After each task that results in a functional, tested change, commit the changes. Commit messages should be clear, concise, and follow conventional guidelines (e.g., `feat: Add new feature`, `fix: Resolve bug`, `refactor: Improve code structure`).

2.  **Environment Setup (Manjaro Linux):**
    *   Create a Python virtual environment (`.venv`) to manage project dependencies in isolation. This is crucial for avoiding conflicts with system-wide packages.
        ```bash
        python -m venv .venv
        source .venv/bin/activate
        ```
    *   Install necessary dependencies (e.g., `opencv-python`, `pyserial`, `numpy`, `matplotlib`, `PyQt5` or chosen GUI framework) into the virtual environment.
        ```bash
        pip install -r requirements.txt
        ```

3.  **Project Structure:**
    *   `src/`: For core application logic.
    *   `src/config/`: For configuration files.
    *   `src/hardware/`: For HAL components.
    *   `src/vision/`: For vision processing modules.
    *   `src/gui/`: For GUI-related code.
    *   `src/core/`: For business logic and main application flow.
    *   `tests/`: For unit and integration tests.
    *   `requirements.txt`: To manage dependencies.
    *   `README.md`: Project documentation.

4.  **Configuration Management:**
    *   Extract all hardcoded constants (thresholds, camera settings, serial settings) into a `config.py` file or use a more robust configuration library (e.g., `configparser`, `PyYAML`).
    *   Implement a `Config` class to load and manage these settings.

## Recommendations for Continuing Work (Gemini CLI Context Reset)

Since the Gemini CLI context resets, it's important to have a clear strategy for resuming work:

*   **Always Commit Frequently:** Ensure all functional changes are committed to Git. This is your primary backup and progress tracker.
*   **Detailed `README.md`:** Keep the `README.md` updated with the current state of the project, setup instructions, and any specific commands needed to run or test the application.
*   **Task Tracking:** Use this `refactoring_plan.md` file as a checklist. Mark completed tasks and note any pending items or decisions.
*   **Session Log (Optional):** If a task is particularly complex or involves many steps, consider keeping a local scratchpad or log of the commands you've executed and the reasoning behind them. This can be a simple text file in the project directory.
*   **Start with `git status` and `git log`:** When resuming, always check `git status` to see uncommitted changes and `git log` to review recent commits. This helps re-establish context quickly.
*   **Review `refactoring_plan.md`:** Re-read this plan to recall the overall goals and the next steps.
*   **Activate Virtual Environment:** Always remember to activate your virtual environment (`source .venv/bin/activate`) before running any Python commands.



### Phase 2: Refactor `cvband.py` (Vision Processing Layer)

1.  **Introduce Classes for Vision Components:**
    *   **`ImageProcessor` Class:**
        *   Encapsulate common image processing steps (e.g., `color_detector`, `shape_detector`, `size_detector`, `calibrate_camera`).
        *   Methods should take an image frame and return processed data (e.g., detected objects, classifications) without directly modifying the frame or handling display.
        *   Parameters like thresholds and camera calibration values should be passed during initialization or as method arguments, not hardcoded.
    *   **`ObjectClassifier` Class (Strategy Pattern):**
        *   Define an interface for classifiers (e.g., `ColorClassifier`, `ShapeClassifier`, `SizeClassifier`).
        *   Each classifier class will implement a `classify(frame)` method.
        *   The `ImageProcessor` can use an instance of `ObjectClassifier` to perform classification.
    *   **`Camera` Class:**
        *   Abstract camera initialization and frame capturing.
        *   Handle `cv2.VideoCapture` instance.
2.  **Improve Modularity and Reusability:**
    *   Break down complex functions into smaller, single-responsibility methods.
    *   Eliminate redundant code by creating helper methods or classes.
    *   Replace magic strings for servo codes with `Enum` types (e.g., `ClassificationType`, `ServoCode`).
3.  **Error Handling:**
    *   Implement robust error handling for image processing operations (e.g., `try-except` blocks for OpenCV functions).

### Phase 3: Refactor `main.py` (Hardware Abstraction, Business Logic, and GUI)

1.  **Hardware Abstraction Layer (HAL):**
    *   **`SerialManager` Class:**
        *   Handle serial port communication (Arduino).
        *   Methods for connecting, reading data, and writing commands (e.g., `send_command(pwm, servo_code)`).
        *   Manage `get_arduino_port` logic.
        *   Implement proper error handling for serial communication.
2.  **Business Logic Layer:**
    *   **`ApplicationController` Class:**
        *   Orchestrate the entire application flow.
        *   Connects the `Camera`, `ImageProcessor`, `ObjectClassifier`, and `SerialManager`.
        *   Manages the main application loop, data flow, and state.
        *   Handles obstacle detection logic and servo code determination.
        *   Should not directly interact with the GUI.
3.  **User Interface Layer (Replace PySimpleGUI with pyimgui):**
    *   **Choose a New GUI Framework:** We will proceed with `pyimgui` given its suitability for embedded vision systems and real-time display needs.
    *   **`GUI` Class (or equivalent):**
        *   Responsible solely for displaying information and capturing user input.
        *   Should observe changes in the `ApplicationController` (Observer Pattern) to update its display.
        *   Should trigger actions in the `ApplicationController` based on user input (e.g., button clicks, slider changes).
        *   Decouple UI elements from application logic.
    *   **Data Visualization:**
        *   Integrate `matplotlib` for plotting RPM data within the new GUI framework.
        *   Ensure graph updates are handled efficiently without blocking the UI.
4.  **Threading Model:**
    *   Review and potentially refine the threading strategy to ensure UI responsiveness and efficient background processing.
    *   Consider using a producer-consumer pattern for data exchange between threads.

### Phase 4: Testing and Deployment

1.  **Unit Tests:**
    *   Write unit tests for each class and module (e.g., `ImageProcessor`, `SerialManager`, `ObjectClassifier`).
2.  **Integration Tests:**
    *   Test the interaction between different layers and components.
3.  **Documentation:**
    *   Update `README.md` with new architecture, setup instructions, and usage.
    *   Add docstrings to all classes and functions.

## Example of Class Structure (Conceptual)

```python
# src/config/config.py
class AppConfig:
    WEBCAM_INDEX = 0
    BAUDRATE = 9600
    MAX_SAMPLES = 100
    # ... other thresholds and settings

# src/hardware/camera.py
class Camera:
    def __init__(self, camera_index):
        # Initialize cv2.VideoCapture
    def read_frame(self):
        # Capture and return frame
    def release(self):
        # Release camera

# src/hardware/serial_manager.py
class SerialManager:
    def __init__(self, baudrate):
        # Initialize serial connection
    def connect(self):
        # Find Arduino port and establish connection
    def read_data(self):
        # Read data from serial
    def send_command(self, pwm_value, servo_code):
        # Send command to Arduino
    def disconnect(self):
        # Close serial connection

# src/vision/classifiers.py
from enum import Enum

class ServoCode(Enum):
    TRIANGLE = '0'
    SQUARE = '1'
    CIRCLE = '2'
    RED = '0'
    YELLOW = '1'
    GREEN = '2'
    SMALL = '0'
    MEDIUM = '1'
    LARGE = '2'

class BaseClassifier:
    def classify(self, frame) -> (ServoCode, processed_frame):
        raise NotImplementedError

class ColorClassifier(BaseClassifier):
    def __init__(self, config):
        # Initialize color thresholds from config
    def classify(self, frame):
        # Implement color detection
        return servo_code, processed_frame

class ShapeClassifier(BaseClassifier):
    def __init__(self, config):
        # Initialize shape detection parameters
    def classify(self, frame):
        # Implement shape detection
        return servo_code, processed_frame

class SizeClassifier(BaseClassifier):
    def __init__(self, config, pixels_per_cm=None):
        # Initialize size detection parameters
    def calibrate(self, frame, known_diameter):
        # Implement calibration logic
        return pixels_per_cm
    def classify(self, frame):
        # Implement size detection
        return servo_code, processed_frame

# src/vision/image_processor.py
class ImageProcessor:
    def __init__(self, config):
        # Initialize common image processing tools
    def preprocess_frame(self, frame):
        # Apply common preprocessing (e.g., blurring, HSV conversion)
        return preprocessed_frame
    def process_frame(self, frame, classifier: BaseClassifier):
        # Use the provided classifier to process the frame
        return servo_code, processed_frame

# src/core/application_controller.py
class ApplicationController:
    def __init__(self, config, camera, serial_manager, image_processor):
        # Initialize components
        # Manage application state, obstacle detection, servo code logic
    def start(self):
        # Main application loop
    def stop(self):
        # Clean up resources
    def set_pwm(self, value):
        # Update PWM
    def set_classifier(self, classifier_type):
        # Change active classifier

# src/gui/main_window.py (Example using PyQt)
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt

class MainWindow(QMainWindow):
    def __init__(self, controller: ApplicationController):
        super().__init__()
        self.controller = controller
        # Setup UI elements, connect signals to controller methods
        # Display webcam feed, graph, LED, controls
    def update_webcam_feed(self, frame):
        # Convert OpenCV frame to QPixmap and display
    def update_graph(self, time_values, rpm_values):
        # Update matplotlib graph
    def update_led(self, state):
        # Update LED indicator
    def closeEvent(self, event):
        self.controller.stop()
        event.accept()

# main.py (New entry point)
from src.config.config import AppConfig
from src.hardware.camera import Camera
from src.hardware.serial_manager import SerialManager
from src.vision.image_processor import ImageProcessor
from src.vision.classifiers import ColorClassifier, ShapeClassifier, SizeClassifier
from src.core.application_controller import ApplicationController
from src.gui.main_window import MainWindow # Or other GUI framework

if __name__ == "__main__":
    config = AppConfig()
    camera = Camera(config.WEBCAM_INDEX)
    serial_manager = SerialManager(config.BAUDRATE)
    image_processor = ImageProcessor(config)

    # Initialize classifiers
    color_classifier = ColorClassifier(config)
    shape_classifier = ShapeClassifier(config)
    size_classifier = SizeClassifier(config) # Will need calibration

    controller = ApplicationController(config, camera, serial_manager, image_processor)
    # Register classifiers with controller
    controller.register_classifier("color", color_classifier)
    controller.register_classifier("shape", shape_classifier)
    controller.register_classifier("size", size_classifier)

    app = QApplication([]) # For PyQt
    main_window = MainWindow(controller)
    main_window.show()

    # Start controller in a separate thread if necessary, or integrate its loop with GUI event loop
    # For PyQt, QTimer can be used to periodically call controller's update method
    # controller.start() # This would be a blocking call, needs to be handled carefully with GUI

    app.exec_() # For PyQt
```
