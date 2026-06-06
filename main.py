"""Start the projectile-motion desktop application."""

import sys
from pathlib import Path
from typing import NoReturn

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.config.settings import get_stylesheet, load_theme
from src.gui.main_window import MainWindow


APP_ICON_PATH: Path = (
    Path(__file__).resolve().parent / "style" / "icons" / "app_icon.svg"
)


def main() -> NoReturn:
    """Create the Qt application, show its main window, and start the event loop."""

    application = QApplication(sys.argv)

    icon = QIcon(str(APP_ICON_PATH))
    application.setWindowIcon(icon)

    theme = load_theme()
    application.setStyleSheet(get_stylesheet(theme))

    window = MainWindow()
    window.setWindowIcon(icon)
    window.showMaximized()

    sys.exit(application.exec())


if __name__ == "__main__":
    main()
