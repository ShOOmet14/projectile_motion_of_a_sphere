from pathlib import Path

from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QWidget,
    QDialog,
)
from PySide6.QtGui import QCloseEvent

from gui.animation_canvas import AnimationCanvas
from gui.parameter_panel import ParameterPanel
from gui.plot_canvas import PlotCanvas
from gui.results_panel import ResultsPanel
from gui.settings_window import SettingsWindow

from simulation.solve import (
    ProjectileResult,
    solve_projectile_motion_no_drag,
    solve_projectile_motion_linear_drag,
    solve_projectile_motion_quadratic_drag,
)

from config.user_settings import load_user_settings, save_user_settings
from storage.csv_export import export_simulation_results_to_csv

from visualization.animation import animate_projectile_motion
from visualization.plots import plot_motion, plot_energy, plot_speed


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

        self.current_parameters = load_user_settings()
        self.parameter_panel = ParameterPanel(self.current_parameters)

        self.trajectory_canvas = PlotCanvas(
            title="Trajectory comparison",
            x_label="x [m]",
            y_label="y [m]",
        )

        self.animation_canvas = AnimationCanvas()

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

        self.tabs = QTabWidget()
        self.tabs.addTab(self.trajectory_canvas, "Trajectory")
        self.tabs.addTab(self.animation_canvas, "Playback")
        self.tabs.addTab(self.energy_canvas, "Energy")
        self.tabs.addTab(self.speed_canvas, "Speed")
        self.tabs.addTab(self.results_panel, "Results")

        self.parameter_panel.run_simulation_button.clicked.connect(self.run_simulation)
        self.parameter_panel.export_csv_button.clicked.connect(self.export_csv)
        self.parameter_panel.export_plots_button.clicked.connect(self.export_plots)
        self.parameter_panel.export_animation_button.clicked.connect(
            self.export_animation
        )
        self.parameter_panel.settings_button.clicked.connect(self.open_settings)

        main_layout.addWidget(self.parameter_panel)
        main_layout.addWidget(self.tabs, 1)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def run_simulation(self) -> None:
        try:
            parameters = self.parameter_panel.get_parameters()
            self.current_parameters = parameters
            save_user_settings(parameters)

            no_drag = solve_projectile_motion_no_drag(parameters)
            linear_drag = solve_projectile_motion_linear_drag(parameters)
            quadratic_drag = solve_projectile_motion_quadratic_drag(parameters)

            self.no_drag_result = no_drag
            self.linear_drag_result = linear_drag
            self.quadratic_drag_result = quadratic_drag

            self.trajectory_canvas.plot_trajectory_comparison(
                no_drag,
                linear_drag,
                quadratic_drag,
            )

            self.animation_canvas.set_results(
                no_drag,
                linear_drag,
                quadratic_drag,
            )

            self.energy_canvas.plot_energy_comparison(
                no_drag,
                linear_drag,
                quadratic_drag,
            )

            self.speed_canvas.plot_speed_comparison(
                no_drag,
                linear_drag,
                quadratic_drag,
            )

            self.results_panel.set_results(
                no_drag,
                linear_drag,
                quadratic_drag,
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Simulation error",
                str(error),
            )

    def has_simulation_results(self) -> bool:
        return (
            self.no_drag_result is not None
            and self.linear_drag_result is not None
            and self.quadratic_drag_result is not None
        )

    def export_csv(self) -> None:
        if not self.has_simulation_results():
            QMessageBox.warning(
                self,
                "Export error",
                "Run simulation before exporting CSV files.",
            )
            return

        assert self.no_drag_result is not None
        assert self.linear_drag_result is not None
        assert self.quadratic_drag_result is not None

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

    def export_plots(self) -> None:
        if not self.has_simulation_results():
            QMessageBox.warning(
                self,
                "Export error",
                "Run simulation before exporting plots.",
            )
            return

        assert self.no_drag_result is not None
        assert self.linear_drag_result is not None
        assert self.quadratic_drag_result is not None

        plots_directory = Path("results") / "plots"
        plots_directory.mkdir(parents=True, exist_ok=True)

        plot_motion(
            self.no_drag_result["x"],
            self.no_drag_result["y"],
            self.linear_drag_result["x"],
            self.linear_drag_result["y"],
            self.quadratic_drag_result["x"],
            self.quadratic_drag_result["y"],
            plots_directory / "trajectory_comparison.png",
        )

        plot_energy(
            self.no_drag_result["E"],
            self.linear_drag_result["E"],
            self.quadratic_drag_result["E"],
            self.no_drag_result["t"],
            self.linear_drag_result["t"],
            self.quadratic_drag_result["t"],
            plots_directory / "energy_comparison.png",
        )

        plot_speed(
            self.no_drag_result["v"],
            self.linear_drag_result["v"],
            self.quadratic_drag_result["v"],
            self.no_drag_result["t"],
            self.linear_drag_result["t"],
            self.quadratic_drag_result["t"],
            plots_directory / "speed_comparison.png",
        )

        QMessageBox.information(
            self,
            "Export complete",
            "Plots saved to results/plots/.",
        )

    def export_animation(self) -> None:
        if not self.has_simulation_results():
            QMessageBox.warning(
                self,
                "Export error",
                "Run simulation before exporting animation.",
            )
            return

        assert self.no_drag_result is not None
        assert self.linear_drag_result is not None
        assert self.quadratic_drag_result is not None

        animations_directory = Path("results") / "animations"
        animations_directory.mkdir(parents=True, exist_ok=True)

        animate_projectile_motion(
            self.no_drag_result,
            self.linear_drag_result,
            self.quadratic_drag_result,
            animations_directory / "projectile_motion.gif",
        )

        QMessageBox.information(
            self,
            "Export complete",
            "Animation saved to results/animations/projectile_motion.gif.",
        )

    def open_settings(self) -> None:
        current_parameters = self.parameter_panel.get_parameters()

        settings_window = SettingsWindow(current_parameters)

        if settings_window.exec() == QDialog.DialogCode.Accepted:
            updated_parameters = settings_window.get_updated_parameters(
                current_parameters
            )

            self.current_parameters = updated_parameters
            self.parameter_panel.set_parameters(updated_parameters)
            save_user_settings(updated_parameters)

    def closeEvent(self, event: QCloseEvent) -> None:
        parameters = self.parameter_panel.get_parameters()
        save_user_settings(parameters)

        super().closeEvent(event)
