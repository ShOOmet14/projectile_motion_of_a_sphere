from pathlib import Path
from collections.abc import Callable
from typing import Any, cast

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from unittest.mock import Mock, call

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal
from pytest import MonkeyPatch

from src.config.parameters import Parameters
from src.visualization import export
from src.visualization.export import (
    GIF_FPS,
    GIF_FRAMES,
    FIGURE_DPI,
    FIGURE_SIZE,
    animate_projectile_motion,
    draw_wind_vector_on_axis,
    get_axis_limits,
    get_interpolated_positions,
    get_interpolated_velocities,
    get_velocity_scale,
    plot_energy,
    plot_motion,
    plot_speed,
    save_plot,
)


def make_projectile_result(offset: float = 0.0) -> dict[str, np.ndarray]:
    vx = np.array([10.0, 8.0, 6.0], dtype=np.float64) + offset
    vy = np.array([4.0, 0.0, -4.0], dtype=np.float64) + offset

    return {
        "t": np.array([0.0, 1.0, 2.0], dtype=np.float64),
        "x": np.array([0.0, 8.0, 14.0], dtype=np.float64) + offset,
        "y": np.array([0.0, 4.0, 0.0], dtype=np.float64) + offset,
        "vx": vx,
        "vy": vy,
        "v": np.hypot(vx, vy),
        "Ek": np.zeros(3, dtype=np.float64),
        "Ep": np.zeros(3, dtype=np.float64),
        "E": np.zeros(3, dtype=np.float64),
    }


def test_save_plot_writes_high_resolution_tight_figure_and_closes_it(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    figure = Mock(spec=Figure)
    close = Mock()
    monkeypatch.setattr(export.plt, "close", close)
    output_path = tmp_path / "plot.png"

    save_plot(figure, output_path)

    figure.savefig.assert_called_once_with(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )
    close.assert_called_once_with(figure)


def test_draw_wind_vector_returns_without_drawing_when_wind_is_zero() -> None:
    axis = Mock()

    draw_wind_vector_on_axis(axis, Parameters(wind_speed=0.0))

    axis.annotate.assert_not_called()
    axis.text.assert_not_called()


def test_draw_wind_vector_adds_arrow_and_formatted_label() -> None:
    axis = Mock()
    axis.transAxes = object()
    parameters = Parameters(
        wind_speed=5.25,
        wind_angle_degrees=90.0,
    )

    draw_wind_vector_on_axis(axis, parameters)

    axis.annotate.assert_called_once()
    annotate_args, annotate_kwargs = axis.annotate.call_args
    assert annotate_args == ("",)
    assert annotate_kwargs["xy"] == pytest.approx((0.78, 1.0))
    assert annotate_kwargs["xytext"] == pytest.approx((0.78, 0.88))
    assert annotate_kwargs["xycoords"] == "axes fraction"
    assert annotate_kwargs["arrowprops"] == {
        "arrowstyle": "->",
        "linewidth": 2.5,
        "color": "black",
    }

    axis.text.assert_called_once_with(
        0.78,
        0.81,
        "Wind: 5.2 m/s, 90°",
        transform=axis.transAxes,
        fontsize=9,
        bbox={
            "facecolor": "white",
            "alpha": 0.75,
            "edgecolor": "none",
        },
    )


@pytest.mark.parametrize("show_vectors", [False, True])
def test_plot_motion_configures_trajectory_plot_and_optionally_draws_vectors(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    show_vectors: bool,
) -> None:
    figure = Mock(spec=Figure)
    axis = Mock()
    subplots = Mock(return_value=(figure, axis))
    saver = Mock()
    vector_drawer = Mock()

    monkeypatch.setattr(export.plt, "subplots", subplots)
    monkeypatch.setattr(export, "save_plot", saver)
    monkeypatch.setattr(export, "draw_wind_vector_on_axis", vector_drawer)

    x_no_drag = np.array([0.0, 1.0], dtype=np.float64)
    y_no_drag = np.array([0.0, 2.0], dtype=np.float64)
    x_linear = np.array([0.0, 0.8], dtype=np.float64)
    y_linear = np.array([0.0, 1.8], dtype=np.float64)
    x_quadratic = np.array([0.0, 0.6], dtype=np.float64)
    y_quadratic = np.array([0.0, 1.6], dtype=np.float64)
    parameters = Parameters(wind_speed=2.0)
    output_path = tmp_path / "motion.png"

    plot_motion(
        x_no_drag,
        y_no_drag,
        x_linear,
        y_linear,
        x_quadratic,
        y_quadratic,
        parameters,
        show_vectors,
        output_path,
    )

    subplots.assert_called_once_with()
    assert axis.plot.call_args_list == [
        call(x_no_drag, y_no_drag, label="No drag", color="red"),
        call(x_linear, y_linear, label="Linear drag", color="blue"),
        call(
            x_quadratic,
            y_quadratic,
            label="Quadratic drag RK4",
            color="green",
        ),
    ]
    axis.set_title.assert_called_once_with("Trajectory comparison")
    axis.set_xlabel.assert_called_once_with("x [m]")
    axis.set_ylabel.assert_called_once_with("y [m]")
    axis.legend.assert_called_once_with()
    axis.grid.assert_called_once_with(True)
    saver.assert_called_once_with(figure, output_path)

    if show_vectors:
        vector_drawer.assert_called_once_with(axis, parameters)
    else:
        vector_drawer.assert_not_called()


@pytest.mark.parametrize(
    ("plotter", "title", "ylabel"),
    [
        (plot_speed, "Speed comparison", "v [m/s]"),
        (plot_energy, "Mechanical energy comparison", "E [J]"),
    ],
)
def test_plot_series_comparison_configures_three_lines_and_saves(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    plotter: Any,
    title: str,
    ylabel: str,
) -> None:
    figure = Mock(spec=Figure)
    axis = Mock()
    monkeypatch.setattr(export.plt, "subplots", Mock(return_value=(figure, axis)))
    saver = Mock()
    monkeypatch.setattr(export, "save_plot", saver)

    no_drag = np.array([1.0, 2.0], dtype=np.float64)
    linear_drag = np.array([3.0, 4.0], dtype=np.float64)
    quadratic_drag = np.array([5.0, 6.0], dtype=np.float64)
    time_no_drag = np.array([0.0, 1.0], dtype=np.float64)
    time_linear = np.array([0.0, 0.9], dtype=np.float64)
    time_quadratic = np.array([0.0, 0.8], dtype=np.float64)
    output_path = tmp_path / "comparison.png"

    plotter(
        no_drag,
        linear_drag,
        quadratic_drag,
        time_no_drag,
        time_linear,
        time_quadratic,
        output_path,
    )

    assert axis.plot.call_args_list == [
        call(time_no_drag, no_drag, label="No drag", color="red"),
        call(time_linear, linear_drag, label="Linear drag", color="blue"),
        call(
            time_quadratic,
            quadratic_drag,
            label="Quadratic drag RK4",
            color="green",
        ),
    ]
    axis.set_title.assert_called_once_with(title)
    axis.set_xlabel.assert_called_once_with("t [s]")
    axis.set_ylabel.assert_called_once_with(ylabel)
    axis.legend.assert_called_once_with()
    axis.grid.assert_called_once_with(True)
    saver.assert_called_once_with(figure, output_path)


def test_get_interpolated_positions() -> None:
    result = make_projectile_result()
    animation_time = np.array([0.0, 0.5, 1.5, 2.0], dtype=np.float64)

    x, y = get_interpolated_positions(result, animation_time)

    assert_array_equal(x, np.array([0.0, 4.0, 11.0, 14.0]))
    assert_array_equal(y, np.array([0.0, 2.0, 2.0, 0.0]))


def test_get_interpolated_velocities() -> None:
    result = make_projectile_result()
    animation_time = np.array([0.0, 0.5, 1.5, 2.0], dtype=np.float64)

    vx, vy = get_interpolated_velocities(result, animation_time)

    assert_array_equal(vx, np.array([10.0, 9.0, 7.0, 6.0]))
    assert_array_equal(vy, np.array([4.0, 2.0, -2.0, -4.0]))


def test_get_axis_limits_uses_all_results_and_applies_margins() -> None:
    no_drag = make_projectile_result()
    linear_drag = make_projectile_result(-2.0)
    quadratic_drag = make_projectile_result(3.0)

    x_min, x_max, y_min, y_max = get_axis_limits(
        no_drag,
        linear_drag,
        quadratic_drag,
    )

    assert x_min == pytest.approx(-3.14)
    assert x_max == pytest.approx(18.14)
    assert y_min == pytest.approx(-2.9)
    assert y_max == pytest.approx(7.9)


def test_get_axis_limits_uses_minimum_ranges_for_flat_results() -> None:
    result = make_projectile_result()
    result["x"] = np.array([2.0, 2.0], dtype=np.float64)
    result["y"] = np.array([0.5, 0.5], dtype=np.float64)

    x_min, x_max, y_min, y_max = get_axis_limits(result, result, result)

    assert x_min == pytest.approx(1.94)
    assert x_max == pytest.approx(2.06)
    assert y_min == pytest.approx(-0.1)
    assert y_max == pytest.approx(1.1)


def test_get_velocity_scale_uses_axis_width_and_maximum_speed() -> None:
    no_drag = make_projectile_result()
    linear_drag = make_projectile_result(-2.0)
    quadratic_drag = make_projectile_result(3.0)

    scale = get_velocity_scale(no_drag, linear_drag, quadratic_drag)

    x_min, x_max, _, _ = get_axis_limits(no_drag, linear_drag, quadratic_drag)
    maximum_speed = max(
        float(np.max(no_drag["v"])),
        float(np.max(linear_drag["v"])),
        float(np.max(quadratic_drag["v"])),
        1.0,
    )
    assert scale == pytest.approx(0.08 * (x_max - x_min) / maximum_speed)


class AnimationStub:
    instances: list["AnimationStub"] = []

    def __init__(
        self,
        figure: Figure,
        update: Any,
        frames: int,
        interval: int,
        blit: bool,
    ) -> None:
        self.figure = figure
        self.update = update
        self.frames = frames
        self.interval = interval
        self.blit = blit
        self.save_calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
        self.__class__.instances.append(self)

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.save_calls.append((args, kwargs))


@pytest.fixture
def captured_animation(
    monkeypatch: MonkeyPatch,
) -> tuple[list[tuple[Figure, Axes]], type[AnimationStub]]:
    figures: list[tuple[Figure, Axes]] = []
    original_subplots = cast(Callable[..., tuple[Figure, Axes]], plt.subplots)
    AnimationStub.instances.clear()

    def capture_subplots(*args: Any, **kwargs: Any) -> tuple[Figure, Axes]:
        figure, axis = original_subplots(*args, **kwargs)
        figures.append((figure, axis))
        return figure, axis

    monkeypatch.setattr(export.plt, "subplots", capture_subplots)
    monkeypatch.setattr(export, "FuncAnimation", AnimationStub)

    return figures, AnimationStub


def test_animate_projectile_motion_builds_and_saves_animation_without_vectors(
    tmp_path: Path,
    captured_animation: tuple[list[tuple[Figure, Any]], type[AnimationStub]],
) -> None:
    figures, animation_stub = captured_animation
    no_drag = make_projectile_result()
    linear_drag = make_projectile_result(1.0)
    quadratic_drag = make_projectile_result(2.0)
    output_path = tmp_path / "motion.gif"

    animate_projectile_motion(
        no_drag,
        linear_drag,
        quadratic_drag,
        Parameters(),
        False,
        output_path,
    )

    assert len(figures) == 1
    figure, axis = figures[0]
    assert tuple(figure.get_size_inches()) == pytest.approx(FIGURE_SIZE)
    assert figure.dpi == pytest.approx(FIGURE_DPI)
    assert len(axis.lines) == 6
    assert len(axis.patches) == 0
    assert len(axis.texts) == 1
    assert axis.get_title() == "Projectile motion animation"
    assert axis.get_xlabel() == "x [m]"
    assert axis.get_ylabel() == "y [m]"
    assert axis.get_legend() is not None

    assert len(animation_stub.instances) == 1
    animation = animation_stub.instances[0]
    assert animation.figure is figure
    assert animation.frames == GIF_FRAMES
    assert animation.interval == 1000 // GIF_FPS
    assert animation.blit is False
    assert len(animation.save_calls) == 1
    save_args, save_kwargs = animation.save_calls[0]
    assert save_args == (output_path,)
    assert save_kwargs["dpi"] == FIGURE_DPI
    assert isinstance(save_kwargs["writer"], export.PillowWriter)
    assert save_kwargs["writer"].fps == GIF_FPS


def test_animate_projectile_motion_update_moves_points_and_sets_time_text(
    tmp_path: Path,
    captured_animation: tuple[list[tuple[Figure, Any]], type[AnimationStub]],
) -> None:
    figures, animation_stub = captured_animation
    no_drag = make_projectile_result()
    linear_drag = make_projectile_result(1.0)
    quadratic_drag = make_projectile_result(2.0)

    animate_projectile_motion(
        no_drag,
        linear_drag,
        quadratic_drag,
        Parameters(),
        False,
        tmp_path / "motion.gif",
    )

    _, axis = figures[0]
    animation_stub.instances[0].update(GIF_FRAMES - 1)

    no_drag_point, linear_drag_point, quadratic_drag_point = axis.lines[3:6]
    assert_array_equal(no_drag_point.get_xdata(), [no_drag["x"][-1]])
    assert_array_equal(no_drag_point.get_ydata(), [no_drag["y"][-1]])
    assert_array_equal(linear_drag_point.get_xdata(), [linear_drag["x"][-1]])
    assert_array_equal(linear_drag_point.get_ydata(), [linear_drag["y"][-1]])
    assert_array_equal(quadratic_drag_point.get_xdata(), [quadratic_drag["x"][-1]])
    assert_array_equal(quadratic_drag_point.get_ydata(), [quadratic_drag["y"][-1]])
    assert axis.texts[0].get_text() == "t = 2.00 s"


def test_animate_projectile_motion_adds_wind_and_velocity_vectors(
    tmp_path: Path,
    captured_animation: tuple[list[tuple[Figure, Any]], type[AnimationStub]],
) -> None:
    figures, animation_stub = captured_animation
    no_drag = make_projectile_result()
    linear_drag = make_projectile_result(1.0)
    quadratic_drag = make_projectile_result(2.0)
    parameters = Parameters(
        wind_speed=5.0,
        wind_angle_degrees=90.0,
    )

    animate_projectile_motion(
        no_drag,
        linear_drag,
        quadratic_drag,
        parameters,
        True,
        tmp_path / "motion.gif",
    )

    _, axis = figures[0]
    assert len(axis.patches) == 4
    assert len(axis.texts) == 3
    assert axis.texts[1].get_text() == "Wind: 5.0 m/s, 90°"

    animation_stub.instances[0].update(GIF_FRAMES - 1)

    scale = get_velocity_scale(no_drag, linear_drag, quadratic_drag)
    expected_positions = [
        (
            (float(no_drag["x"][-1]), float(no_drag["y"][-1])),
            (
                float(no_drag["x"][-1] + no_drag["vx"][-1] * scale),
                float(no_drag["y"][-1] + no_drag["vy"][-1] * scale),
            ),
        ),
        (
            (float(linear_drag["x"][-1]), float(linear_drag["y"][-1])),
            (
                float(linear_drag["x"][-1] + linear_drag["vx"][-1] * scale),
                float(linear_drag["y"][-1] + linear_drag["vy"][-1] * scale),
            ),
        ),
        (
            (
                float(quadratic_drag["x"][-1]),
                float(quadratic_drag["y"][-1]),
            ),
            (
                float(quadratic_drag["x"][-1] + quadratic_drag["vx"][-1] * scale),
                float(quadratic_drag["y"][-1] + quadratic_drag["vy"][-1] * scale),
            ),
        ),
    ]

    for arrow, expected in zip(axis.patches[1:], expected_positions, strict=True):
        assert_allclose(arrow._posA_posB[0], expected[0])
        assert_allclose(arrow._posA_posB[1], expected[1])

    assert axis.texts[2].get_text() == (
        "Velocity components\n"
        "No drag: vx=6.00, vy=-4.00 m/s\n"
        "Linear:  vx=7.00, vy=-3.00 m/s\n"
        "Quad:    vx=8.00, vy=-2.00 m/s\n"
        "Wind:    vx=0.00, vy=5.00 m/s"
    )


def test_animate_projectile_motion_adds_velocity_vectors_without_wind_arrow(
    tmp_path: Path,
    captured_animation: tuple[list[tuple[Figure, Any]], type[AnimationStub]],
) -> None:
    figures, _ = captured_animation
    result = make_projectile_result()

    animate_projectile_motion(
        result,
        result,
        result,
        Parameters(wind_speed=0.0),
        True,
        tmp_path / "motion.gif",
    )

    _, axis = figures[0]
    assert len(axis.patches) == 3
    assert len(axis.texts) == 2
    assert all(not text.get_text().startswith("Wind:") for text in axis.texts)
