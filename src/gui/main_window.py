"""Coordinate the projectile-motion GUI, simulations, exports, and settings."""

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QCloseEvent, QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QWidget,
)

from src.config.parameters import Parameters
from src.config.settings import (
    ThemeName,
    get_stylesheet,
    is_theme_name,
    load_theme,
    load_user_settings,
    save_theme,
    save_user_settings,
)
from src.gui.animation_canvas import AnimationCanvas
from src.gui.parameter_panel import ParameterPanel
from src.gui.plot_canvas import PlotCanvas
from src.gui.results_panel import ResultsPanel
from src.simulation.solve import (
    ProjectileResult,
    solve_projectile_motion_linear_drag,
    solve_projectile_motion_no_drag,
    solve_projectile_motion_quadratic_drag,
)
from src.storage.csv_export import export_simulation_results_to_csv
from src.visualization.export import (
    animate_projectile_motion,
    plot_energy,
    plot_motion,
    plot_speed,
)


_RESULTS_DIRECTORY = Path("results")
_PLOTS_DIRECTORY = _RESULTS_DIRECTORY / "plots"
_ANIMATIONS_DIRECTORY = _RESULTS_DIRECTORY / "animations"

SimulationResults = tuple[
    ProjectileResult,
    ProjectileResult,
    ProjectileResult,
]


class MainWindow(QMainWindow):
    """Coordinate simulation controls, result views, exports, and settings."""

    def __init__(self) -> None:
        """Create the application window and connect all GUI actions."""

        super().__init__()

        self.setWindowTitle("Projectile Motion Simulator")
        self.resize(1400, 850)

        self.no_drag_result: ProjectileResult | None = None
        self.linear_drag_result: ProjectileResult | None = None
        self.quadratic_drag_result: ProjectileResult | None = None

        self.current_parameters = load_user_settings()
        self.current_theme: ThemeName = load_theme()

        self.parameter_panel = ParameterPanel(
            self.current_parameters,
            self.current_theme,
        )

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

        self.animation_canvas = AnimationCanvas()
        self.results_panel = ResultsPanel()

        self.tabs = self._create_tabs()
        self._connect_signals()

        central_widget = QWidget()
        central_widget.setObjectName("mainContainer")

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.parameter_panel)
        main_layout.addWidget(self.tabs, 1)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def _create_tabs(self) -> QTabWidget:
        """Create the tab container for plots, playback, and text results."""

        tabs = QTabWidget()
        tabs.setObjectName("mainTabs")

        tabs.addTab(self.trajectory_canvas, "Trajectory")
        tabs.addTab(self.energy_canvas, "Energy")
        tabs.addTab(self.speed_canvas, "Speed")
        tabs.addTab(self.animation_canvas, "Playback")
        tabs.addTab(self.results_panel, "Results")

        return tabs

    def _connect_signals(self) -> None:
        """Connect parameter-panel controls to their window-level actions."""

        self.parameter_panel.run_simulation_button.clicked.connect(self.run_simulation)

        self.parameter_panel.export_csv_button.clicked.connect(self.export_csv)

        self.parameter_panel.export_plots_button.clicked.connect(self.export_plots)

        self.parameter_panel.export_animation_button.clicked.connect(
            self.export_animation
        )

        self.parameter_panel.theme_input.currentTextChanged.connect(self.change_theme)

        self.parameter_panel.open_plots_folder_button.clicked.connect(
            self.open_plots_folder
        )

        self.parameter_panel.open_animations_folder_button.clicked.connect(
            self.open_animations_folder
        )

    def run_simulation(self) -> None:
        """Run all motion models and update every result view."""

        try:
            parameters = self.parameter_panel.get_parameters()
            show_vectors = self.parameter_panel.should_show_vectors()

            results = (
                solve_projectile_motion_no_drag(parameters),
                solve_projectile_motion_linear_drag(parameters),
                solve_projectile_motion_quadratic_drag(parameters),
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Simulation error",
                str(error),
            )

            return

        self.current_parameters = parameters
        save_user_settings(parameters)

        self._store_results(results)

        self._update_result_views(
            results,
            parameters,
            show_vectors,
        )

    def _store_results(self, results: SimulationResults) -> None:
        """Store the latest successful result from each simulation model."""

        (
            self.no_drag_result,
            self.linear_drag_result,
            self.quadratic_drag_result,
        ) = results

    def _update_result_views(
        self,
        results: SimulationResults,
        parameters: Parameters,
        show_vectors: bool,
    ) -> None:
        """Refresh plots, playback data, and text summaries."""

        no_drag, linear_drag, quadratic_drag = results

        self.trajectory_canvas.plot_trajectory_comparison(
            no_drag,
            linear_drag,
            quadratic_drag,
            parameters,
            show_vectors,
        )

        self.animation_canvas.set_results(
            no_drag,
            linear_drag,
            quadratic_drag,
            parameters,
            show_vectors,
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

    def _get_simulation_results(self) -> SimulationResults | None:
        """Return all model results when a simulation has completed."""

        if (
            self.no_drag_result is None
            or self.linear_drag_result is None
            or self.quadratic_drag_result is None
        ):
            return None

        return (
            self.no_drag_result,
            self.linear_drag_result,
            self.quadratic_drag_result,
        )

    def has_simulation_results(self) -> bool:
        """Return whether results for all three models are available."""

        return self._get_simulation_results() is not None

    def _require_simulation_results(
        self,
        warning_message: str,
    ) -> SimulationResults | None:
        """Return model results or show an export warning when they are missing."""

        results = self._get_simulation_results()

        if results is None:
            QMessageBox.warning(
                self,
                "Export error",
                warning_message,
            )

        return results

    def export_csv(self) -> None:
        """Export the latest simulation results as CSV files."""

        results = self._require_simulation_results(
            "Run simulation before exporting CSV files."
        )

        if results is None:
            return

        export_simulation_results_to_csv(
            *results,
            _RESULTS_DIRECTORY,
        )

        QMessageBox.information(
            self,
            "Export complete",
            "CSV files saved to results/.",
        )

    def export_plots(self) -> None:
        """Export static trajectory, energy, and speed comparison plots."""

        results = self._require_simulation_results(
            "Run simulation before exporting plots."
        )

        if results is None:
            return

        no_drag, linear_drag, quadratic_drag = results

        _PLOTS_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        show_vectors = self.parameter_panel.should_show_vectors()

        plot_motion(
            no_drag["x"],
            no_drag["y"],
            linear_drag["x"],
            linear_drag["y"],
            quadratic_drag["x"],
            quadratic_drag["y"],
            self.current_parameters,
            show_vectors,
            _PLOTS_DIRECTORY / "trajectory_plot.png",
        )

        plot_energy(
            no_drag["E"],
            linear_drag["E"],
            quadratic_drag["E"],
            no_drag["t"],
            linear_drag["t"],
            quadratic_drag["t"],
            _PLOTS_DIRECTORY / "energy_comparison.png",
        )

        plot_speed(
            no_drag["v"],
            linear_drag["v"],
            quadratic_drag["v"],
            no_drag["t"],
            linear_drag["t"],
            quadratic_drag["t"],
            _PLOTS_DIRECTORY / "speed_comparison.png",
        )

        QMessageBox.information(
            self,
            "Export complete",
            (
                "Plots saved to results/plots/.\n\n"
                "You can open this folder using the 'Open plots folder' button "
                "in the left panel."
            ),
        )

    def export_animation(self) -> None:
        """Export a GIF animation for the latest successful simulation."""

        results = self._require_simulation_results(
            "Run simulation before exporting animation."
        )

        if results is None:
            return

        _ANIMATIONS_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        show_vectors = self.parameter_panel.should_show_vectors()

        animate_projectile_motion(
            *results,
            self.current_parameters,
            show_vectors,
            _ANIMATIONS_DIRECTORY / "projectile_motion.gif",
        )

        QMessageBox.information(
            self,
            "Export complete",
            (
                "Animation saved to results/animations/projectile_motion.gif.\n\n"
                "You can open this folder using the 'Open GIF folder' button "
                "in the left panel."
            ),
        )

    def change_theme(self, theme_text: str) -> None:
        """Save and apply a supported application theme."""

        if not is_theme_name(theme_text):
            return

        self.current_theme = theme_text
        save_theme(theme_text)

        application = QApplication.instance()

        if isinstance(application, QApplication):
            application.setStyleSheet(get_stylesheet(theme_text))

    def open_plots_folder(self) -> None:
        """Create and open the directory containing exported static plots."""

        self._open_directory(_PLOTS_DIRECTORY)

    def open_animations_folder(self) -> None:
        """Create and open the directory containing exported GIF animations."""

        self._open_directory(_ANIMATIONS_DIRECTORY)

    @staticmethod
    def _open_directory(directory: Path) -> None:
        """Create a directory and request that the operating system open it."""

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(directory.resolve())))

    def closeEvent(self, event: QCloseEvent) -> None:
        """Save valid GUI parameters before allowing the window to close."""

        try:
            parameters = self.parameter_panel.get_parameters()

        except ValueError:
            parameters = self.current_parameters

        save_user_settings(parameters)

        super().closeEvent(event)
