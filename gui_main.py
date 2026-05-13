import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    directory = Path(__file__).resolve().parent
    style_path = directory / "style" / "style.css"

    with open(style_path, "r", encoding="utf-8") as file:
        app.setStyleSheet(file.read())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
