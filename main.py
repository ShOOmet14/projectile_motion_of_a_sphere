import sys

from PySide6.QtWidgets import QApplication

from config.app_settings import load_theme
from config.theme import get_stylesheet
from gui.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet(get_stylesheet(load_theme()))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
