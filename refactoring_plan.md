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

## Task Plan (Checklist)

### Phase 1: Setup and Configuration

- [x] **Version Control Setup:**
    - [x] Initialize a Git repository in the project root.
    - [ ] Create a corresponding GitHub repository and link it. (This is an external step, not managed by the agent)
    - [x] **Commit Strategy:** After each task that results in a functional, tested change, commit the changes. Commit messages should be clear, concise, and follow conventional guidelines (e.g., `feat: Add new feature`, `fix: Resolve bug`, `refactor: Improve code structure`).

- [x] **Environment Setup (Manjaro Linux):**
    - [x] Create a Python virtual environment (`.venv`) to manage project dependencies in isolation.
    - [x] Install necessary dependencies (e.g., `opencv-python`, `pyserial`, `numpy`, `matplotlib`, `PyQt5` or chosen GUI framework) into the virtual environment.

- [x] **Project Structure:**
    - [x] `src/`: For core application logic.
    - [x] `src/config/`: For configuration files.
    - [x] `src/hardware/`: For HAL components.
    - [x] `src/vision/`: For vision processing modules.
    - [x] `src/gui/`: For GUI-related code.
    - [x] `src/core/`: For business logic and main application flow.
    - [x] `tests/`: For unit and integration tests.
    - [x] `requirements.txt`: To manage dependencies.
    - [ ] `README.md`: Project documentation. (Needs to be updated)

- [x] **Configuration Management:**
    - [x] Extract all hardcoded constants (thresholds, camera settings, serial settings) into a `config.py` file or use a more robust configuration library (e.g., `configparser`, `PyYAML`).
    - [x] Implement a `Config` class to load and manage these settings.

## Recommendations for Continuing Work (Gemini CLI Context Reset)

Since the Gemini CLI context resets, it's important to have a clear strategy for resuming work:

*   **Always Commit Frequently:** Ensure all functional changes are committed to Git. This is your primary backup and progress tracker.
*   **Detailed `README.md`:** Keep the `README.md` updated with the current state of the project, setup instructions, and any specific commands needed to run or test the application.
*   **Task Tracking:** Use this `refactoring_plan.md` file as a checklist. Mark completed tasks and note any pending items or decisions.
*   **Session Log (Optional):** If a task is particularly complex or involves many steps, consider keeping a local scratchpad or log of the commands you've executed and the reasoning behind them. This can be a simple text file in the project directory.
*   **Start with `git status` and `git log`:** When resuming, always check `git status` to see uncommitted changes and `git log` to review recent commits. This helps re-establish context quickly.
*   **Review `refactoring_plan.md`:** Re-read this plan to recall the overall goals and the next steps.
*   **Activate Virtual Environment:** Always remember to activate your virtual environment (`source .venv/bin/activate`) before running any Python commands.

*   **Current Debugging Context (Serial Port & Fonts):**
    *   **Serial Port Issue:** The `ttyS` identifier was removed from `SERIAL_DEVICE_IDENTIFIERS` in `src/config/config.py` to prevent connection attempts to generic system serial ports.
    *   **Permission Denied Fix:** User was instructed to add themselves to the `uucp` group (`sudo usermod -a -G uucp $USER`) and to log out/in for changes to take effect.
    *   **Font Warnings:** User was advised to install `ttf-ms-fonts` via `yay` on Manjaro to resolve `findfont` warnings.
    *   **Serial Port Connection Verified:** The serial port connection issue has been resolved and verified.

## Debugging Session: DC Motor and Serial Communication (2025-09-29)

### Problem Statement:
The Pololu 37D DC motor with encoder, controlled via an L298N driver, was behaving like a binary switch (only full speed at PWM 255) despite UI input ranging from 0-255. Initial hardware checks (ENA to 5V/3.3V) showed no change, but touching the ENA pin modulated speed, suggesting a floating input or connection issue.

### Debugging Steps and Findings:

1.  **Initial Code Review (Arduino & Python):**
    *   `Motor.cpp`: `analogWrite()` and `setSpeed()` logic appeared correct.
    *   `Communication.cpp`: Initial parsing logic using `String.toInt()` was identified as a potential weak point.
    *   `serial_manager.py`: Python side seemed to correctly construct and send `PWM_SERVOCODE` commands.
    *   `connections.md`: Wiring diagram was verified and deemed correct.

2.  **Isolated Arduino Test Sketch:**
    *   A simple Arduino sketch was created to directly cycle PWM values (0-255) using `analogWrite()` without any serial communication.
    *   **Result:** The motor *successfully* accelerated and decelerated smoothly.
    *   **Conclusion:** This definitively proved that the hardware (Arduino's PWM pins, L298N driver, motor, power supply, and basic wiring) is capable of variable speed control. The problem was confirmed to be in the software, specifically the serial communication/parsing.

3.  **Attempted Software Fixes (Arduino `Communication.cpp`):
    *   **Fix 1: Robust Parsing:** Modified `Communication.cpp` to use `atoi()` (more reliable C-style string to int conversion) and `trim()` to handle potential `\r` characters. Changed separator from `_` to `,` in both Python and Arduino.
    *   **Result:** Motor behavior remained unchanged (binary switch). Debug messages from Arduino (e.g., "Comando Recibido: [XXX") showed that the Arduino was only receiving the PWM value, not the full command string with the separator and servo code.
    *   **Conclusion:** The problem was not in *how* the Arduino parsed the string, but that it was *not receiving the full string* in the first place.

4.  **Attempted Software Fixes (Python `serial_manager.py`):
    *   **Fix 2: Add Delay:** Added `time.sleep(0.05)` after `serial.write()` in Python to give Arduino more time to process.
    *   **Result:** No change. Arduino still only received partial commands.
    *   **Fix 3: Python Debug Prints:** Added `print(f"Sent from Python: {command.decode().strip()}")` to confirm Python was sending the full command.
    *   **Result:** Python confirmed it was sending the full command (e.g., `Sent from Python: 127,9`). However, Arduino debug messages were still not appearing in the Python terminal.

5.  **Isolation Test (Python sending, Arduino monitoring):
    *   **Setup:** Modified Python (`application_controller.py` and `serial_manager.py`) to prevent it from reading from the serial port, allowing `arduino-cli monitor` to have exclusive read access. Arduino was loaded with granular debug prints (`Recibido char: [X]`).
    *   **Result:** Python reported `Not connected to serial device. Command not sent.` because the `connect()` call was blocked by `arduino-cli monitor`. Crucially, **no "Recibido char:" messages appeared in the `arduino-cli monitor` terminal.**
    *   **Conclusion:** This definitively confirmed that **no serial data is physically reaching the Arduino's serial port from the computer.** The problem is at the physical layer of the serial communication.

### Current Status & Next Steps:

*   **Problem:** Physical serial communication breakdown between computer and Arduino. Python sends data, but Arduino does not receive it.
*   **Recommendation:** Focus on hardware troubleshooting:
    1.  **Try a different USB cable.**
    2.  **Try a different USB port** on the computer.
    3.  **Try a different computer** (if available) to rule out system-specific issues.
    4.  Inspect Arduino's USB port and serial chip for damage.
*   **Code State:**
    *   Python files (`application_controller.py`, `serial_manager.py`) have been reverted to their original state.
    *   Arduino file (`arduino_code/Communication.cpp`) still contains the granular debug prints. This will be reverted to its original state now.

## Debugging Session: Motor PWM and Timer Conflict (2025-09-30)

### Problem Statement
After fixing the serial communication parsing, the motor continued to exhibit "binary" behavior (only working at PWM 255). This occurred even though `atoi()` was correctly parsing the incoming integer values.

### Debugging Steps and Findings

1.  **Visual Debugging with LED:** Since the serial monitor was occupied by the Python application, a hardware debugging approach was used. An LED was connected to Arduino Pin 11. The Arduino code was modified to write the parsed `pwmValue` to this LED using `analogWrite()`.
2.  **Observation:** The brightness of the LED on Pin 11 correctly and smoothly corresponded to the PWM value sent from the Python UI (i.e., it got brighter as the slider was moved from 0 to 255).
    *   **Conclusion:** This definitively proved that the Python code, serial transmission, and Arduino command parsing were all working correctly. The `pwmValue` variable was being populated with the correct intermediate values.
3.  **Pin Swap Test:** The user connected the motor's ENA to Pin 11 and the debug LED to Pin 9.
    *   **Result:** The motor, now on Pin 11, worked perfectly with variable speed. The LED, now on Pin 9, exhibited the original problem: it only turned on at 255.
    *   **Conclusion:** This isolated the fault to **Arduino Pin 9**, which was not outputting a PWM signal as expected within the context of the full application.

### Root Cause Analysis

The contradictory behavior (Pin 9 working in an isolated test but not in the full application) was traced to a **hardware timer conflict**.
*   The Arduino `Servo` library, used for the classifier servo on Pin 10, uses the hardware **Timer1**.
*   On the Arduino Uno, Timer1 is also responsible for PWM functionality on **Pins 9 and 10**.
*   When the `Servo` library is initialized, it takes exclusive control of Timer1, disabling PWM on Pin 9.

### Resolution

1.  **Permanent Pin Change:** The motor's PWM control pin was permanently moved from Pin 9 to **Pin 11**, which uses a different hardware timer that does not conflict with the Servo library.
2.  **Code Update:** The `CONVEYOR_MOTOR_PWM_PIN` constant in `arduino_code.ino` was updated to `11`.
3.  **Documentation Update:** `connections.md` was updated to reflect the new wiring.
4.  **Code Cleanup:** All debugging code (the LED logic in `Communication.h` a.k.a. `cpp` and debug prints/delays in `serial_manager.py`) was removed. The serial protocol was reverted to use `_` as a separator for consistency.

### Phase 2: Refactor `cvband.py` (Vision Processing Layer)

- [x] **Introduce Classes for Vision Components:**
    - [x] **`ImageProcessor` Class:**
        - [x] Encapsulate common image processing steps (e.g., `color_detector`, `shape_detector`, `size_detector`, `calibrate_camera`).
        - [x] Methods should take an image frame and return processed data (e.g., detected objects, classifications) without directly modifying the frame or handling display.
        - [x] Parameters like thresholds and camera calibration values should be passed during initialization or as method arguments, not hardcoded.
    - [x] **`ObjectClassifier` Class (Strategy Pattern):**
        - [x] Define an interface for classifiers (e.g., `ColorClassifier`, `ShapeClassifier`, `SizeClassifier`).
        - [x] Each classifier class will implement a `classify(frame)` method.
    - [x] **`Camera` Class:**
        - [x] Abstract camera initialization and frame capturing.
        - [x] Handle `cv2.VideoCapture` instance.
- [x] **Improve Modularity and Reusability:**
    - [x] Break down complex functions into smaller, single-responsibility methods.
    - [x] Eliminate redundant code by creating helper methods or classes.
    - [x] Replace magic strings for servo codes with `Enum` types (e.g., `ClassificationType`, `ServoCode`).
- [x] **Error Handling:**
    - [x] Implement robust error handling for image processing operations (e.g., `try-except` blocks for OpenCV functions).

### Phase 3: Refactor `main.py` (Hardware Abstraction, Business Logic, and GUI)

- [x] **Hardware Abstraction Layer (HAL):**
    - [x] **`SerialManager` Class:**
        - [x] Handle serial port communication (Arduino).
        - [x] Methods for connecting, reading data, and writing commands (e.g., `send_command(pwm, servo_code)`).
        - [x] Manage `get_arduino_port` logic.
        - [x] Implement proper error handling for serial communication.

- [x] **Business Logic Layer:**
    - [x] **`ApplicationController` Class:**
        - [x] Orchestrate the entire application flow.
        - [x] Connects the `Camera`, `ImageProcessor`, `ObjectClassifier`, and `SerialManager`.
        - [x] Manages the main application loop, data flow, and state.
        - [x] Handles obstacle detection logic and servo code determination.
        - [x] Should not directly interact with the GUI.
- [x] **User Interface Layer (Replace PySimpleGUI with PyQt6):**
    - [x] **Choose a New GUI Framework:** We will proceed with `PyQt6` given its robustness, feature set, and suitability for desktop applications with complex UI and integration needs.
    - [x] **`GUI` Class (or equivalent):**
        - [x] Responsible solely for displaying information and capturing user input.
        - [x] Should observe changes in the `ApplicationController` (Observer Pattern) to update its display.
        - [x] Should trigger actions in the `ApplicationController` based on user input (e.g., button clicks, slider changes).
        - [x] Decouple UI elements from application logic.
    - [x] **Data Visualization:**
        - [x] Integrate `matplotlib` for plotting RPM data within the new GUI framework.
        - [x] Ensure graph updates are handled efficiently without blocking the UI.

- [x] **Threading Model:**
    - [x] Review and potentially refine the threading strategy to ensure UI responsiveness and efficient background processing.
    - [x] Consider using a producer-consumer pattern for data exchange between threads.

### Phase 4: Hardware Integration (Step-by-Step)

- [ ] **Infrared (IR) Sensor Interaction:**
    - [x] Verify existing implementation for IR sensor reading and UI LED update.
    - [ ] Connect IR sensor to Arduino (`OBSTACLE_SENSOR_PIN`).
    - [ ] Upload Arduino code.
    - [ ] Run Python application and test interaction.
- [ ] **Servomotor Integration:**
    - [ ] Connect servomotor to Arduino (`SERVO_PIN`).
    - [ ] Test servomotor control from Python application (e.g., by selecting different classifiers).
- [ ] **DC Motor with Encoder Integration:**
    - [ ] Connect DC motor and encoder to Arduino (`MOTOR_PWM_PIN`, `MOTOR_DIR_PIN`, `RPM_SENSOR_PIN`).
    - [ ] Test motor speed control from Python application (PWM slider).
    - [ ] Test RPM reading and graph update in UI.

### Phase 5: Testing and Deployment (Moved to End)

- [ ] **Unit Tests:**
    - [ ] Write unit tests for each class and module (e.g., `ImageProcessor`, `SerialManager`, `ObjectClassifier`).
- [ ] **Integration Tests:**
    - [ ] Test the interaction between different layers and components.
- [ ] **Documentation:**
    - [x] Update `README.md` with new architecture, setup instructions, and usage.
    - [x] Add docstrings to all classes and functions.

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

class ServoCode:
    TRIANGLE = '0'
    SQUARE = '1'
    CIRCLE = '2'
    RED = '0'
    YELLOW = '1'
    GREEN = '2'
    SMALL = '0'
    MEDIUM = '1'
    LARGE = '2'
    UNKNOWN = '9' # Default for unclassified or error

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