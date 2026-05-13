from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from config.parameters import DEFAULT_PARAMETERS, Parameters


class ParameterPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setFixedWidth(320)

        layout = QFormLayout()

        self.parameters_label = QLabel("Parameters")
        self.parameters_label.setProperty("class", "h1")

        self.velocity_input = QDoubleSpinBox()
        self.velocity_input.setRange(0.0, 1000.0)
        self.velocity_input.setValue(DEFAULT_PARAMETERS.v0)
        self.velocity_input.setSingleStep(1.0)
        self.velocity_input.setDecimals(2)
        self.velocity_input.setSuffix(" m/s")

        self.angle_input = QDoubleSpinBox()
        self.angle_input.setRange(0.0, 90.0)
        self.angle_input.setValue(DEFAULT_PARAMETERS.angle_deg)
        self.angle_input.setSingleStep(0.1)
        self.angle_input.setDecimals(1)
        self.angle_input.setSuffix(" \u00b0")

        self.mass_input = QDoubleSpinBox()
        self.mass_input.setRange(0.001, 100.0)
        self.mass_input.setValue(DEFAULT_PARAMETERS.mass)
        self.mass_input.setSingleStep(0.01)
        self.mass_input.setDecimals(3)
        self.mass_input.setSuffix(" kg")

        self.radius_input = QDoubleSpinBox()
        self.radius_input.setRange(0.001, 10.0)
        self.radius_input.setValue(DEFAULT_PARAMETERS.radius)
        self.radius_input.setSingleStep(0.001)
        self.radius_input.setDecimals(4)
        self.radius_input.setSuffix(" m")

        self.drag_coefficient_input = QDoubleSpinBox()
        self.drag_coefficient_input.setRange(0.0, 5.0)
        self.drag_coefficient_input.setValue(DEFAULT_PARAMETERS.cd)
        self.drag_coefficient_input.setSingleStep(0.01)
        self.drag_coefficient_input.setDecimals(3)

        self.air_density_input = QDoubleSpinBox()
        self.air_density_input.setRange(0.0, 10.0)
        self.air_density_input.setValue(DEFAULT_PARAMETERS.rho)
        self.air_density_input.setSingleStep(0.001)
        self.air_density_input.setDecimals(4)
        self.air_density_input.setSuffix(" kg/m³")

        self.linear_drag_coefficient_input = QDoubleSpinBox()
        self.linear_drag_coefficient_input.setRange(0.0001, 10.0)
        self.linear_drag_coefficient_input.setValue(DEFAULT_PARAMETERS.linear_drag)
        self.linear_drag_coefficient_input.setSingleStep(0.01)
        self.linear_drag_coefficient_input.setDecimals(4)

        self.dt_input = QDoubleSpinBox()
        self.dt_input.setRange(0.0001, 1.0)
        self.dt_input.setValue(DEFAULT_PARAMETERS.dt)
        self.dt_input.setSingleStep(0.001)
        self.dt_input.setDecimals(4)
        self.dt_input.setSuffix(" s")

        self.t_max_input = QDoubleSpinBox()
        self.t_max_input.setRange(1.0, 1000.0)
        self.t_max_input.setValue(DEFAULT_PARAMETERS.t_max)
        self.t_max_input.setSingleStep(1.0)
        self.t_max_input.setDecimals(2)
        self.t_max_input.setSuffix(" s")

        self.print_parameters_button = QPushButton("Print parameters")

        layout.addRow(self.parameters_label)
        layout.addRow(QLabel("Initial speed (<b>v0</b>):"), self.velocity_input)
        layout.addRow(QLabel("Angle (<b>\u03b1</b>):"), self.angle_input)
        layout.addRow(QLabel("Mass (<b>m</b>):"), self.mass_input)
        layout.addRow(QLabel("Radius (<b>R</b>):"), self.radius_input)
        layout.addRow(
            QLabel("Linear drag coefficient (<b>b</b>):"),
            self.linear_drag_coefficient_input,
        )
        layout.addRow(
            QLabel("Quadratic drag coefficient (<b>Cd</b>):"),
            self.drag_coefficient_input,
        )
        layout.addRow(QLabel("Air density (<b>\u03c1</b>):"), self.air_density_input)
        layout.addRow(QLabel("Time step (<b>dt</b>):"), self.dt_input)
        layout.addRow(QLabel("Max time (<b>Tmax</b>):"), self.t_max_input)
        layout.addRow(self.print_parameters_button)

        self.setLayout(layout)

    def get_parameters(self) -> Parameters:
        return Parameters(
            v0=self.velocity_input.value(),
            angle_deg=self.angle_input.value(),
            mass=self.mass_input.value(),
            radius=self.radius_input.value(),
            cd=self.drag_coefficient_input.value(),
            rho=self.air_density_input.value(),
            linear_drag=self.linear_drag_coefficient_input.value(),
            dt=self.dt_input.value(),
            t_max=self.t_max_input.value(),
            g=DEFAULT_PARAMETERS.g,
        )
