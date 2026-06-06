"""Test application startup without creating a real QApplication instance."""

import runpy
import sys
from dataclasses import dataclass
from unittest.mock import Mock

import pytest
from PySide6 import QtGui, QtWidgets
from pytest import MonkeyPatch

import main as application_entry_point
from src.config import settings
from src.gui import main_window


@dataclass
class StartupDoubles:
    """Store the test doubles used during application startup."""

    application_factory: Mock
    application: Mock
    icon_factory: Mock
    icon: object
    load_theme: Mock
    get_stylesheet: Mock
    window_factory: Mock
    window: Mock


def install_startup_doubles(
    monkeypatch: MonkeyPatch,
    exit_code: int = 0,
) -> StartupDoubles:
    """Replace application-startup dependencies with isolated test doubles."""

    application = Mock()
    application.exec.return_value = exit_code

    application_factory = Mock(return_value=application)

    icon = object()

    icon_factory = Mock(return_value=icon)

    load_theme = Mock(return_value="dark")

    get_stylesheet = Mock(return_value="stylesheet")

    window = Mock()

    window_factory = Mock(return_value=window)

    # Patch names already imported and stored inside main.py.
    # These patches are used when calling application_entry_point.main()
    # directly.
    monkeypatch.setattr(
        application_entry_point,
        "QApplication",
        application_factory,
    )

    monkeypatch.setattr(
        application_entry_point,
        "QIcon",
        icon_factory,
    )

    monkeypatch.setattr(
        application_entry_point,
        "load_theme",
        load_theme,
    )

    monkeypatch.setattr(
        application_entry_point,
        "get_stylesheet",
        get_stylesheet,
    )

    monkeypatch.setattr(
        application_entry_point,
        "MainWindow",
        window_factory,
    )

    # Patch the original modules as well.
    # These patches are used when runpy executes main.py as a fresh script.
    monkeypatch.setattr(
        QtWidgets,
        "QApplication",
        application_factory,
    )

    monkeypatch.setattr(
        QtGui,
        "QIcon",
        icon_factory,
    )

    monkeypatch.setattr(
        settings,
        "load_theme",
        load_theme,
    )

    monkeypatch.setattr(
        settings,
        "get_stylesheet",
        get_stylesheet,
    )

    monkeypatch.setattr(
        main_window,
        "MainWindow",
        window_factory,
    )

    return StartupDoubles(
        application_factory=application_factory,
        application=application,
        icon_factory=icon_factory,
        icon=icon,
        load_theme=load_theme,
        get_stylesheet=get_stylesheet,
        window_factory=window_factory,
        window=window,
    )


def test_app_icon_path_points_to_existing_file() -> None:
    assert application_entry_point.APP_ICON_PATH.is_file()


def test_main_configures_application_shows_window_and_exits(
    monkeypatch: MonkeyPatch,
) -> None:
    doubles = install_startup_doubles(
        monkeypatch,
        exit_code=17,
    )

    arguments = [
        "main.py",
        "--example",
    ]

    monkeypatch.setattr(
        sys,
        "argv",
        arguments,
    )

    with pytest.raises(SystemExit) as error:
        application_entry_point.main()

    assert error.value.code == 17

    doubles.application_factory.assert_called_once_with(arguments)

    doubles.icon_factory.assert_called_once_with(
        str(application_entry_point.APP_ICON_PATH)
    )

    doubles.load_theme.assert_called_once_with()

    doubles.get_stylesheet.assert_called_once_with("dark")

    doubles.application.setWindowIcon.assert_called_once_with(doubles.icon)

    doubles.application.setStyleSheet.assert_called_once_with("stylesheet")

    doubles.window_factory.assert_called_once_with()

    doubles.window.setWindowIcon.assert_called_once_with(doubles.icon)

    doubles.window.showMaximized.assert_called_once_with()

    doubles.application.exec.assert_called_once_with()


def test_script_entry_point_calls_main(
    monkeypatch: MonkeyPatch,
) -> None:
    doubles = install_startup_doubles(
        monkeypatch,
        exit_code=23,
    )

    entry_point_path = application_entry_point.__file__

    assert entry_point_path is not None

    with pytest.raises(SystemExit) as error:
        runpy.run_path(
            entry_point_path,
            run_name="__main__",
        )

    assert error.value.code == 23

    doubles.application_factory.assert_called_once_with(sys.argv)

    doubles.icon_factory.assert_called_once_with(
        str(application_entry_point.APP_ICON_PATH)
    )

    doubles.window_factory.assert_called_once_with()

    doubles.application.exec.assert_called_once_with()
