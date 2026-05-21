import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.config.settings import get_stylesheet, load_theme
from src.gui.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon("style/icons/app_icon.svg"))
    app.setStyleSheet(get_stylesheet(load_theme()))

    window = MainWindow()
    window.setWindowIcon(QIcon("style/icons/app_icon.svg"))
    window.showMaximized()

    sys.exit(app.exec())
