from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel

from gui.parameter_panel import ParameterPanel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Projectile Motion Simulator")
        self.resize(1200, 800)

        central_widget = QWidget()
        main_layout = QHBoxLayout()

        self.parameter_panel = ParameterPanel()
        self.parameter_panel.print_parameters_button.clicked.connect(
            self.print_parameters
        )

        main_area = QWidget()
        main_area_layout = QVBoxLayout()

        main_area_layout.addWidget(QLabel("Plot area"))
        main_area_layout.addWidget(QLabel("Results area"))

        main_area.setLayout(main_area_layout)

        main_layout.addWidget(self.parameter_panel)
        main_layout.addWidget(main_area)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def print_parameters(self) -> None:
        parameters = self.parameter_panel.get_parameters()

        print(f"v0 = {parameters.v0}")
        print(f"angle_deg = {parameters.angle_deg}")
        print(f"mass = {parameters.mass}")
        print(f"radius = {parameters.radius}")
        print(f"cd = {parameters.cd}")
        print(f"rho = {parameters.rho}")
        print(f"linear_drag = {parameters.linear_drag}")
        print(f"dt = {parameters.dt}")
        print(f"g = {parameters.g}")

        print(f"angle_rad = {parameters.angle_rad}")
        print(f"vx0 = {parameters.vx0}")
        print(f"vy0 = {parameters.vy0}")
        print(f"area = {parameters.area}")
        print(f"k = {parameters.k}")
        print(f"q = {parameters.q}")
