import pytest
from pytestqt.qtbot import QtBot

import numpy as np

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch

from src.gui.animation_canvas import (
    AnimationCanvas,
    TIMER_INTERVAL_MS,
    ANIMATION_FRAMES,
)
from src.config.parameters import Parameters


@pytest.fixture
def canvas(qtbot: QtBot) -> AnimationCanvas:
    widget = AnimationCanvas()
    qtbot.addWidget(widget)

    return widget


def test_animation_canvas_initialization(canvas: AnimationCanvas) -> None:
    assert canvas.no_drag is None
    assert canvas.linear_drag is None
    assert canvas.quadratic_drag is None

    assert canvas.parameters is None
    assert canvas.show_vectors is True

    assert canvas.wind_arrow is None
    assert canvas.velocity_arrows == {}
    assert canvas.velocity_text is None
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
    assert canvas.axis is not None
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
    assert first_item is not None
    assert first_item.widget() is canvas.canvas

    second_item = main_layout.itemAt(1)
    assert second_item is not None

    controls_layout = second_item.layout()
    assert isinstance(controls_layout, QHBoxLayout)
    assert controls_layout.count() == 3

    start_item = controls_layout.itemAt(0)
    stop_item = controls_layout.itemAt(1)
    reset_item = controls_layout.itemAt(2)

    assert start_item is not None
    assert stop_item is not None
    assert reset_item is not None

    assert start_item.widget() is canvas.start_button
    assert stop_item.widget() is canvas.stop_button
    assert reset_item.widget() is canvas.reset_button


def test_show_empty_plot_resets_axis(canvas: AnimationCanvas) -> None:
    canvas.axis.plot([0, 1], [0, 1])
    assert len(canvas.axis.lines) == 1

    canvas.show_empty_plot()

    assert len(canvas.axis.lines) == 0
    assert canvas.axis.get_title() == "Projectile motion playback"
    assert canvas.axis.get_xlabel() == "x [m]"
    assert canvas.axis.get_ylabel() == "y [m]"
    assert any(line.get_visible() for line in canvas.axis.get_xgridlines())
    assert any(line.get_visible() for line in canvas.axis.get_ygridlines())


# Helper function
def make_projectile_results(final_time: float):
    return {
        "t": np.array([0.0, final_time], dtype=np.float64),
        "x": np.array([0.0, 10.0], dtype=np.float64),
        "y": np.array([0.0, 5.0], dtype=np.float64),
        "vx": np.array([10.0, 10.0], dtype=np.float64),
        "vy": np.array([5.0, 0.0], dtype=np.float64),
        "v": np.array([11.0, 10.0], dtype=np.float64),
    }


@pytest.mark.parametrize(
    ("show_vectors", "expected_arrow_names", "expect_velocity_text"),
    [
        (False, frozenset[str](), False),
        (True, {"no_drag", "linear_drag", "quadratic_drag"}, True),
    ],
)
def test_set_results(
    canvas: AnimationCanvas,
    show_vectors: bool,
    expected_arrow_names: frozenset[str],
    expect_velocity_text: bool,
) -> None:
    no_drag = make_projectile_results(1.0)
    linear_drag = make_projectile_results(2.0)
    quadratic_drag = make_projectile_results(3.0)
    parameters = Parameters()

    canvas.timer.start()
    assert canvas.timer.isActive()

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

    assert isinstance(canvas.animation_time, np.ndarray)
    assert canvas.animation_time.dtype == np.float64
    assert canvas.animation_time.size == ANIMATION_FRAMES
    assert canvas.animation_time[0] == 0.0
    assert canvas.animation_time[-1] == pytest.approx(3.0)

    assert canvas.frame_index == 0
    assert not canvas.timer.isActive()

    assert canvas.no_drag_point is not None
    assert canvas.linear_drag_point is not None
    assert canvas.quadratic_drag_point is not None
    assert canvas.time_text is not None
    assert canvas.time_text.get_text() == "t = 0.00 s"

    assert set(canvas.velocity_arrows.keys()) == expected_arrow_names

    if expect_velocity_text:
        assert canvas.velocity_text is not None
    else:
        assert canvas.velocity_text is None

    assert canvas.wind_arrow is None

    assert canvas.start_button.isEnabled()
    assert not canvas.stop_button.isEnabled()
    assert canvas.reset_button.isEnabled()


def test_draw_static_scene_returns_when_results_are_missing(
    canvas: AnimationCanvas,
) -> None:
    canvas.axis.plot([0.0, 1.0], [0.0, 1.0])
    assert len(canvas.axis.lines) == 1

    canvas.draw_static_scene()

    assert len(canvas.axis.lines) == 1
    assert canvas.no_drag_point is None
    assert canvas.linear_drag_point is None
    assert canvas.quadratic_drag_point is None
    assert canvas.time_text is None


def test_draw_static_scene_draws_trajectories_and_points_without_vectors(
    canvas: AnimationCanvas,
) -> None:
    canvas.no_drag = make_projectile_results(1.0)
    canvas.linear_drag = make_projectile_results(2.0)
    canvas.quadratic_drag = make_projectile_results(3.0)
    canvas.parameters = Parameters()
    canvas.show_vectors = False

    expected_x_min, expected_x_max, expected_y_min, expected_y_max = (
        canvas.get_axis_limits()
    )

    canvas.draw_static_scene()

    assert canvas.no_drag_point is not None
    assert canvas.linear_drag_point is not None
    assert canvas.quadratic_drag_point is not None
    assert canvas.time_text is not None

    assert len(canvas.axis.lines) == 6

    trajectory_labels = [line.get_label() for line in canvas.axis.lines[:3]]

    assert trajectory_labels == [
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

    assert canvas.axis.get_xlim() == pytest.approx((expected_x_min, expected_x_max))
    assert canvas.axis.get_ylim() == pytest.approx((expected_y_min, expected_y_max))

    assert canvas.wind_arrow is None
    assert canvas.velocity_arrows == {}
    assert canvas.velocity_text is None

    legend = canvas.axis.get_legend()
    assert legend is not None

    legend_labels = [text.get_text() for text in legend.get_texts()]

    assert legend_labels == [
        "No drag",
        "Linear drag",
        "Quadratic drag RK4",
    ]

    assert any(line.get_visible() for line in canvas.axis.get_xgridlines())
    assert any(line.get_visible() for line in canvas.axis.get_ygridlines())


def test_draw_static_scene_draws_velocity_vectors_when_enabled(
    canvas: AnimationCanvas,
) -> None:
    canvas.no_drag = make_projectile_results(1.0)
    canvas.linear_drag = make_projectile_results(2.0)
    canvas.quadratic_drag = make_projectile_results(3.0)
    canvas.parameters = Parameters()
    canvas.show_vectors = True

    canvas.draw_static_scene()

    assert frozenset(canvas.velocity_arrows.keys()) == frozenset(
        {
            "no_drag",
            "linear_drag",
            "quadratic_drag",
        }
    )

    assert canvas.velocity_text is not None
    assert canvas.wind_arrow is None


def test_draw_static_vectors_returns_when_required_data_is_missing(
    canvas: AnimationCanvas,
) -> None:
    canvas.draw_static_vectors()

    assert canvas.wind_arrow is None
    assert canvas.velocity_arrows == {}
    assert canvas.velocity_text is None
    assert len(canvas.axis.patches) == 0


def test_draw_static_vectors_draws_velocity_arrows_without_wind(
    canvas: AnimationCanvas,
) -> None:
    canvas.no_drag = make_projectile_results(1.0)
    canvas.linear_drag = make_projectile_results(2.0)
    canvas.quadratic_drag = make_projectile_results(3.0)
    canvas.parameters = Parameters(wind_speed=0.0)

    expected_x_min, expected_x_max, _, _ = canvas.get_axis_limits()
    expected_x_range = max(expected_x_max - expected_x_min, 1.0)

    expected_max_speed = max(
        float(np.max(canvas.no_drag["v"])),
        float(np.max(canvas.linear_drag["v"])),
        float(np.max(canvas.quadratic_drag["v"])),
        1.0,
    )

    expected_velocity_scale = 0.08 * expected_x_range / expected_max_speed

    canvas.draw_static_vectors()

    assert canvas.wind_arrow is None

    assert frozenset(canvas.velocity_arrows.keys()) == frozenset(
        {
            "no_drag",
            "linear_drag",
            "quadratic_drag",
        }
    )

    assert all(
        isinstance(arrow, FancyArrowPatch) for arrow in canvas.velocity_arrows.values()
    )

    assert canvas.velocity_text is not None
    assert canvas.velocity_text.get_text() == ""
    assert canvas.velocity_scale == pytest.approx(expected_velocity_scale)

    assert len(canvas.axis.patches) == 3


def test_draw_static_vectors_draws_wind_arrow_when_wind_speed_is_positive(
    canvas: AnimationCanvas,
) -> None:
    canvas.no_drag = make_projectile_results(1.0)
    canvas.linear_drag = make_projectile_results(2.0)
    canvas.quadratic_drag = make_projectile_results(3.0)
    canvas.parameters = Parameters(
        wind_speed=5.0,
        wind_angle_degrees=45.0,
    )

    canvas.draw_static_vectors()

    assert isinstance(canvas.wind_arrow, FancyArrowPatch)

    assert frozenset(canvas.velocity_arrows.keys()) == frozenset(
        {
            "no_drag",
            "linear_drag",
            "quadratic_drag",
        }
    )

    assert canvas.velocity_text is not None

    texts = [text.get_text() for text in canvas.axis.texts]

    assert "Wind: 5.0 m/s, 45°" in texts

    assert len(canvas.axis.patches) == 4
