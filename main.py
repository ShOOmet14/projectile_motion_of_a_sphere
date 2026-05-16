import sys

from PySide6.QtWidgets import QApplication

from config.settings import get_stylesheet, load_theme
from gui.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet(get_stylesheet(load_theme()))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
