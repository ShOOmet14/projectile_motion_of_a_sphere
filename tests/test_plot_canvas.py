from typing import Literal
from unittest.mock import Mock

import numpy as np
import pytest
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.text import Annotation
from pytestqt.qtbot import QtBot
from PySide6.QtWidgets import QVBoxLayout

from src.config.parameters import Parameters
from src.gui.plot_canvas import PlotCanvas
from src.simulation.solve import ProjectileResult


TITLE = "Projectile trajectories"
X_LABEL = "x [m]"
Y_LABEL = "y [m]"

_ComparisonKey = Literal[
    "t",
    "x",
    "y",
    "v",
    "E",
]


@pytest.fixture
def canvas(qtbot: QtBot) -> PlotCanvas:
    widget = PlotCanvas(
        TITLE,
        X_LABEL,
        Y_LABEL,
    )

    qtbot.addWidget(widget)

    return widget


def make_projectile_result(multiplier: float) -> ProjectileResult:
    return {
        "t": np.array(
            [0.0, 1.0, 2.0],
            dtype=np.float64,
        ),
        "x": multiplier
        * np.array(
            [0.0, 4.0, 8.0],
            dtype=np.float64,
        ),
        "y": multiplier
        * np.array(
            [0.0, 3.0, 0.0],
            dtype=np.float64,
        ),
        "vx": multiplier
        * np.array(
            [4.0, 4.0, 4.0],
            dtype=np.float64,
        ),
        "vy": multiplier
        * np.array(
            [3.0, 0.0, -3.0],
            dtype=np.float64,
        ),
        "v": multiplier
        * np.array(
            [5.0, 4.0, 5.0],
            dtype=np.float64,
        ),
        "Ek": multiplier
        * np.array(
            [25.0, 16.0, 25.0],
            dtype=np.float64,
        ),
        "Ep": multiplier
        * np.array(
            [0.0, 12.0, 0.0],
            dtype=np.float64,
        ),
        "E": multiplier
        * np.array(
            [25.0, 28.0, 25.0],
            dtype=np.float64,
        ),
    }


def assert_grid_is_visible(canvas: PlotCanvas) -> None:
    assert any(line.get_visible() for line in canvas.axis.get_xgridlines())

    assert any(line.get_visible() for line in canvas.axis.get_ygridlines())


def assert_finished_plot(canvas: PlotCanvas) -> None:
    assert canvas.axis.get_title() == TITLE
    assert canvas.axis.get_xlabel() == X_LABEL
    assert canvas.axis.get_ylabel() == Y_LABEL

    assert_grid_is_visible(canvas)

    legend = canvas.axis.get_legend()
    assert legend is not None

    labels = [text.get_text() for text in legend.get_texts()]

    assert labels == [
        "No drag",
        "Linear drag",
        "Quadratic drag RK4",
    ]


def assert_comparison_lines(
    canvas: PlotCanvas,
    results: tuple[
        ProjectileResult,
        ProjectileResult,
        ProjectileResult,
    ],
    *,
    x_key: _ComparisonKey,
    y_key: _ComparisonKey,
) -> None:
    assert len(canvas.axis.lines) == 3

    labels = [line.get_label() for line in canvas.axis.lines]

    colors = [line.get_color() for line in canvas.axis.lines]

    assert labels == [
        "No drag",
        "Linear drag",
        "Quadratic drag RK4",
    ]

    assert colors == [
        "red",
        "blue",
        "green",
    ]

    for line, result in zip(
        canvas.axis.lines,
        results,
        strict=True,
    ):
        np.testing.assert_array_equal(
            line.get_xdata(),
            result[x_key],
        )

        np.testing.assert_array_equal(
            line.get_ydata(),
            result[y_key],
        )


def test_plot_canvas_initialization(canvas: PlotCanvas) -> None:
    assert canvas.title == TITLE
    assert canvas.x_label == X_LABEL
    assert canvas.y_label == Y_LABEL

    assert isinstance(canvas.figure, Figure)
    assert isinstance(canvas.canvas, FigureCanvasQTAgg)

    assert canvas.axis in canvas.figure.axes
    assert len(canvas.figure.axes) == 1

    layout = canvas.layout()
    assert isinstance(layout, QVBoxLayout)
    assert layout.count() == 1

    canvas_item = layout.itemAt(0)
    assert canvas_item is not None
    assert canvas_item.widget() is canvas.canvas

    assert len(canvas.axis.lines) == 0
    assert canvas.axis.get_title() == TITLE
    assert canvas.axis.get_xlabel() == X_LABEL
    assert canvas.axis.get_ylabel() == Y_LABEL

    assert_grid_is_visible(canvas)


def test_show_empty_plot_resets_axis_and_redraws(
    canvas: PlotCanvas,
) -> None:
    canvas.axis.plot(
        [0.0, 1.0],
        [0.0, 1.0],
        label="temporary",
    )

    canvas.axis.set_title("temporary title")
    canvas.axis.set_xlabel("temporary x")
    canvas.axis.set_ylabel("temporary y")

    tight_layout = Mock()
    draw_idle = Mock()

    canvas.figure.tight_layout = tight_layout
    canvas.canvas.draw_idle = draw_idle

    canvas.show_empty_plot()

    assert len(canvas.axis.lines) == 0
    assert canvas.axis.get_title() == TITLE
    assert canvas.axis.get_xlabel() == X_LABEL
    assert canvas.axis.get_ylabel() == Y_LABEL

    assert_grid_is_visible(canvas)

    tight_layout.assert_called_once_with()
    draw_idle.assert_called_once_with()


def test_finish_plot_applies_formatting_adds_legend_and_redraws(
    canvas: PlotCanvas,
) -> None:
    canvas.axis.clear()

    canvas.axis.plot(
        [0.0, 1.0],
        [0.0, 1.0],
        label="Example",
    )

    tight_layout = Mock()
    draw_idle = Mock()

    canvas.figure.tight_layout = tight_layout
    canvas.canvas.draw_idle = draw_idle

    canvas.finish_plot()

    assert canvas.axis.get_title() == TITLE
    assert canvas.axis.get_xlabel() == X_LABEL
    assert canvas.axis.get_ylabel() == Y_LABEL

    assert_grid_is_visible(canvas)

    legend = canvas.axis.get_legend()
    assert legend is not None

    labels = [text.get_text() for text in legend.get_texts()]

    assert labels == ["Example"]

    tight_layout.assert_called_once_with()
    draw_idle.assert_called_once_with()


def test_plot_trajectory_comparison_draws_expected_lines_without_vectors(
    canvas: PlotCanvas,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    no_drag = make_projectile_result(1.0)
    linear_drag = make_projectile_result(2.0)
    quadratic_drag = make_projectile_result(3.0)
    parameters = Parameters()

    canvas.axis.plot(
        [99.0],
        [99.0],
        label="stale",
    )

    vector_drawer = Mock()

    monkeypatch.setattr(
        canvas,
        "draw_wind_vector",
        vector_drawer,
    )

    canvas.plot_trajectory_comparison(
        no_drag=no_drag,
        linear_drag=linear_drag,
        quadratic_drag=quadratic_drag,
        parameters=parameters,
        show_vectors=False,
    )

    assert_comparison_lines(
        canvas,
        (
            no_drag,
            linear_drag,
            quadratic_drag,
        ),
        x_key="x",
        y_key="y",
    )

    assert_finished_plot(canvas)

    vector_drawer.assert_not_called()


def test_plot_trajectory_comparison_draws_wind_vector_when_enabled(
    canvas: PlotCanvas,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    no_drag = make_projectile_result(1.0)
    linear_drag = make_projectile_result(2.0)
    quadratic_drag = make_projectile_result(3.0)

    parameters = Parameters(
        wind_speed=4.0,
        wind_angle_degrees=30.0,
    )

    vector_drawer = Mock()

    monkeypatch.setattr(
        canvas,
        "draw_wind_vector",
        vector_drawer,
    )

    canvas.plot_trajectory_comparison(
        no_drag=no_drag,
        linear_drag=linear_drag,
        quadratic_drag=quadratic_drag,
        parameters=parameters,
        show_vectors=True,
    )

    assert_comparison_lines(
        canvas,
        (
            no_drag,
            linear_drag,
            quadratic_drag,
        ),
        x_key="x",
        y_key="y",
    )

    assert_finished_plot(canvas)

    vector_drawer.assert_called_once_with(parameters)


@pytest.mark.parametrize(
    (
        "method_name",
        "y_key",
    ),
    [
        (
            "plot_energy_comparison",
            "E",
        ),
        (
            "plot_speed_comparison",
            "v",
        ),
    ],
)
def test_time_series_comparison_draws_expected_lines(
    canvas: PlotCanvas,
    method_name: str,
    y_key: _ComparisonKey,
) -> None:
    no_drag = make_projectile_result(1.0)
    linear_drag = make_projectile_result(2.0)
    quadratic_drag = make_projectile_result(3.0)

    canvas.axis.plot(
        [99.0],
        [99.0],
        label="stale",
    )

    plot_method = getattr(
        canvas,
        method_name,
    )

    plot_method(
        no_drag=no_drag,
        linear_drag=linear_drag,
        quadratic_drag=quadratic_drag,
    )

    assert_comparison_lines(
        canvas,
        (
            no_drag,
            linear_drag,
            quadratic_drag,
        ),
        x_key="t",
        y_key=y_key,
    )

    assert_finished_plot(canvas)


def test_draw_wind_vector_returns_when_wind_is_zero(
    canvas: PlotCanvas,
) -> None:
    canvas.draw_wind_vector(
        Parameters(
            wind_speed=0.0,
        )
    )

    assert len(canvas.axis.texts) == 0


def test_draw_wind_vector_adds_arrow_and_label(
    canvas: PlotCanvas,
) -> None:
    canvas.draw_wind_vector(
        Parameters(
            wind_speed=6.25,
            wind_angle_degrees=90.0,
        )
    )

    annotations = [text for text in canvas.axis.texts if isinstance(text, Annotation)]

    labels = [text for text in canvas.axis.texts if not isinstance(text, Annotation)]

    assert len(annotations) == 1
    assert len(labels) == 1

    annotation = annotations[0]
    label = labels[0]

    assert annotation.get_text() == ""
    assert annotation.xy == pytest.approx((0.08, 1.0))

    assert annotation.get_position() == pytest.approx((0.08, 0.88))

    assert annotation.xycoords == "axes fraction"

    assert annotation.arrow_patch is not None
    assert annotation.arrow_patch.get_linewidth() == pytest.approx(2.5)

    assert label.get_text() == "Wind: 6.2 m/s, 90°"

    assert label.get_position() == pytest.approx((0.08, 0.81))

    assert label.get_transform() is canvas.axis.transAxes
    assert label.get_fontsize() == pytest.approx(9.0)

    bbox = label.get_bbox_patch()
    assert bbox is not None
    assert bbox.get_alpha() == pytest.approx(0.75)
