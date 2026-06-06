"""Display interactive playback for projectile-motion simulation results."""

from math import cos, sin

import numpy as np
import numpy.typing as npt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch
from matplotlib.text import Text
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.config.parameters import Parameters
from src.simulation.solve import ProjectileResult


FloatArray = npt.NDArray[np.float64]

ANIMATION_FRAMES: int = 300
ANIMATION_FPS: int = 30
TIMER_INTERVAL_MS: int = 1000 // ANIMATION_FPS

_FIGURE_SIZE: tuple[float, float] = (8.0, 5.0)
_FIGURE_DPI: int = 100

_VELOCITY_ARROW_COLORS: dict[str, str] = {
    "no_drag": "red",
    "linear_drag": "blue",
    "quadratic_drag": "green",
}


class AnimationCanvas(QWidget):
    """Display and control playback for the three projectile-motion models."""

    def __init__(self) -> None:
        """Create an empty playback canvas with disabled controls."""

        super().__init__()

        self.no_drag: ProjectileResult | None = None
        self.linear_drag: ProjectileResult | None = None
        self.quadratic_drag: ProjectileResult | None = None

        self.parameters: Parameters | None = None
        self.show_vectors = True

        self.wind_arrow: FancyArrowPatch | None = None
        self.velocity_arrows: dict[str, FancyArrowPatch] = {}
        self.velocity_text: Text | None = None
        self.velocity_scale = 1.0

        self.animation_time: FloatArray = np.array([], dtype=np.float64)
        self.frame_index = 0

        self.no_drag_point: Line2D | None = None
        self.linear_drag_point: Line2D | None = None
        self.quadratic_drag_point: Line2D | None = None
        self.time_text: Text | None = None

        self.timer = QTimer(self)
        self.timer.setInterval(TIMER_INTERVAL_MS)
        self.timer.timeout.connect(self.update_frame)

        self.figure = Figure(
            figsize=_FIGURE_SIZE,
            dpi=_FIGURE_DPI,
        )
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axis = self.figure.add_subplot(111)

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.reset_button = QPushButton("Reset")

        self._set_button_states(
            start_enabled=False,
            stop_enabled=False,
            reset_enabled=False,
        )

        self.start_button.clicked.connect(self.start_animation)
        self.stop_button.clicked.connect(self.stop_animation)
        self.reset_button.clicked.connect(self.reset_animation)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.reset_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.canvas)
        main_layout.addLayout(controls_layout)

        self.setLayout(main_layout)

        self.show_empty_plot()

    def _set_button_states(
        self,
        *,
        start_enabled: bool,
        stop_enabled: bool,
        reset_enabled: bool,
    ) -> None:
        """Update playback-control availability."""

        self.start_button.setEnabled(start_enabled)
        self.stop_button.setEnabled(stop_enabled)
        self.reset_button.setEnabled(reset_enabled)

    def _redraw(self) -> None:
        """Update the figure layout and schedule a canvas redraw."""

        self.figure.tight_layout()
        self.canvas.draw_idle()

    def _apply_axis_labels(self) -> None:
        """Apply the labels shared by empty and populated playback plots."""

        self.axis.set_title("Projectile motion playback")
        self.axis.set_xlabel("x [m]")
        self.axis.set_ylabel("y [m]")
        self.axis.grid(True)

    def show_empty_plot(self) -> None:
        """Clear the canvas and display an empty formatted playback plot."""

        self.axis.clear()
        self._apply_axis_labels()
        self._redraw()

    def set_results(
        self,
        no_drag: ProjectileResult,
        linear_drag: ProjectileResult,
        quadratic_drag: ProjectileResult,
        parameters: Parameters,
        show_vectors: bool,
    ) -> None:
        """Load simulation results and reset playback to the first frame."""

        self.no_drag = no_drag
        self.linear_drag = linear_drag
        self.quadratic_drag = quadratic_drag

        self.parameters = parameters
        self.show_vectors = show_vectors

        animation_end_time = max(
            float(no_drag["t"][-1]),
            float(linear_drag["t"][-1]),
            float(quadratic_drag["t"][-1]),
        )

        self.animation_time = np.linspace(
            0.0,
            animation_end_time,
            ANIMATION_FRAMES,
            dtype=np.float64,
        )

        self.frame_index = 0
        self.timer.stop()

        self.draw_static_scene()
        self.update_points(0.0)

        self._set_button_states(
            start_enabled=True,
            stop_enabled=False,
            reset_enabled=True,
        )

    def _has_results(self) -> bool:
        """Return whether all three model results are available."""

        return (
            self.no_drag is not None
            and self.linear_drag is not None
            and self.quadratic_drag is not None
        )

    def draw_static_scene(self) -> None:
        """Draw trajectories, markers, labels, and optional vector overlays."""

        if not self._has_results():
            return

        assert self.no_drag is not None
        assert self.linear_drag is not None
        assert self.quadratic_drag is not None

        self.axis.clear()

        self.wind_arrow = None
        self.velocity_arrows = {}
        self.velocity_text = None

        self._draw_trajectory(
            self.no_drag,
            label="No drag",
            color="red",
        )
        self._draw_trajectory(
            self.linear_drag,
            label="Linear drag",
            color="blue",
        )
        self._draw_trajectory(
            self.quadratic_drag,
            label="Quadratic drag RK4",
            color="green",
        )

        self.no_drag_point = self._create_projectile_point("red")
        self.linear_drag_point = self._create_projectile_point("blue")
        self.quadratic_drag_point = self._create_projectile_point("green")

        self.time_text = self.axis.text(
            0.02,
            0.95,
            "",
            transform=self.axis.transAxes,
            fontsize=11,
            bbox={
                "facecolor": "white",
                "alpha": 0.75,
                "edgecolor": "none",
            },
        )

        x_min, x_max, y_min, y_max = self.get_axis_limits()

        self._apply_axis_labels()
        self.axis.set_xlim(x_min, x_max)
        self.axis.set_ylim(y_min, y_max)

        if self.show_vectors and self.parameters is not None:
            self.draw_static_vectors()

        self.axis.legend()
        self._redraw()

    def _draw_trajectory(
        self,
        result: ProjectileResult,
        *,
        label: str,
        color: str,
    ) -> None:
        """Draw one faded trajectory line behind its animated marker."""

        self.axis.plot(
            result["x"],
            result["y"],
            label=label,
            color=color,
            alpha=0.45,
            linewidth=2.0,
        )

    def _create_projectile_point(self, color: str) -> Line2D:
        """Create one animated projectile marker."""

        return self.axis.plot(
            [],
            [],
            "o",
            color=color,
            markersize=8,
            markeredgecolor="black",
            markeredgewidth=0.8,
            label="_nolegend_",
        )[0]

    def draw_static_vectors(self) -> None:
        """Draw wind and velocity-vector overlays when required data exists."""

        if (
            self.parameters is None
            or self.no_drag is None
            or self.linear_drag is None
            or self.quadratic_drag is None
        ):
            return

        if self.parameters.wind_speed > 0:
            self._draw_wind_vector()

        self.velocity_scale = self._calculate_velocity_scale()

        for name, color in _VELOCITY_ARROW_COLORS.items():
            arrow = FancyArrowPatch(
                (0.0, 0.0),
                (0.0, 0.0),
                arrowstyle="->",
                mutation_scale=14,
                linewidth=2.0,
                color=color,
            )

            self.axis.add_patch(arrow)
            self.velocity_arrows[name] = arrow

        self.velocity_text = self.axis.text(
            0.02,
            0.78,
            "",
            transform=self.axis.transAxes,
            fontsize=9,
            bbox={
                "facecolor": "white",
                "alpha": 0.75,
                "edgecolor": "none",
            },
        )

    def _draw_wind_vector(self) -> None:
        """Draw a normalized wind-direction arrow and label."""

        assert self.parameters is not None

        start_x = 0.78
        start_y = 0.88
        length = 0.12

        end_x, end_y = self._get_wind_arrow_end(
            start_x,
            start_y,
            length,
        )

        self.wind_arrow = FancyArrowPatch(
            (start_x, start_y),
            (end_x, end_y),
            transform=self.axis.transAxes,
            arrowstyle="->",
            mutation_scale=16,
            linewidth=2.5,
            color="black",
        )

        self.axis.add_patch(self.wind_arrow)

        self.axis.text(
            start_x,
            start_y - 0.07,
            self._format_wind_label(),
            transform=self.axis.transAxes,
            fontsize=9,
            bbox={
                "facecolor": "white",
                "alpha": 0.75,
                "edgecolor": "none",
            },
        )

    def _get_wind_arrow_end(
        self,
        start_x: float,
        start_y: float,
        length: float,
    ) -> tuple[float, float]:
        """Return the end point of a normalized wind-direction arrow."""

        assert self.parameters is not None

        dx = length * cos(self.parameters.wind_angle_radians)
        dy = length * sin(self.parameters.wind_angle_radians)

        return start_x + dx, start_y + dy

    def _format_wind_label(self) -> str:
        """Return a compact label describing wind speed and direction."""

        assert self.parameters is not None

        return (
            f"Wind: {self.parameters.wind_speed:.1f} m/s, "
            f"{self.parameters.wind_angle_degrees:.0f}°"
        )

    def _calculate_velocity_scale(self) -> float:
        """Return a visual scale factor for velocity arrows."""

        assert self.no_drag is not None
        assert self.linear_drag is not None
        assert self.quadratic_drag is not None

        x_min, x_max, _, _ = self.get_axis_limits()
        x_range = max(x_max - x_min, 1.0)

        max_speed = max(
            float(np.max(self.no_drag["v"])),
            float(np.max(self.linear_drag["v"])),
            float(np.max(self.quadratic_drag["v"])),
            1.0,
        )

        return 0.08 * x_range / max_speed

    def start_animation(self) -> None:
        """Start playback when simulation results have been loaded."""

        if len(self.animation_time) == 0:
            return

        self.timer.start()

        self._set_button_states(
            start_enabled=False,
            stop_enabled=True,
            reset_enabled=True,
        )

    def stop_animation(self) -> None:
        """Stop playback and enable the controls for restarting it."""

        self.timer.stop()

        self._set_button_states(
            start_enabled=True,
            stop_enabled=False,
            reset_enabled=True,
        )

    def reset_animation(self) -> None:
        """Stop playback and return all markers to the first frame."""

        self.timer.stop()
        self.frame_index = 0
        self.update_points(0.0)

        self._set_button_states(
            start_enabled=True,
            stop_enabled=False,
            reset_enabled=True,
        )

    def update_frame(self) -> None:
        """Advance playback by one frame or stop when the timeline ends."""

        if self.frame_index >= len(self.animation_time):
            self.timer.stop()
            self._set_button_states(
                start_enabled=True,
                stop_enabled=False,
                reset_enabled=True,
            )
            return

        current_time = float(self.animation_time[self.frame_index])
        self.update_points(current_time)

        self.frame_index += 1

    def update_points(self, current_time: float) -> None:
        """Interpolate and draw projectile state at one playback time."""

        if (
            self.no_drag is None
            or self.linear_drag is None
            or self.quadratic_drag is None
            or self.no_drag_point is None
            or self.linear_drag_point is None
            or self.quadratic_drag_point is None
            or self.time_text is None
        ):
            return

        x_no_drag, y_no_drag = self.get_interpolated_position(
            self.no_drag,
            current_time,
        )
        x_linear, y_linear = self.get_interpolated_position(
            self.linear_drag,
            current_time,
        )
        x_quadratic, y_quadratic = self.get_interpolated_position(
            self.quadratic_drag,
            current_time,
        )

        vx_no_drag, vy_no_drag = self.get_interpolated_velocity(
            self.no_drag,
            current_time,
        )
        vx_linear, vy_linear = self.get_interpolated_velocity(
            self.linear_drag,
            current_time,
        )
        vx_quadratic, vy_quadratic = self.get_interpolated_velocity(
            self.quadratic_drag,
            current_time,
        )

        self.no_drag_point.set_data([x_no_drag], [y_no_drag])
        self.linear_drag_point.set_data([x_linear], [y_linear])
        self.quadratic_drag_point.set_data([x_quadratic], [y_quadratic])

        self.time_text.set_text(f"t = {current_time:.2f} s")

        if self.show_vectors:
            self.update_velocity_arrow(
                "no_drag",
                x_no_drag,
                y_no_drag,
                vx_no_drag,
                vy_no_drag,
            )
            self.update_velocity_arrow(
                "linear_drag",
                x_linear,
                y_linear,
                vx_linear,
                vy_linear,
            )
            self.update_velocity_arrow(
                "quadratic_drag",
                x_quadratic,
                y_quadratic,
                vx_quadratic,
                vy_quadratic,
            )

            if self.velocity_text is not None:
                self.velocity_text.set_text(
                    self._format_velocity_text(
                        vx_no_drag,
                        vy_no_drag,
                        vx_linear,
                        vy_linear,
                        vx_quadratic,
                        vy_quadratic,
                    )
                )

        self.canvas.draw_idle()

    def _format_velocity_text(
        self,
        vx_no_drag: float,
        vy_no_drag: float,
        vx_linear: float,
        vy_linear: float,
        vx_quadratic: float,
        vy_quadratic: float,
    ) -> str:
        """Return formatted projectile and wind velocity components."""

        wind_vx = 0.0
        wind_vy = 0.0

        if self.parameters is not None:
            wind_vx = self.parameters.wind_vx
            wind_vy = self.parameters.wind_vy

        return (
            "Velocity components\n"
            f"No drag: vx={vx_no_drag:.2f}, vy={vy_no_drag:.2f} m/s\n"
            f"Linear:  vx={vx_linear:.2f}, vy={vy_linear:.2f} m/s\n"
            f"Quad:    vx={vx_quadratic:.2f}, vy={vy_quadratic:.2f} m/s\n"
            f"Wind:    vx={wind_vx:.2f}, vy={wind_vy:.2f} m/s"
        )

    @staticmethod
    def get_interpolated_position(
        result: ProjectileResult,
        current_time: float,
    ) -> tuple[float, float]:
        """Interpolate projectile position at one playback time."""

        x = float(np.interp(current_time, result["t"], result["x"]))
        y = float(np.interp(current_time, result["t"], result["y"]))

        return x, y

    @staticmethod
    def get_interpolated_velocity(
        result: ProjectileResult,
        current_time: float,
    ) -> tuple[float, float]:
        """Interpolate projectile velocity at one playback time."""

        vx = float(np.interp(current_time, result["t"], result["vx"]))
        vy = float(np.interp(current_time, result["t"], result["vy"]))

        return vx, vy

    def update_velocity_arrow(
        self,
        name: str,
        x: float,
        y: float,
        vx: float,
        vy: float,
    ) -> None:
        """Move one velocity arrow if it exists in the current scene."""

        arrow = self.velocity_arrows.get(name)

        if arrow is None:
            return

        arrow.set_positions(
            (x, y),
            (
                x + vx * self.velocity_scale,
                y + vy * self.velocity_scale,
            ),
        )

    def get_axis_limits(self) -> tuple[float, float, float, float]:
        """Return padded axis limits that contain all loaded trajectories."""

        if (
            self.no_drag is None
            or self.linear_drag is None
            or self.quadratic_drag is None
        ):
            return 0.0, 1.0, 0.0, 1.0

        min_x = min(
            float(np.min(self.no_drag["x"])),
            float(np.min(self.linear_drag["x"])),
            float(np.min(self.quadratic_drag["x"])),
        )

        max_x = max(
            float(np.max(self.no_drag["x"])),
            float(np.max(self.linear_drag["x"])),
            float(np.max(self.quadratic_drag["x"])),
        )

        min_y = min(
            float(np.min(self.no_drag["y"])),
            float(np.min(self.linear_drag["y"])),
            float(np.min(self.quadratic_drag["y"])),
            0.0,
        )

        max_y = max(
            float(np.max(self.no_drag["y"])),
            float(np.max(self.linear_drag["y"])),
            float(np.max(self.quadratic_drag["y"])),
            1.0,
        )

        x_range = max(max_x - min_x, 1.0)
        y_range = max(max_y - min_y, 1.0)

        x_margin = x_range * 0.06
        y_margin = y_range * 0.10

        return (
            min_x - x_margin,
            max_x + x_margin,
            min_y - y_margin,
            max_y + y_margin,
        )
