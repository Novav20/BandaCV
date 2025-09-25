import sys
from PyQt6.QtWidgets import QApplication
from src.config.config import AppConfig
from src.core.application_controller import ApplicationController
from src.gui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    config = AppConfig()
    controller = ApplicationController(config)
    main_window = MainWindow(controller)
    main_window.showMaximized()

    sys.exit(app.exec())
