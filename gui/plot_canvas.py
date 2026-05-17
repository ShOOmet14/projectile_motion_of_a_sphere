from math import cos, sin, pi

from PySide6.QtWidgets import QVBoxLayout, QWidget

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from simulation.solve import ProjectileResult
from config.parameters import Parameters


class PlotCanvas(QWidget):
    def __init__(self, title: str, x_label: str, y_label: str) -> None:
        super().__init__()

        self.title = title
        self.x_label = x_label
        self.y_label = y_label

        layout = QVBoxLayout()

        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axis = self.figure.add_subplot(111)

        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.show_empty_plot()

    def show_empty_plot(self) -> None:
        self.axis.clear()

        self.axis.set_title(self.title)
        self.axis.set_xlabel(self.x_label)
        self.axis.set_ylabel(self.y_label)
        self.axis.grid(True)

        self.figure.tight_layout()
        self.canvas.draw_idle()

    def finish_plot(self) -> None:
        self.axis.set_title(self.title)
        self.axis.set_xlabel(self.x_label)
        self.axis.set_ylabel(self.y_label)

        self.axis.legend()
        self.axis.grid(True)

        self.figure.tight_layout()
        self.canvas.draw_idle()

    def plot_trajectory_comparison(
        self,
        no_drag: ProjectileResult,
        linear_drag: ProjectileResult,
        quadratic_drag: ProjectileResult,
        parameters: Parameters,
        show_vectors: bool,
    ) -> None:
        self.axis.clear()

        self.axis.plot(
            no_drag["x"],
            no_drag["y"],
            label="No drag",
            color="red",
        )

        self.axis.plot(
            linear_drag["x"],
            linear_drag["y"],
            label="Linear drag",
            color="blue",
        )

        self.axis.plot(
            quadratic_drag["x"],
            quadratic_drag["y"],
            label="Quadratic drag RK4",
            color="green",
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
        self.axis.clear()

        self.axis.plot(
            no_drag["t"],
            no_drag["E"],
            label="No drag",
            color="red",
        )

        self.axis.plot(
            linear_drag["t"],
            linear_drag["E"],
            label="Linear drag",
            color="blue",
        )

        self.axis.plot(
            quadratic_drag["t"],
            quadratic_drag["E"],
            label="Quadratic drag RK4",
            color="green",
        )

        self.finish_plot()

    def plot_speed_comparison(
        self,
        no_drag: ProjectileResult,
        linear_drag: ProjectileResult,
        quadratic_drag: ProjectileResult,
    ) -> None:
        self.axis.clear()

        self.axis.plot(
            no_drag["t"],
            no_drag["v"],
            label="No drag",
            color="red",
        )

        self.axis.plot(
            linear_drag["t"],
            linear_drag["v"],
            label="Linear drag",
            color="blue",
        )

        self.axis.plot(
            quadratic_drag["t"],
            quadratic_drag["v"],
            label="Quadratic drag RK4",
            color="green",
        )

        self.finish_plot()

    def draw_wind_vector(self, parameters: Parameters) -> None:
        if parameters.wind_speed <= 0:
            return

        angle_rad = parameters.wind_angle_deg * pi / 180.0

        start_x = 0.08
        start_y = 0.88
        length = 0.12

        dx = length * cos(angle_rad)
        dy = length * sin(angle_rad)

        self.axis.annotate(
            "",
            xy=(start_x + dx, start_y + dy),
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
            f"Wind: {parameters.wind_speed:.1f} m/s, {parameters.wind_angle_deg:.0f}°",
            transform=self.axis.transAxes,
            fontsize=9,
            bbox={
                "facecolor": "white",
                "alpha": 0.75,
                "edgecolor": "none",
            },
        )
