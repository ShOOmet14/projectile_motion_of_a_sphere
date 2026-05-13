from PySide6.QtWidgets import QVBoxLayout, QWidget

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from simulation.solve import ProjectileResult


class PlotCanvas(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout()

        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axis = self.figure.add_subplot(111)

        layout.addWidget(self.canvas)

        self.setLayout(layout)

        self.show_empty_plot()

    def show_empty_plot(self) -> None:
        self.axis.clear()

        self.axis.set_title("Trajectory comparison")
        self.axis.set_xlabel("x [m]")
        self.axis.set_ylabel("y [m]")
        self.axis.grid(True)

        self.canvas.draw()

    def plot_trajectory_comparison(
        self,
        no_drag: ProjectileResult,
        linear_drag: ProjectileResult,
        quadratic_drag: ProjectileResult,
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

        self.axis.set_title("Trajectory comparison")
        self.axis.set_xlabel("x [m]")
        self.axis.set_ylabel("y [m]")

        self.axis.legend()
        self.axis.grid(True)

        self.figure.tight_layout()
        self.canvas.draw()
