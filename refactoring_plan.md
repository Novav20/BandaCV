# Refactoring Plan for PruebasDeVision

This document outlines a plan to refactor the `cvband.py` and `main.py` files to improve scalability, modularity, flexibility, and maintainability, adhering to good practices and modern architectures for vision/embedded systems projects. The code will be written in English, but our conversation will remain in Spanish.

## Action Items for User

- [ ] **Configure Motor Gear Ratio:**
    - **Task:** The RPM calculation for the motor has been corrected, but it now depends on the specific gear ratio of your motor.
    - **Action:**
        1.  Look at the metal gearbox on your Pololu 37D motor. The gear ratio (e.g., `50:1`, `70:1`) should be written on it.
        2.  Open the file `arduino_code/arduino_code.ino`.
        3.  Find the line `const int MOTOR_GEAR_RATIO = 50;`
        4.  Change the value `50` to the gear ratio of your motor (e.g., if it's `70:1`, change it to `70`).
        5.  **Re-upload the sketch to your Arduino** for the changes to take effect.

## Summary of Recent Changes (Session 2025-10-01)

-   **Hardware Communication Resilience:**
    -   The application now automatically detects when the Arduino is disconnected and enters a non-blocking reconnection loop, with status updates shown in the UI.
    -   A **heartbeat mechanism** has been implemented. The Python app sends a command every second to the Arduino.
    -   An **Arduino-side watchdog** has been implemented. If the Arduino doesn't receive a command for 2 seconds, it now autonomously enters a safe state (motor off, servo home), preventing runaway hardware.
    -   Upon reconnection, the UI and the application's internal state are safely reset to PWM 0 to prevent unexpected motor startup.

-   **RPM Calculation Fix:**
    -   The RPM calculation was found to be significantly inflated due to an incorrect `pulses_per_revolution` value.
    -   The formula in `arduino_code.ino` has been corrected to use the encoder's base CPR (16) and the motor's specific gear ratio. This now requires user configuration (see Action Items).

-   **IR Sensor Trigger:**
    -   The classification logic was changed from being "level-triggered" (requiring the object to stay in front of the sensor) to **"rising-edge triggered"**.
    -   The classification process now starts the moment the IR sensor detects an object and continues for a set duration, even if the object moves past the sensor.

-   **Servo Debugging:**
    -   A "Servo Debug" window was added to the GUI to allow for manual, persistent control of the servo.
    -   Fixed a bug where the debug position would be immediately overridden by the heartbeat.

-   **Bug Fixes & UX Improvements:**
    -   Fixed a race condition that could cause a crash on application shutdown.
    -   Added a user notification for when the IR sensor is triggered without an active classifier.

## Task Plan (Checklist)

### Phase 1: Setup and Configuration

- [x] **Version Control Setup**
- [x] **Environment Setup (Manjaro Linux)**
- [x] **Project Structure**
- [x] **Configuration Management**

### Phase 2: Refactor `cvband.py` (Vision Processing Layer)

- [x] **Introduce Classes for Vision Components**
- [x] **Improve Modularity and Reusability**
- [x] **Error Handling**

### Phase 3: Refactor `main.py` (Hardware Abstraction, Business Logic, and GUI)

- [x] **Hardware Abstraction Layer (HAL)**
- [x] **Business Logic Layer**
- [x] **User Interface Layer (Replace PySimpleGUI with PyQt6)**
- [x] **Threading Model**

### Phase 4: Hardware Integration (Step-by-Step)

- [x] **Infrared (IR) Sensor Interaction:**
    - [x] Verify existing implementation for IR sensor reading and UI LED update.
    - [x] **(FIXED)** Logic updated to be a rising-edge trigger for classification.
- [x] **Servomotor Integration:**
    - [x] Connect servomotor to Arduino (`SERVO_PIN`).
    - [x] Test servomotor control from Python application (e.g., by selecting different classifiers).
    - [x] **(ADDED)** Servo Debug UI for isolated testing.
- [x] **DC Motor with Encoder Integration:**
    - [x] Connect DC motor and encoder to Arduino (`MOTOR_PWM_PIN`, `MOTOR_DIR_PIN`, `RPM_SENSOR_PIN`).
    - [x] Test motor speed control from Python application (PWM slider).
    - [x] **(FIXED)** Test RPM reading and graph update in UI. Calculation was corrected in firmware. Requires user to set `MOTOR_GEAR_RATIO`.

### Phase 5: Testing and Deployment (Moved to End)

- [ ] **Unit Tests:**
    - [ ] Write unit tests for each class and module (e.g., `ImageProcessor`, `SerialManager`, `ObjectClassifier`).
- [ ] **Integration Tests:**
    - [ ] Test the interaction between different layers and components.
- [ ] **Documentation:**
    - [x] Update `README.md` with new architecture, setup instructions, and usage.
    - [x] Add docstrings to all classes and functions.

## Future Tasks & Reminders (for next session)

- [x] **Fix Application Shutdown Errors:** Implemented a guard in `process_video_frame` to prevent crashes.
- [x] **Ensure Motor Stops on Exit:** Implemented in two ways: a best-effort command from Python on shutdown, and a robust watchdog on the Arduino.
