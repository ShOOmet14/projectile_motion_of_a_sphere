from unittest.mock import Mock

import numpy as np
import pytest
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch
from pytestqt.qtbot import QtBot
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout

from src.config.parameters import Parameters
from src.gui.animation_canvas import (
    ANIMATION_FRAMES,
    TIMER_INTERVAL_MS,
    AnimationCanvas,
)
from src.simulation.solve import ProjectileResult


_ARROW_NAMES = frozenset(
    {
        "no_drag",
        "linear_drag",
        "quadratic_drag",
    }
)


@pytest.fixture
def canvas(qtbot: QtBot) -> AnimationCanvas:
    widget = AnimationCanvas()
    qtbot.addWidget(widget)

    return widget


def make_projectile_result(final_time: float) -> ProjectileResult:
    return {
        "t": np.array([0.0, final_time], dtype=np.float64),
        "x": np.array([0.0, 10.0], dtype=np.float64),
        "y": np.array([0.0, 5.0], dtype=np.float64),
        "vx": np.array([10.0, 10.0], dtype=np.float64),
        "vy": np.array([5.0, 0.0], dtype=np.float64),
        "v": np.array([11.0, 10.0], dtype=np.float64),
        "Ek": np.array([60.5, 50.0], dtype=np.float64),
        "Ep": np.array([0.0, 49.0], dtype=np.float64),
        "E": np.array([60.5, 99.0], dtype=np.float64),
    }


def load_canvas_with_results(
    canvas: AnimationCanvas,
    *,
    show_vectors: bool = False,
    parameters: Parameters | None = None,
) -> None:
    canvas.set_results(
        no_drag=make_projectile_result(1.0),
        linear_drag=make_projectile_result(2.0),
        quadratic_drag=make_projectile_result(3.0),
        parameters=parameters or Parameters(),
        show_vectors=show_vectors,
    )


def get_point_coordinates(point: Line2D) -> tuple[float, float]:
    x_data, y_data = point.get_data()

    x_values = np.asarray(x_data, dtype=np.float64)
    y_values = np.asarray(y_data, dtype=np.float64)

    return float(x_values[0]), float(y_values[0])


def assert_grid_is_visible(canvas: AnimationCanvas) -> None:
    assert any(line.get_visible() for line in canvas.axis.get_xgridlines())
    assert any(line.get_visible() for line in canvas.axis.get_ygridlines())


def test_animation_canvas_initialization(canvas: AnimationCanvas) -> None:
    assert canvas.no_drag is None
    assert canvas.linear_drag is None
    assert canvas.quadratic_drag is None

    assert canvas.parameters is None
    assert canvas.show_vectors is True

    assert canvas.wind_arrow is None
    assert canvas.velocity_arrows == {}
    assert canvas.velocity_scale == 1.0

    assert isinstance(canvas.animation_time, np.ndarray)
    assert canvas.animation_time.dtype == np.float64
    assert canvas.animation_time.size == 0
    assert canvas.frame_index == 0

    assert canvas.no_drag_point is None
    assert canvas.linear_drag_point is None
    assert canvas.quadratic_drag_point is None
    assert canvas.time_text is None

    assert isinstance(canvas.timer, QTimer)
    assert canvas.timer.interval() == TIMER_INTERVAL_MS
    assert not canvas.timer.isActive()

    assert isinstance(canvas.figure, Figure)
    assert isinstance(canvas.canvas, FigureCanvasQTAgg)
    assert canvas.axis in canvas.figure.axes
    assert len(canvas.figure.axes) == 1

    assert isinstance(canvas.start_button, QPushButton)
    assert isinstance(canvas.stop_button, QPushButton)
    assert isinstance(canvas.reset_button, QPushButton)

    assert canvas.start_button.text() == "Start"
    assert canvas.stop_button.text() == "Stop"
    assert canvas.reset_button.text() == "Reset"

    assert not canvas.start_button.isEnabled()
    assert not canvas.stop_button.isEnabled()
    assert not canvas.reset_button.isEnabled()

    main_layout = canvas.layout()
    assert isinstance(main_layout, QVBoxLayout)
    assert main_layout.count() == 2

    first_item = main_layout.itemAt(0)
    second_item = main_layout.itemAt(1)

    assert first_item is not None
    assert second_item is not None
    assert first_item.widget() is canvas.canvas

    controls_layout = second_item.layout()
    assert isinstance(controls_layout, QHBoxLayout)
    assert controls_layout.count() == 3


def test_show_empty_plot_resets_axis(canvas: AnimationCanvas) -> None:
    canvas.axis.plot([0.0, 1.0], [0.0, 1.0])

    canvas.show_empty_plot()

    assert len(canvas.axis.lines) == 0
    assert canvas.axis.get_title() == "Projectile motion playback"
    assert canvas.axis.get_xlabel() == "x [m]"
    assert canvas.axis.get_ylabel() == "y [m]"
    assert_grid_is_visible(canvas)


@pytest.mark.parametrize(
    ("show_vectors", "expected_arrow_names"),
    [
        (False, frozenset()),
        (True, _ARROW_NAMES),
    ],
)
def test_set_results_resets_playback_and_configures_vector_overlays(
    canvas: AnimationCanvas,
    show_vectors: bool,
    expected_arrow_names: frozenset[str],
) -> None:
    no_drag = make_projectile_result(1.0)
    linear_drag = make_projectile_result(2.0)
    quadratic_drag = make_projectile_result(3.0)
    parameters = Parameters()

    canvas.timer.start()

    canvas.set_results(
        no_drag=no_drag,
        linear_drag=linear_drag,
        quadratic_drag=quadratic_drag,
        parameters=parameters,
        show_vectors=show_vectors,
    )

    assert canvas.no_drag is no_drag
    assert canvas.linear_drag is linear_drag
    assert canvas.quadratic_drag is quadratic_drag
    assert canvas.parameters is parameters
    assert canvas.show_vectors is show_vectors

    assert canvas.animation_time.dtype == np.float64
    assert canvas.animation_time.size == ANIMATION_FRAMES
    assert canvas.animation_time[0] == pytest.approx(0.0)
    assert canvas.animation_time[-1] == pytest.approx(3.0)

    assert canvas.frame_index == 0
    assert not canvas.timer.isActive()

    assert canvas.no_drag_point is not None
    assert canvas.linear_drag_point is not None
    assert canvas.quadratic_drag_point is not None
    assert canvas.time_text is not None
    assert canvas.time_text.get_text() == "t = 0.00 s"

    assert frozenset(canvas.velocity_arrows) == expected_arrow_names
    assert canvas.wind_arrow is None

    assert canvas.start_button.isEnabled()
    assert not canvas.stop_button.isEnabled()
    assert canvas.reset_button.isEnabled()


def test_draw_static_scene_returns_when_results_are_missing(
    canvas: AnimationCanvas,
) -> None:
    canvas.axis.plot([0.0, 1.0], [0.0, 1.0])

    canvas.draw_static_scene()

    assert len(canvas.axis.lines) == 1
    assert canvas.no_drag_point is None
    assert canvas.linear_drag_point is None
    assert canvas.quadratic_drag_point is None
    assert canvas.time_text is None


def test_draw_static_scene_draws_trajectories_markers_and_labels(
    canvas: AnimationCanvas,
) -> None:
    canvas.no_drag = make_projectile_result(1.0)
    canvas.linear_drag = make_projectile_result(2.0)
    canvas.quadratic_drag = make_projectile_result(3.0)
    canvas.parameters = Parameters()
    canvas.show_vectors = False

    expected_limits = canvas.get_axis_limits()

    canvas.draw_static_scene()

    assert canvas.no_drag_point is not None
    assert canvas.linear_drag_point is not None
    assert canvas.quadratic_drag_point is not None
    assert canvas.time_text is not None

    assert len(canvas.axis.lines) == 6
    assert [line.get_label() for line in canvas.axis.lines[:3]] == [
        "No drag",
        "Linear drag",
        "Quadratic drag RK4",
    ]

    assert canvas.no_drag_point.get_label() == "_nolegend_"
    assert canvas.linear_drag_point.get_label() == "_nolegend_"
    assert canvas.quadratic_drag_point.get_label() == "_nolegend_"
    assert canvas.time_text.get_text() == ""

    assert canvas.axis.get_title() == "Projectile motion playback"
    assert canvas.axis.get_xlabel() == "x [m]"
    assert canvas.axis.get_ylabel() == "y [m]"
    assert canvas.axis.get_xlim() == pytest.approx(expected_limits[:2])
    assert canvas.axis.get_ylim() == pytest.approx(expected_limits[2:])
    assert_grid_is_visible(canvas)

    legend = canvas.axis.get_legend()
    assert legend is not None
    assert [text.get_text() for text in legend.get_texts()] == [
        "No drag",
        "Linear drag",
        "Quadratic drag RK4",
    ]


def test_draw_static_vectors_returns_when_required_data_is_missing(
    canvas: AnimationCanvas,
) -> None:
    canvas.draw_static_vectors()

    assert canvas.wind_arrow is None
    assert canvas.velocity_arrows == {}
    assert len(canvas.axis.patches) == 0


def test_draw_static_vectors_draws_velocity_arrows_without_wind(
    canvas: AnimationCanvas,
) -> None:
    canvas.no_drag = make_projectile_result(1.0)
    canvas.linear_drag = make_projectile_result(2.0)
    canvas.quadratic_drag = make_projectile_result(3.0)
    canvas.parameters = Parameters(wind_speed=0.0)

    canvas.draw_static_vectors()

    assert canvas.wind_arrow is None
    assert frozenset(canvas.velocity_arrows) == _ARROW_NAMES
    assert all(
        isinstance(arrow, FancyArrowPatch) for arrow in canvas.velocity_arrows.values()
    )
    assert canvas.velocity_scale > 0.0
    assert len(canvas.axis.patches) == 3


def test_draw_static_vectors_draws_wind_arrow_and_label(
    canvas: AnimationCanvas,
) -> None:
    canvas.no_drag = make_projectile_result(1.0)
    canvas.linear_drag = make_projectile_result(2.0)
    canvas.quadratic_drag = make_projectile_result(3.0)
    canvas.parameters = Parameters(
        wind_speed=5.0,
        wind_angle_degrees=45.0,
    )

    canvas.draw_static_vectors()

    assert isinstance(canvas.wind_arrow, FancyArrowPatch)
    assert frozenset(canvas.velocity_arrows) == _ARROW_NAMES
    assert "Wind: 5.0 m/s, 45°" in [text.get_text() for text in canvas.axis.texts]
    assert len(canvas.axis.patches) == 4


def test_start_animation_does_nothing_without_results(
    canvas: AnimationCanvas,
) -> None:
    canvas.start_animation()

    assert not canvas.timer.isActive()
    assert not canvas.start_button.isEnabled()
    assert not canvas.stop_button.isEnabled()
    assert not canvas.reset_button.isEnabled()


def test_start_stop_and_reset_animation_update_control_states(
    canvas: AnimationCanvas,
) -> None:
    load_canvas_with_results(canvas)

    canvas.start_animation()

    assert canvas.timer.isActive()
    assert not canvas.start_button.isEnabled()
    assert canvas.stop_button.isEnabled()
    assert canvas.reset_button.isEnabled()

    canvas.stop_animation()

    assert not canvas.timer.isActive()
    assert canvas.start_button.isEnabled()
    assert not canvas.stop_button.isEnabled()
    assert canvas.reset_button.isEnabled()

    canvas.frame_index = 10
    canvas.start_animation()
    canvas.reset_animation()

    assert not canvas.timer.isActive()
    assert canvas.frame_index == 0
    assert canvas.time_text is not None
    assert canvas.time_text.get_text() == "t = 0.00 s"


def test_update_frame_updates_points_and_increments_index(
    canvas: AnimationCanvas,
) -> None:
    load_canvas_with_results(canvas)

    canvas.update_frame()

    assert canvas.frame_index == 1
    assert canvas.time_text is not None
    assert canvas.time_text.get_text() == "t = 0.00 s"

    assert canvas.no_drag_point is not None
    assert get_point_coordinates(canvas.no_drag_point) == pytest.approx((0.0, 0.0))


def test_update_frame_stops_when_timeline_is_finished(
    canvas: AnimationCanvas,
) -> None:
    load_canvas_with_results(canvas)
    canvas.start_animation()
    canvas.frame_index = len(canvas.animation_time)

    canvas.update_frame()

    assert not canvas.timer.isActive()
    assert canvas.start_button.isEnabled()
    assert not canvas.stop_button.isEnabled()
    assert canvas.reset_button.isEnabled()


def test_update_points_returns_when_required_data_is_missing(
    canvas: AnimationCanvas,
) -> None:
    canvas.update_points(0.5)

    assert canvas.no_drag_point is None
    assert canvas.linear_drag_point is None
    assert canvas.quadratic_drag_point is None
    assert canvas.time_text is None


def test_update_points_interpolates_markers_and_time_text(
    canvas: AnimationCanvas,
) -> None:
    load_canvas_with_results(canvas)

    canvas.update_points(0.5)

    assert canvas.no_drag_point is not None
    assert canvas.linear_drag_point is not None
    assert canvas.quadratic_drag_point is not None
    assert canvas.time_text is not None

    assert get_point_coordinates(canvas.no_drag_point) == pytest.approx((5.0, 2.5))
    assert get_point_coordinates(canvas.linear_drag_point) == pytest.approx((2.5, 1.25))
    assert get_point_coordinates(canvas.quadratic_drag_point) == pytest.approx(
        (1.6666666667, 0.8333333333)
    )
    assert canvas.time_text.get_text() == "t = 0.50 s"


def test_get_interpolated_position() -> None:
    result = make_projectile_result(2.0)

    x, y = AnimationCanvas.get_interpolated_position(result, 0.5)

    assert x == pytest.approx(2.5)
    assert y == pytest.approx(1.25)


def test_get_interpolated_velocity() -> None:
    result = make_projectile_result(2.0)

    vx, vy = AnimationCanvas.get_interpolated_velocity(result, 1.0)

    assert vx == pytest.approx(10.0)
    assert vy == pytest.approx(2.5)


def test_update_velocity_arrow_returns_when_arrow_does_not_exist(
    canvas: AnimationCanvas,
) -> None:
    canvas.update_velocity_arrow(
        name="missing_arrow",
        x=1.0,
        y=2.0,
        vx=3.0,
        vy=4.0,
    )

    assert canvas.velocity_arrows == {}


def test_update_velocity_arrow_sets_positions(
    canvas: AnimationCanvas,
) -> None:
    arrow = Mock(spec=FancyArrowPatch)
    canvas.velocity_arrows["test"] = arrow
    canvas.velocity_scale = 0.5

    canvas.update_velocity_arrow(
        name="test",
        x=2.0,
        y=3.0,
        vx=4.0,
        vy=6.0,
    )

    arrow.set_positions.assert_called_once_with(
        (2.0, 3.0),
        (4.0, 6.0),
    )


def test_get_axis_limits_returns_defaults_without_results(
    canvas: AnimationCanvas,
) -> None:
    assert canvas.get_axis_limits() == (
        0.0,
        1.0,
        0.0,
        1.0,
    )


def test_get_axis_limits_uses_all_results_with_margins(
    canvas: AnimationCanvas,
) -> None:
    canvas.no_drag = make_projectile_result(1.0)
    canvas.linear_drag = make_projectile_result(1.0)
    canvas.quadratic_drag = make_projectile_result(1.0)

    canvas.linear_drag["x"] = np.array([-2.0, 8.0], dtype=np.float64)
    canvas.linear_drag["y"] = np.array([-1.0, 4.0], dtype=np.float64)
    canvas.quadratic_drag["x"] = np.array([1.0, 12.0], dtype=np.float64)
    canvas.quadratic_drag["y"] = np.array([0.0, 7.0], dtype=np.float64)

    x_min, x_max, y_min, y_max = canvas.get_axis_limits()

    assert x_min == pytest.approx(-2.84)
    assert x_max == pytest.approx(12.84)
    assert y_min == pytest.approx(-1.8)
    assert y_max == pytest.approx(7.8)
