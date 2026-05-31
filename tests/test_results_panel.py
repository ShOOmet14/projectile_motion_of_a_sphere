import numpy as np
from pytestqt.qtbot import QtBot

from PySide6.QtWidgets import QLabel, QPlainTextEdit, QVBoxLayout

from src.gui.results_panel import ResultsPanel
from src.simulation.solve import ProjectileResult


def make_projectile_result(multiplier: float = 1.0) -> ProjectileResult:
    return {
        "t": np.array([0.0, 1.234, 2.3456], dtype=np.float64) * multiplier,
        "x": np.array([0.0, 4.0, 12.345], dtype=np.float64) * multiplier,
        "y": np.array([0.0, 5.678, 1.0], dtype=np.float64) * multiplier,
        "vx": np.array([8.0, 3.0, 6.0], dtype=np.float64) * multiplier,
        "vy": np.array([6.0, -1.0, -4.0], dtype=np.float64) * multiplier,
        "v": np.array([10.5, 3.333, 8.999], dtype=np.float64) * multiplier,
        "E": np.array([100.5, 80.1, 66.666], dtype=np.float64) * multiplier,
    }


def test_results_panel_initialization(qtbot: QtBot) -> None:
    panel = ResultsPanel()
    qtbot.addWidget(panel)

    assert isinstance(panel.title_label, QLabel)
    assert panel.title_label.text() == "Results"
    assert panel.title_label.property("class") == "h1"

    assert isinstance(panel.results_text, QPlainTextEdit)
    assert panel.results_text.isReadOnly()
    assert panel.results_text.placeholderText() == (
        "Run simulation to display results here."
    )
    assert panel.results_text.toPlainText() == ""

    layout = panel.layout()
    assert isinstance(layout, QVBoxLayout)
    assert layout.count() == 2

    title_item = layout.itemAt(0)
    results_item = layout.itemAt(1)

    assert title_item is not None
    assert results_item is not None
    assert title_item.widget() is panel.title_label
    assert results_item.widget() is panel.results_text


def test_format_result_returns_expected_summary(qtbot: QtBot) -> None:
    panel = ResultsPanel()
    qtbot.addWidget(panel)

    result = panel.format_result("Example model", make_projectile_result())

    assert result == (
        "Example model:\n"
        "Flight time: 2.35 s\n"
        "Range: 12.35 m\n"
        "Max height: 5.68 m\n"
        "Initial speed: 10.50 m/s\n"
        "Min speed: 3.33 m/s\n"
        "Final speed: 9.00 m/s\n"
        "Initial energy: 100.50 J\n"
        "Final energy: 66.67 J"
    )


def test_set_results_displays_all_models_separated_by_blank_lines(
    qtbot: QtBot,
) -> None:
    panel = ResultsPanel()
    qtbot.addWidget(panel)

    no_drag = make_projectile_result(1.0)
    linear_drag = make_projectile_result(2.0)
    quadratic_drag = make_projectile_result(3.0)

    panel.set_results(
        no_drag=no_drag,
        linear_drag=linear_drag,
        quadratic_drag=quadratic_drag,
    )

    expected_text = "\n\n".join(
        (
            panel.format_result("No drag", no_drag),
            panel.format_result("Linear drag", linear_drag),
            panel.format_result("Quadratic drag RK4", quadratic_drag),
        )
    )

    assert panel.results_text.toPlainText() == expected_text
