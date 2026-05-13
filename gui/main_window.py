from PySide6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from gui.parameter_panel import ParameterPanel
from gui.results_panel import ResultsPanel

from simulation.solve import (
    solve_projectile_motion_no_drag,
    solve_projectile_motion_linear_drag,
    solve_projectile_motion_quadratic_drag,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Projectile Motion Simulator")
        self.resize(1400, 850)

        central_widget = QWidget()
        main_layout = QHBoxLayout()

        self.parameter_panel = ParameterPanel()
        self.results_panel = ResultsPanel()

        self.parameter_panel.run_simulation_button.clicked.connect(self.run_simulation)

        left_panel = QWidget()
        left_panel.setFixedWidth(380)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.parameter_panel)
        left_layout.addWidget(self.results_panel, 1)

        left_panel.setLayout(left_layout)

        main_area = QWidget()
        main_area_layout = QVBoxLayout()

        video_area = QLabel("Video playback")
        video_area.setMinimumHeight(300)
        video_area.setStyleSheet(
            "border: 1px solid gray; font-size: 24px; qproperty-alignment: AlignCenter;"
        )

        plots_area = QLabel("Images / plots")
        plots_area.setMinimumHeight(300)
        plots_area.setStyleSheet(
            "border: 1px solid gray; font-size: 24px; qproperty-alignment: AlignCenter;"
        )

        main_area_layout.addWidget(video_area)
        main_area_layout.addWidget(plots_area)

        main_area.setLayout(main_area_layout)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(main_area, 1)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def run_simulation(self) -> None:
        try:
            parameters = self.parameter_panel.get_parameters()

            no_drag = solve_projectile_motion_no_drag(parameters)
            linear_drag = solve_projectile_motion_linear_drag(parameters)
            quadratic_drag = solve_projectile_motion_quadratic_drag(parameters)

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
