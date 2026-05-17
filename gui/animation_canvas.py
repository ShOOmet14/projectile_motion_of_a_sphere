from math import cos, pi, sin

import numpy as np
import numpy.typing as npt

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch
from matplotlib.text import Text

from config.parameters import Parameters
from simulation.solve import ProjectileResult


ANIMATION_FRAMES = 300
ANIMATION_FPS = 30
TIMER_INTERVAL_MS = 1000 // ANIMATION_FPS


class AnimationCanvas(QWidget):
    def __init__(self) -> None:
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

        self.animation_time: npt.NDArray[np.float64] = np.array(
            [],
            dtype=np.float64,
        )
        self.frame_index = 0

        self.no_drag_point: Line2D | None = None
        self.linear_drag_point: Line2D | None = None
        self.quadratic_drag_point: Line2D | None = None
        self.time_text: Text | None = None

        self.timer = QTimer()
        self.timer.setInterval(TIMER_INTERVAL_MS)
        self.timer.timeout.connect(self.update_frame)

        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axis = self.figure.add_subplot(111)

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.reset_button = QPushButton("Reset")

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.reset_button.setEnabled(False)

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

    def show_empty_plot(self) -> None:
        self.axis.clear()

        self.axis.set_title("Projectile motion playback")
        self.axis.set_xlabel("x [m]")
        self.axis.set_ylabel("y [m]")
        self.axis.grid(True)

        self.figure.tight_layout()
        self.canvas.draw_idle()

    def set_results(
        self,
        no_drag: ProjectileResult,
        linear_drag: ProjectileResult,
        quadratic_drag: ProjectileResult,
        parameters: Parameters,
        show_vectors: bool,
    ) -> None:
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

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.reset_button.setEnabled(True)

    def draw_static_scene(self) -> None:
        if (
            self.no_drag is None
            or self.linear_drag is None
            or self.quadratic_drag is None
        ):
            return

        self.axis.clear()

        self.wind_arrow = None
        self.velocity_arrows = {}
        self.velocity_text = None

        self.axis.plot(
            self.no_drag["x"],
            self.no_drag["y"],
            label="No drag",
            color="red",
            alpha=0.45,
            linewidth=2.0,
        )

        self.axis.plot(
            self.linear_drag["x"],
            self.linear_drag["y"],
            label="Linear drag",
            color="blue",
            alpha=0.45,
            linewidth=2.0,
        )

        self.axis.plot(
            self.quadratic_drag["x"],
            self.quadratic_drag["y"],
            label="Quadratic drag RK4",
            color="green",
            alpha=0.45,
            linewidth=2.0,
        )

        self.no_drag_point = self.axis.plot(
            [],
            [],
            "o",
            color="red",
            markersize=8,
            markeredgecolor="black",
            markeredgewidth=0.8,
            label="_nolegend_",
        )[0]

        self.linear_drag_point = self.axis.plot(
            [],
            [],
            "o",
            color="blue",
            markersize=8,
            markeredgecolor="black",
            markeredgewidth=0.8,
            label="_nolegend_",
        )[0]

        self.quadratic_drag_point = self.axis.plot(
            [],
            [],
            "o",
            color="green",
            markersize=8,
            markeredgecolor="black",
            markeredgewidth=0.8,
            label="_nolegend_",
        )[0]

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

        self.axis.set_title("Projectile motion playback")
        self.axis.set_xlabel("x [m]")
        self.axis.set_ylabel("y [m]")
        self.axis.set_xlim(x_min, x_max)
        self.axis.set_ylim(y_min, y_max)

        if self.show_vectors and self.parameters is not None:
            self.draw_static_vectors()

        self.axis.legend()
        self.axis.grid(True)

        self.figure.tight_layout()
        self.canvas.draw_idle()

    def draw_static_vectors(self) -> None:
        if (
            self.parameters is None
            or self.no_drag is None
            or self.linear_drag is None
            or self.quadratic_drag is None
        ):
            return

        if self.parameters.wind_speed > 0:
            angle_rad = self.parameters.wind_angle_deg * pi / 180.0

            start_x = 0.78
            start_y = 0.88
            length = 0.12

            dx = length * cos(angle_rad)
            dy = length * sin(angle_rad)

            self.wind_arrow = FancyArrowPatch(
                (start_x, start_y),
                (start_x + dx, start_y + dy),
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
                (
                    f"Wind: {self.parameters.wind_speed:.1f} m/s, "
                    f"{self.parameters.wind_angle_deg:.0f}°"
                ),
                transform=self.axis.transAxes,
                fontsize=9,
                bbox={
                    "facecolor": "white",
                    "alpha": 0.75,
                    "edgecolor": "none",
                },
            )

        x_min, x_max, _, _ = self.get_axis_limits()
        x_range = max(x_max - x_min, 1.0)

        max_speed = max(
            float(np.max(self.no_drag["v"])),
            float(np.max(self.linear_drag["v"])),
            float(np.max(self.quadratic_drag["v"])),
            1.0,
        )

        self.velocity_scale = 0.08 * x_range / max_speed

        arrow_data = {
            "no_drag": "red",
            "linear_drag": "blue",
            "quadratic_drag": "green",
        }

        for name, color in arrow_data.items():
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

    def start_animation(self) -> None:
        if len(self.animation_time) == 0:
            return

        self.timer.start()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.reset_button.setEnabled(True)

    def stop_animation(self) -> None:
        self.timer.stop()

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.reset_button.setEnabled(True)

    def reset_animation(self) -> None:
        self.timer.stop()
        self.frame_index = 0
        self.update_points(0.0)

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.reset_button.setEnabled(True)

    def update_frame(self) -> None:
        if self.frame_index >= len(self.animation_time):
            self.timer.stop()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            return

        current_time = float(self.animation_time[self.frame_index])
        self.update_points(current_time)

        self.frame_index += 1

    def update_points(self, current_time: float) -> None:
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
                wind_vx = 0.0
                wind_vy = 0.0

                if self.parameters is not None:
                    wind_vx = self.parameters.wind_vx
                    wind_vy = self.parameters.wind_vy

                self.velocity_text.set_text(
                    "Velocity components\n"
                    f"No drag: vx={vx_no_drag:.2f}, vy={vy_no_drag:.2f} m/s\n"
                    f"Linear:  vx={vx_linear:.2f}, vy={vy_linear:.2f} m/s\n"
                    f"Quad:    vx={vx_quadratic:.2f}, vy={vy_quadratic:.2f} m/s\n"
                    f"Wind:    vx={wind_vx:.2f}, vy={wind_vy:.2f} m/s"
                )

        self.canvas.draw_idle()

    def get_interpolated_position(
        self,
        result: ProjectileResult,
        current_time: float,
    ) -> tuple[float, float]:
        x = float(np.interp(current_time, result["t"], result["x"]))
        y = float(np.interp(current_time, result["t"], result["y"]))

        return x, y

    def get_interpolated_velocity(
        self,
        result: ProjectileResult,
        current_time: float,
    ) -> tuple[float, float]:
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
