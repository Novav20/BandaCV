# BandaCV - Conveyor Belt Vision System

## Description

BandaCV is a Python-based application that uses computer vision to classify objects on a conveyor belt. It is designed to be a modular and extensible system for educational and prototyping purposes. The system can identify objects based on their color, shape, and size, and it can communicate with an Arduino-based controller to sort the objects.

## Features

*   **Object Classification:** Classify objects by color (red, yellow, green), shape (triangle, square, circle), and size (small, medium, large).
*   **Hardware Integration:** Communicates with an Arduino over a serial connection to control a servo-driven sorting mechanism.
*   **Real-time Video Processing:** Uses OpenCV to process a live video feed from a webcam.
*   **Modular Architecture:** The application is structured into distinct layers for hardware abstraction, vision processing, business logic, and user interface, making it easy to modify and extend.
*   **GUI:** A PyQt-based graphical user interface to control the application and visualize the results.

## Project Structure

```
/home/novillus/Documents/VSCodeProjects/BandaCV/
├───.gitignore
├───main.py
├───refactoring_plan.md
├───requirements.txt
├───.git/...
├───.venv/...
├───old_code/
├───src/
│   ├───config/
│   │   ├───config.py
│   ├───core/
│   │   ├───application_controller.py
│   ├───gui/
│   │   ├───main_window.py
│   ├───hardware/
│   │   ├───camera.py
│   │   ├───serial_manager.py
│   └───vision/
│       ├───classifiers.py
│       ├───image_processor.py
└───tests/
    ├───test_application_controller.py
    ├───test_camera.py
    ├───test_classifiers.py
    ├───test_image_processor.py
    └───test_serial_manager.py
```

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd BandaCV
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the application, execute the `main.py` script:

```bash
python main.py
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License.
