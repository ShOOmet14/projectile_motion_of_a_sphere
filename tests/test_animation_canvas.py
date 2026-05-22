import pytest
from pytestqt.qtbot import QtBot

import numpy as np

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from src.gui.animation_canvas import AnimationCanvas, TIMER_INTERVAL_MS


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
