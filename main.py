import sys

from typing import NoReturn


APP_ICON_PATH = "style/icons/app_icon.svg"


def main() -> NoReturn:
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication

    from src.config.settings import get_stylesheet, load_theme
    from src.gui.main_window import MainWindow

    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(APP_ICON_PATH))
    app.setStyleSheet(get_stylesheet(load_theme()))

    window = MainWindow()
    window.setWindowIcon(QIcon(APP_ICON_PATH))
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
