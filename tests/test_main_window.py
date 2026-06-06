from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from src.config.parameters import Parameters
from src.gui import main_window as main_window_module
from src.gui.main_window import MainWindow
from src.simulation.solve import ProjectileResult


def make_projectile_result(offset: float = 0.0) -> ProjectileResult:
    """Return a complete deterministic simulation result for GUI tests."""

    return {
        "t": np.array([0.0, 1.0], dtype=np.float64),
        "x": np.array([0.0 + offset, 10.0 + offset], dtype=np.float64),
        "y": np.array([0.0, 5.0], dtype=np.float64),
        "vx": np.array([10.0, 10.0], dtype=np.float64),
        "vy": np.array([5.0, 0.0], dtype=np.float64),
        "v": np.array([11.0, 10.0], dtype=np.float64),
        "Ek": np.array([12.0, 10.0], dtype=np.float64),
        "Ep": np.array([8.0, 5.0], dtype=np.float64),
        "E": np.array([20.0, 15.0], dtype=np.float64),
    }


@pytest.fixture
def parameters() -> Parameters:
    return Parameters(
        initial_velocity=20.0,
        initial_angle_degrees=30.0,
        initial_x=-4.0,
        initial_y=2.0,
    )


@pytest.fixture
def window(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
    parameters: Parameters,
) -> MainWindow:
    monkeypatch.setattr(
        main_window_module,
        "load_user_settings",
        Mock(return_value=parameters),
    )

    monkeypatch.setattr(
        main_window_module,
        "load_theme",
        Mock(return_value="light"),
    )

    monkeypatch.setattr(
        main_window_module,
        "save_user_settings",
        Mock(),
    )

    main_window = MainWindow()
    qtbot.addWidget(main_window)

    return main_window


@pytest.fixture
def message_boxes(
    monkeypatch: pytest.MonkeyPatch,
) -> dict[str, Mock]:
    warning = Mock()
    information = Mock()

    monkeypatch.setattr(
        main_window_module.QMessageBox,
        "warning",
        warning,
    )

    monkeypatch.setattr(
        main_window_module.QMessageBox,
        "information",
        information,
    )

    return {
        "warning": warning,
        "information": information,
    }


def store_results(
    window: MainWindow,
) -> tuple[
    ProjectileResult,
    ProjectileResult,
    ProjectileResult,
]:
    """Store and return one fake result for each simulation model."""

    no_drag = make_projectile_result(1.0)
    linear_drag = make_projectile_result(2.0)
    quadratic_drag = make_projectile_result(3.0)

    window.no_drag_result = no_drag
    window.linear_drag_result = linear_drag
    window.quadratic_drag_result = quadratic_drag

    return no_drag, linear_drag, quadratic_drag


def test_main_window_initialization(
    window: MainWindow,
    parameters: Parameters,
) -> None:
    assert window.windowTitle() == "Projectile Motion Simulator"

    assert window.no_drag_result is None
    assert window.linear_drag_result is None
    assert window.quadratic_drag_result is None

    assert window.current_parameters == parameters
    assert window.current_theme == "light"

    assert window.centralWidget() is not None
    assert window.centralWidget().objectName() == "mainContainer"

    assert window.tabs.objectName() == "mainTabs"
    assert window.tabs.count() == 5

    assert window.tabs.tabText(0) == "Trajectory"
    assert window.tabs.tabText(1) == "Energy"
    assert window.tabs.tabText(2) == "Speed"
    assert window.tabs.tabText(3) == "Playback"
    assert window.tabs.tabText(4) == "Results"


def test_has_simulation_results_returns_false_until_all_results_exist(
    window: MainWindow,
) -> None:
    result = make_projectile_result()

    assert window.has_simulation_results() is False

    window.no_drag_result = result
    assert window.has_simulation_results() is False

    window.linear_drag_result = result
    assert window.has_simulation_results() is False


def test_has_simulation_results_returns_true_when_all_results_exist(
    window: MainWindow,
) -> None:
    store_results(window)

    assert window.has_simulation_results() is True


def test_run_simulation_saves_results_and_updates_gui(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    parameters: Parameters,
) -> None:
    no_drag = make_projectile_result(1.0)
    linear_drag = make_projectile_result(2.0)
    quadratic_drag = make_projectile_result(3.0)

    save_user_settings = Mock()

    solve_no_drag = Mock(return_value=no_drag)
    solve_linear_drag = Mock(return_value=linear_drag)
    solve_quadratic_drag = Mock(return_value=quadratic_drag)

    get_parameters = Mock(return_value=parameters)
    should_show_vectors = Mock(return_value=False)

    plot_trajectory_comparison = Mock()
    animation_set_results = Mock()
    plot_energy_comparison = Mock()
    plot_speed_comparison = Mock()
    results_set_results = Mock()

    monkeypatch.setattr(
        main_window_module,
        "save_user_settings",
        save_user_settings,
    )

    monkeypatch.setattr(
        main_window_module,
        "solve_projectile_motion_no_drag",
        solve_no_drag,
    )

    monkeypatch.setattr(
        main_window_module,
        "solve_projectile_motion_linear_drag",
        solve_linear_drag,
    )

    monkeypatch.setattr(
        main_window_module,
        "solve_projectile_motion_quadratic_drag",
        solve_quadratic_drag,
    )

    monkeypatch.setattr(
        window.parameter_panel,
        "get_parameters",
        get_parameters,
    )

    monkeypatch.setattr(
        window.parameter_panel,
        "should_show_vectors",
        should_show_vectors,
    )

    monkeypatch.setattr(
        window.trajectory_canvas,
        "plot_trajectory_comparison",
        plot_trajectory_comparison,
    )

    monkeypatch.setattr(
        window.animation_canvas,
        "set_results",
        animation_set_results,
    )

    monkeypatch.setattr(
        window.energy_canvas,
        "plot_energy_comparison",
        plot_energy_comparison,
    )

    monkeypatch.setattr(
        window.speed_canvas,
        "plot_speed_comparison",
        plot_speed_comparison,
    )

    monkeypatch.setattr(
        window.results_panel,
        "set_results",
        results_set_results,
    )

    window.run_simulation()

    assert window.current_parameters == parameters

    assert window.no_drag_result is no_drag
    assert window.linear_drag_result is linear_drag
    assert window.quadratic_drag_result is quadratic_drag

    get_parameters.assert_called_once_with()
    should_show_vectors.assert_called_once_with()

    solve_no_drag.assert_called_once_with(parameters)
    solve_linear_drag.assert_called_once_with(parameters)
    solve_quadratic_drag.assert_called_once_with(parameters)

    save_user_settings.assert_called_once_with(parameters)

    plot_trajectory_comparison.assert_called_once_with(
        no_drag,
        linear_drag,
        quadratic_drag,
        parameters,
        False,
    )

    animation_set_results.assert_called_once_with(
        no_drag,
        linear_drag,
        quadratic_drag,
        parameters,
        False,
    )

    plot_energy_comparison.assert_called_once_with(
        no_drag,
        linear_drag,
        quadratic_drag,
    )

    plot_speed_comparison.assert_called_once_with(
        no_drag,
        linear_drag,
        quadratic_drag,
    )

    results_set_results.assert_called_once_with(
        no_drag,
        linear_drag,
        quadratic_drag,
    )


def test_run_simulation_shows_warning_when_parameters_are_invalid(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    message_boxes: dict[str, Mock],
) -> None:
    get_parameters = Mock(side_effect=ValueError("Bad parameters"))

    save_user_settings = Mock()

    monkeypatch.setattr(
        window.parameter_panel,
        "get_parameters",
        get_parameters,
    )

    monkeypatch.setattr(
        main_window_module,
        "save_user_settings",
        save_user_settings,
    )

    window.run_simulation()

    message_boxes["warning"].assert_called_once_with(
        window,
        "Simulation error",
        "Bad parameters",
    )

    assert window.no_drag_result is None
    assert window.linear_drag_result is None
    assert window.quadratic_drag_result is None

    save_user_settings.assert_not_called()


def test_run_simulation_does_not_save_failed_solver_parameters_or_replace_results(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    message_boxes: dict[str, Mock],
) -> None:
    existing_results = store_results(window)
    previous_parameters = window.current_parameters

    invalid_for_solver = Parameters(
        initial_velocity=50.0,
        initial_angle_degrees=90.0,
        time_step=0.1,
        time_max=0.2,
    )

    save_user_settings = Mock()

    monkeypatch.setattr(
        window.parameter_panel,
        "get_parameters",
        Mock(return_value=invalid_for_solver),
    )

    monkeypatch.setattr(
        main_window_module,
        "save_user_settings",
        save_user_settings,
    )

    monkeypatch.setattr(
        main_window_module,
        "solve_projectile_motion_no_drag",
        Mock(side_effect=ValueError("Increase parameters.t_max.")),
    )

    window.run_simulation()

    message_boxes["warning"].assert_called_once_with(
        window,
        "Simulation error",
        "Increase parameters.t_max.",
    )

    assert window.current_parameters == previous_parameters

    assert window.no_drag_result is existing_results[0]
    assert window.linear_drag_result is existing_results[1]
    assert window.quadratic_drag_result is existing_results[2]

    save_user_settings.assert_not_called()


def test_export_csv_warns_when_simulation_was_not_run(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    message_boxes: dict[str, Mock],
) -> None:
    exporter = Mock()

    monkeypatch.setattr(
        main_window_module,
        "export_simulation_results_to_csv",
        exporter,
    )

    window.export_csv()

    exporter.assert_not_called()

    message_boxes["warning"].assert_called_once_with(
        window,
        "Export error",
        "Run simulation before exporting CSV files.",
    )


def test_export_csv_exports_existing_results(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    message_boxes: dict[str, Mock],
) -> None:
    no_drag, linear_drag, quadratic_drag = store_results(window)

    exporter = Mock()

    monkeypatch.setattr(
        main_window_module,
        "export_simulation_results_to_csv",
        exporter,
    )

    window.export_csv()

    exporter.assert_called_once_with(
        no_drag,
        linear_drag,
        quadratic_drag,
        Path("results"),
    )

    message_boxes["information"].assert_called_once_with(
        window,
        "Export complete",
        "CSV files saved to results/.",
    )


def test_export_plots_warns_when_simulation_was_not_run(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    message_boxes: dict[str, Mock],
) -> None:
    plot_motion = Mock()

    monkeypatch.setattr(
        main_window_module,
        "plot_motion",
        plot_motion,
    )

    window.export_plots()

    plot_motion.assert_not_called()

    message_boxes["warning"].assert_called_once_with(
        window,
        "Export error",
        "Run simulation before exporting plots.",
    )


def test_export_plots_uses_successful_simulation_parameters(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    parameters: Parameters,
    message_boxes: dict[str, Mock],
) -> None:
    no_drag, linear_drag, quadratic_drag = store_results(window)

    window.current_parameters = parameters

    monkeypatch.chdir(tmp_path)

    plot_motion = Mock()
    plot_energy = Mock()
    plot_speed = Mock()

    monkeypatch.setattr(
        main_window_module,
        "plot_motion",
        plot_motion,
    )

    monkeypatch.setattr(
        main_window_module,
        "plot_energy",
        plot_energy,
    )

    monkeypatch.setattr(
        main_window_module,
        "plot_speed",
        plot_speed,
    )

    get_parameters = Mock(
        return_value=Parameters(
            wind_speed=99.0,
        )
    )

    should_show_vectors = Mock(return_value=True)

    monkeypatch.setattr(
        window.parameter_panel,
        "get_parameters",
        get_parameters,
    )

    monkeypatch.setattr(
        window.parameter_panel,
        "should_show_vectors",
        should_show_vectors,
    )

    window.export_plots()

    assert (tmp_path / "results" / "plots").is_dir()

    get_parameters.assert_not_called()
    should_show_vectors.assert_called_once_with()

    plot_motion.assert_called_once_with(
        no_drag["x"],
        no_drag["y"],
        linear_drag["x"],
        linear_drag["y"],
        quadratic_drag["x"],
        quadratic_drag["y"],
        parameters,
        True,
        Path("results") / "plots" / "trajectory_plot.png",
    )

    plot_energy.assert_called_once_with(
        no_drag["E"],
        linear_drag["E"],
        quadratic_drag["E"],
        no_drag["t"],
        linear_drag["t"],
        quadratic_drag["t"],
        Path("results") / "plots" / "energy_comparison.png",
    )

    plot_speed.assert_called_once_with(
        no_drag["v"],
        linear_drag["v"],
        quadratic_drag["v"],
        no_drag["t"],
        linear_drag["t"],
        quadratic_drag["t"],
        Path("results") / "plots" / "speed_comparison.png",
    )

    message_boxes["information"].assert_called_once()


def test_export_animation_warns_when_simulation_was_not_run(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    message_boxes: dict[str, Mock],
) -> None:
    animate = Mock()

    monkeypatch.setattr(
        main_window_module,
        "animate_projectile_motion",
        animate,
    )

    window.export_animation()

    animate.assert_not_called()

    message_boxes["warning"].assert_called_once_with(
        window,
        "Export error",
        "Run simulation before exporting animation.",
    )


def test_export_animation_uses_successful_simulation_parameters(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    parameters: Parameters,
    message_boxes: dict[str, Mock],
) -> None:
    no_drag, linear_drag, quadratic_drag = store_results(window)

    window.current_parameters = parameters

    monkeypatch.chdir(tmp_path)

    animate = Mock()

    monkeypatch.setattr(
        main_window_module,
        "animate_projectile_motion",
        animate,
    )

    get_parameters = Mock(
        return_value=Parameters(
            wind_speed=99.0,
        )
    )

    should_show_vectors = Mock(return_value=False)

    monkeypatch.setattr(
        window.parameter_panel,
        "get_parameters",
        get_parameters,
    )

    monkeypatch.setattr(
        window.parameter_panel,
        "should_show_vectors",
        should_show_vectors,
    )

    window.export_animation()

    assert (tmp_path / "results" / "animations").is_dir()

    get_parameters.assert_not_called()
    should_show_vectors.assert_called_once_with()

    animate.assert_called_once_with(
        no_drag,
        linear_drag,
        quadratic_drag,
        parameters,
        False,
        Path("results") / "animations" / "projectile_motion.gif",
    )

    message_boxes["information"].assert_called_once()


def test_change_theme_saves_theme_and_updates_application_stylesheet(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    save_theme = Mock()
    get_stylesheet = Mock(return_value="new stylesheet")

    monkeypatch.setattr(
        main_window_module,
        "save_theme",
        save_theme,
    )

    monkeypatch.setattr(
        main_window_module,
        "get_stylesheet",
        get_stylesheet,
    )

    application = QApplication.instance()
    assert isinstance(application, QApplication)

    window.change_theme("dark")

    assert window.current_theme == "dark"

    save_theme.assert_called_once_with("dark")
    get_stylesheet.assert_called_once_with("dark")

    assert application.styleSheet() == "new stylesheet"


def test_change_theme_ignores_invalid_theme(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    save_theme = Mock()

    monkeypatch.setattr(
        main_window_module,
        "save_theme",
        save_theme,
    )

    window.current_theme = "light"

    window.change_theme("blue")

    assert window.current_theme == "light"
    save_theme.assert_not_called()


def test_change_theme_skips_stylesheet_when_qapplication_is_missing(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class ApplicationStub:
        @staticmethod
        def instance() -> object:
            return object()

    save_theme = Mock()
    get_stylesheet = Mock()

    monkeypatch.setattr(
        main_window_module,
        "QApplication",
        ApplicationStub,
    )

    monkeypatch.setattr(
        main_window_module,
        "save_theme",
        save_theme,
    )

    monkeypatch.setattr(
        main_window_module,
        "get_stylesheet",
        get_stylesheet,
    )

    window.change_theme("dark")

    assert window.current_theme == "dark"

    save_theme.assert_called_once_with("dark")
    get_stylesheet.assert_not_called()


def test_open_plots_folder_creates_directory_and_opens_it(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)

    open_url = Mock()

    monkeypatch.setattr(
        main_window_module.QDesktopServices,
        "openUrl",
        open_url,
    )

    window.open_plots_folder()

    expected_directory = tmp_path / "results" / "plots"

    assert expected_directory.is_dir()

    open_url.assert_called_once()

    opened_url = open_url.call_args.args[0]

    assert Path(opened_url.toLocalFile()).resolve() == expected_directory.resolve()


def test_open_animations_folder_creates_directory_and_opens_it(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)

    open_url = Mock()

    monkeypatch.setattr(
        main_window_module.QDesktopServices,
        "openUrl",
        open_url,
    )

    window.open_animations_folder()

    expected_directory = tmp_path / "results" / "animations"

    assert expected_directory.is_dir()

    open_url.assert_called_once()

    opened_url = open_url.call_args.args[0]

    assert Path(opened_url.toLocalFile()).resolve() == expected_directory.resolve()


def test_close_event_saves_current_gui_parameters(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    parameters: Parameters,
) -> None:
    save_user_settings = Mock()

    monkeypatch.setattr(
        main_window_module,
        "save_user_settings",
        save_user_settings,
    )

    monkeypatch.setattr(
        window.parameter_panel,
        "get_parameters",
        Mock(return_value=parameters),
    )

    event = QCloseEvent()

    window.closeEvent(event)

    save_user_settings.assert_called_once_with(parameters)


def test_close_event_falls_back_to_last_valid_parameters(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    parameters: Parameters,
) -> None:
    save_user_settings = Mock()

    window.current_parameters = parameters

    monkeypatch.setattr(
        main_window_module,
        "save_user_settings",
        save_user_settings,
    )

    monkeypatch.setattr(
        window.parameter_panel,
        "get_parameters",
        Mock(side_effect=ValueError("Too many simulation steps")),
    )

    event = QCloseEvent()

    window.closeEvent(event)

    save_user_settings.assert_called_once_with(parameters)
