import runpy
import sys

from dataclasses import dataclass
from types import ModuleType
from unittest.mock import Mock, call

import pytest
from pytest import MonkeyPatch

import main as application_entry_point


@dataclass
class StartupDoubles:
    application_factory: Mock
    app: Mock
    icon_factory: Mock
    app_icon: object
    window_icon: object
    load_theme: Mock
    get_stylesheet: Mock
    window_factory: Mock
    window: Mock


def install_startup_doubles(
    monkeypatch: MonkeyPatch,
    exit_code: int = 0,
) -> StartupDoubles:
    app = Mock()
    app.exec.return_value = exit_code
    application_factory = Mock(return_value=app)

    app_icon = object()
    window_icon = object()
    icon_factory = Mock(side_effect=[app_icon, window_icon])

    load_theme = Mock(return_value="dark")
    get_stylesheet = Mock(return_value="stylesheet")

    window = Mock()
    window_factory = Mock(return_value=window)

    pyside_module = ModuleType("PySide6")
    qt_gui_module = ModuleType("PySide6.QtGui")
    qt_widgets_module = ModuleType("PySide6.QtWidgets")
    settings_module = ModuleType("src.config.settings")
    main_window_module = ModuleType("src.gui.main_window")

    setattr(qt_gui_module, "QIcon", icon_factory)
    setattr(qt_widgets_module, "QApplication", application_factory)
    setattr(settings_module, "load_theme", load_theme)
    setattr(settings_module, "get_stylesheet", get_stylesheet)
    setattr(main_window_module, "MainWindow", window_factory)

    monkeypatch.setitem(sys.modules, "PySide6", pyside_module)
    monkeypatch.setitem(sys.modules, "PySide6.QtGui", qt_gui_module)
    monkeypatch.setitem(sys.modules, "PySide6.QtWidgets", qt_widgets_module)
    monkeypatch.setitem(sys.modules, "src.config.settings", settings_module)
    monkeypatch.setitem(sys.modules, "src.gui.main_window", main_window_module)

    return StartupDoubles(
        application_factory=application_factory,
        app=app,
        icon_factory=icon_factory,
        app_icon=app_icon,
        window_icon=window_icon,
        load_theme=load_theme,
        get_stylesheet=get_stylesheet,
        window_factory=window_factory,
        window=window,
    )


def test_main_configures_application_shows_window_and_exits(
    monkeypatch: MonkeyPatch,
) -> None:
    doubles = install_startup_doubles(monkeypatch, exit_code=17)
    arguments = ["main.py", "--example"]
    monkeypatch.setattr(sys, "argv", arguments)

    with pytest.raises(SystemExit) as error:
        application_entry_point.main()

    assert error.value.code == 17

    doubles.application_factory.assert_called_once_with(arguments)
    assert doubles.icon_factory.call_args_list == [
        call(application_entry_point.APP_ICON_PATH),
        call(application_entry_point.APP_ICON_PATH),
    ]

    doubles.load_theme.assert_called_once_with()
    doubles.get_stylesheet.assert_called_once_with("dark")

    doubles.app.setWindowIcon.assert_called_once_with(doubles.app_icon)
    doubles.app.setStyleSheet.assert_called_once_with("stylesheet")

    doubles.window_factory.assert_called_once_with()
    doubles.window.setWindowIcon.assert_called_once_with(doubles.window_icon)
    doubles.window.showMaximized.assert_called_once_with()

    doubles.app.exec.assert_called_once_with()


def test_script_entry_point_calls_main(monkeypatch: MonkeyPatch) -> None:
    doubles = install_startup_doubles(monkeypatch, exit_code=23)

    entry_point_path = application_entry_point.__file__
    assert entry_point_path is not None

    with pytest.raises(SystemExit) as error:
        runpy.run_path(
            entry_point_path,
            run_name="__main__",
        )

    assert error.value.code == 23
    doubles.application_factory.assert_called_once_with(sys.argv)
    doubles.window_factory.assert_called_once_with()
    doubles.app.exec.assert_called_once_with()
