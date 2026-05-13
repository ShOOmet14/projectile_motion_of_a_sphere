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
from matplotlib.text import Text

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
    ) -> None:
        self.no_drag = no_drag
        self.linear_drag = linear_drag
        self.quadratic_drag = quadratic_drag

        self.animation_time = np.linspace(
            0.0,
            float(no_drag["t"][-1]),
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

        max_x = max(
            float(np.max(self.no_drag["x"])),
            float(np.max(self.linear_drag["x"])),
            float(np.max(self.quadratic_drag["x"])),
        )

        max_y = max(
            float(np.max(self.no_drag["y"])),
            float(np.max(self.linear_drag["y"])),
            float(np.max(self.quadratic_drag["y"])),
        )

        self.axis.set_title("Projectile motion playback")
        self.axis.set_xlabel("x [m]")
        self.axis.set_ylabel("y [m]")
        self.axis.set_xlim(0.0, max_x * 1.05)
        self.axis.set_ylim(0.0, max_y * 1.10)
        self.axis.legend()
        self.axis.grid(True)

        self.figure.tight_layout()
        self.canvas.draw_idle()

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

        self.no_drag_point.set_data([x_no_drag], [y_no_drag])
        self.linear_drag_point.set_data([x_linear], [y_linear])
        self.quadratic_drag_point.set_data([x_quadratic], [y_quadratic])

        self.time_text.set_text(f"t = {current_time:.2f} s")

        self.canvas.draw_idle()

    def get_interpolated_position(
        self,
        result: ProjectileResult,
        current_time: float,
    ) -> tuple[float, float]:
        x = float(np.interp(current_time, result["t"], result["x"]))
        y = float(np.interp(current_time, result["t"], result["y"]))

        return x, y
