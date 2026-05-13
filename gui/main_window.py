from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QWidget,
)

from gui.parameter_panel import ParameterPanel
from gui.plot_canvas import PlotCanvas
from gui.results_panel import ResultsPanel
from gui.animation_canvas import AnimationCanvas

from storage.csv_export import export_simulation_results_to_csv

from simulation.solve import (
    ProjectileResult,
    solve_projectile_motion_no_drag,
    solve_projectile_motion_linear_drag,
    solve_projectile_motion_quadratic_drag,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Projectile Motion Simulator")
        self.resize(1400, 850)

        self.no_drag_result: ProjectileResult | None = None
        self.linear_drag_result: ProjectileResult | None = None
        self.quadratic_drag_result: ProjectileResult | None = None

        central_widget = QWidget()
        main_layout = QHBoxLayout()

        self.parameter_panel = ParameterPanel()

        self.trajectory_canvas = PlotCanvas(
            title="Trajectory comparison",
            x_label="x [m]",
            y_label="y [m]",
        )

        self.energy_canvas = PlotCanvas(
            title="Mechanical energy comparison",
            x_label="t [s]",
            y_label="E [J]",
        )

        self.speed_canvas = PlotCanvas(
            title="Speed comparison",
            x_label="t [s]",
            y_label="v [m/s]",
        )

        self.results_panel = ResultsPanel()
        self.animation_canvas = AnimationCanvas()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.trajectory_canvas, "Trajectory")
        self.tabs.addTab(self.animation_canvas, "Playback")
        self.tabs.addTab(self.energy_canvas, "Energy")
        self.tabs.addTab(self.speed_canvas, "Speed")
        self.tabs.addTab(self.results_panel, "Results")

        self.parameter_panel.run_simulation_button.clicked.connect(self.run_simulation)

        self.parameter_panel.export_csv_button.clicked.connect(self.export_csv)

        main_layout.addWidget(self.parameter_panel)
        main_layout.addWidget(self.tabs, 1)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def run_simulation(self) -> None:
        try:
            parameters = self.parameter_panel.get_parameters()

            self.no_drag_result = solve_projectile_motion_no_drag(parameters)
            self.linear_drag_result = solve_projectile_motion_linear_drag(parameters)
            self.quadratic_drag_result = solve_projectile_motion_quadratic_drag(
                parameters
            )

            self.trajectory_canvas.plot_trajectory_comparison(
                self.no_drag_result,
                self.linear_drag_result,
                self.quadratic_drag_result,
            )

            self.animation_canvas.set_results(
                self.no_drag_result,
                self.linear_drag_result,
                self.quadratic_drag_result,
            )

            self.energy_canvas.plot_energy_comparison(
                self.no_drag_result,
                self.linear_drag_result,
                self.quadratic_drag_result,
            )

            self.speed_canvas.plot_speed_comparison(
                self.no_drag_result,
                self.linear_drag_result,
                self.quadratic_drag_result,
            )

            self.results_panel.set_results(
                self.no_drag_result,
                self.linear_drag_result,
                self.quadratic_drag_result,
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Simulation error",
                str(error),
            )

    def export_csv(self) -> None:
        if (
            self.no_drag_result is None
            or self.linear_drag_result is None
            or self.quadratic_drag_result is None
        ):
            QMessageBox.warning(
                self,
                "Export error",
                "Run simulation before exporting CSV files.",
            )
            return

        export_simulation_results_to_csv(
            self.no_drag_result,
            self.linear_drag_result,
            self.quadratic_drag_result,
            "results",
        )

        QMessageBox.information(
            self,
            "Export complete",
            "CSV files saved to results/.",
        )
