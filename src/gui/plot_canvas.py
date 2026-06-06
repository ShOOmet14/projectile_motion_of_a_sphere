"""Display static projectile-motion comparison plots inside Qt widgets."""

from math import cos, sin
from typing import Literal

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget

from src.config.parameters import Parameters
from src.simulation.solve import ProjectileResult


FIGURE_SIZE: tuple[float, float] = (8.0, 5.0)
FIGURE_DPI: int = 100

_ResultArrayKey = Literal[
    "t",
    "x",
    "y",
    "v",
    "E",
]


def _get_wind_arrow_end(
    parameters: Parameters,
    start_x: float,
    start_y: float,
    length: float,
) -> tuple[float, float]:
    """Return the end point of a normalized wind-direction arrow."""

    dx = length * cos(parameters.wind_angle_radians)
    dy = length * sin(parameters.wind_angle_radians)

    return start_x + dx, start_y + dy


def _format_wind_label(parameters: Parameters) -> str:
    """Return a compact label describing wind speed and direction."""

    return (
        f"Wind: {parameters.wind_speed:.1f} m/s, {parameters.wind_angle_degrees:.0f}°"
    )


class PlotCanvas(QWidget):
    """Display one static Matplotlib comparison plot inside a Qt widget."""

    def __init__(
        self,
        title: str,
        x_label: str,
        y_label: str,
    ) -> None:
        """Create an initially empty plot canvas with the supplied labels."""

        super().__init__()

        self.title = title
        self.x_label = x_label
        self.y_label = y_label

        layout = QVBoxLayout()

        self.figure = Figure(
            figsize=FIGURE_SIZE,
            dpi=FIGURE_DPI,
        )

        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axis = self.figure.add_subplot(111)

        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.show_empty_plot()

    def show_empty_plot(self) -> None:
        """Clear the axis and display an empty formatted plot."""

        self.axis.clear()

        self._apply_axis_formatting(
            include_legend=False,
        )

        self._redraw()

    def finish_plot(self) -> None:
        """Apply formatting and redraw a completed comparison plot."""

        self._apply_axis_formatting(
            include_legend=True,
        )

        self._redraw()

    def _apply_axis_formatting(
        self,
        *,
        include_legend: bool,
    ) -> None:
        """Apply labels, grid visibility, and an optional legend."""

        self.axis.set_title(self.title)
        self.axis.set_xlabel(self.x_label)
        self.axis.set_ylabel(self.y_label)

        if include_legend:
            self.axis.legend()

        self.axis.grid(True)

    def _redraw(self) -> None:
        """Update the layout and schedule a canvas redraw."""

        self.figure.tight_layout()
        self.canvas.draw_idle()

    def _draw_comparison_lines(
        self,
        no_drag: ProjectileResult,
        linear_drag: ProjectileResult,
        quadratic_drag: ProjectileResult,
        *,
        x_key: _ResultArrayKey,
        y_key: _ResultArrayKey,
    ) -> None:
        """Draw one comparison line for each projectile-motion model."""

        self.axis.plot(
            no_drag[x_key],
            no_drag[y_key],
            label="No drag",
            color="red",
        )

        self.axis.plot(
            linear_drag[x_key],
            linear_drag[y_key],
            label="Linear drag",
            color="blue",
        )

        self.axis.plot(
            quadratic_drag[x_key],
            quadratic_drag[y_key],
            label="Quadratic drag RK4",
            color="green",
        )

    def plot_trajectory_comparison(
        self,
        no_drag: ProjectileResult,
        linear_drag: ProjectileResult,
        quadratic_drag: ProjectileResult,
        parameters: Parameters,
        show_vectors: bool,
    ) -> None:
        """Display trajectories for all three projectile-motion models."""

        self.axis.clear()

        self._draw_comparison_lines(
            no_drag,
            linear_drag,
            quadratic_drag,
            x_key="x",
            y_key="y",
        )

        if show_vectors:
            self.draw_wind_vector(parameters)

        self.finish_plot()

    def plot_energy_comparison(
        self,
        no_drag: ProjectileResult,
        linear_drag: ProjectileResult,
        quadratic_drag: ProjectileResult,
    ) -> None:
        """Display mechanical energy over time for all three models."""

        self.axis.clear()

        self._draw_comparison_lines(
            no_drag,
            linear_drag,
            quadratic_drag,
            x_key="t",
            y_key="E",
        )

        self.finish_plot()

    def plot_speed_comparison(
        self,
        no_drag: ProjectileResult,
        linear_drag: ProjectileResult,
        quadratic_drag: ProjectileResult,
    ) -> None:
        """Display speed over time for all three models."""

        self.axis.clear()

        self._draw_comparison_lines(
            no_drag,
            linear_drag,
            quadratic_drag,
            x_key="t",
            y_key="v",
        )

        self.finish_plot()

    def draw_wind_vector(self, parameters: Parameters) -> None:
        """Draw a normalized wind-direction arrow and label when wind is enabled."""

        if parameters.wind_speed <= 0:
            return

        start_x = 0.08
        start_y = 0.88
        length = 0.12

        end_x, end_y = _get_wind_arrow_end(
            parameters,
            start_x,
            start_y,
            length,
        )

        self.axis.annotate(
            "",
            xy=(end_x, end_y),
            xytext=(start_x, start_y),
            xycoords="axes fraction",
            arrowprops={
                "arrowstyle": "->",
                "linewidth": 2.5,
                "color": "black",
            },
        )

        self.axis.text(
            start_x,
            start_y - 0.07,
            _format_wind_label(parameters),
            transform=self.axis.transAxes,
            fontsize=9,
            bbox={
                "facecolor": "white",
                "alpha": 0.75,
                "edgecolor": "none",
            },
        )
