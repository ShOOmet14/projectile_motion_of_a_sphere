from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from config.parameters import Parameters


class ParameterPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setFixedWidth(320)

        layout = QFormLayout()

        self.velocity_input = QDoubleSpinBox()
        self.velocity_input.setRange(0.0, 1000.0)
        self.velocity_input.setValue(50.0)
        self.velocity_input.setSingleStep(1.0)
        self.velocity_input.setDecimals(2)
        self.velocity_input.setSuffix(" m/s")

        self.angle_input = QDoubleSpinBox()
        self.angle_input.setRange(0.0, 90.0)
        self.angle_input.setValue(45.0)
        self.angle_input.setSingleStep(0.1)
        self.angle_input.setDecimals(1)
        self.angle_input.setSuffix(" \u00b0")

        self.mass_input = QDoubleSpinBox()
        self.mass_input.setRange(0.001, 100.0)
        self.mass_input.setValue(0.145)
        self.mass_input.setSingleStep(0.01)
        self.mass_input.setDecimals(3)
        self.mass_input.setSuffix(" kg")

        self.radius_input = QDoubleSpinBox()
        self.radius_input.setRange(0.001, 10.0)
        self.radius_input.setValue(0.0366)
        self.radius_input.setSingleStep(0.001)
        self.radius_input.setDecimals(4)
        self.radius_input.setSuffix(" m")

        self.drag_coefficient_input = QDoubleSpinBox()
        self.drag_coefficient_input.setRange(0.0, 5.0)
        self.drag_coefficient_input.setValue(0.47)
        self.drag_coefficient_input.setSingleStep(0.01)
        self.drag_coefficient_input.setDecimals(3)

        self.air_density_input = QDoubleSpinBox()
        self.air_density_input.setRange(0.0, 10.0)
        self.air_density_input.setValue(1.225)
        self.air_density_input.setSingleStep(0.001)
        self.air_density_input.setDecimals(4)
        self.air_density_input.setSuffix(" kg/m³")

        self.linear_drag_coefficient_input = QDoubleSpinBox()
        self.linear_drag_coefficient_input.setRange(0.0, 10.0)
        self.linear_drag_coefficient_input.setValue(0.1)
        self.linear_drag_coefficient_input.setSingleStep(0.01)
        self.linear_drag_coefficient_input.setDecimals(4)

        self.dt_input = QDoubleSpinBox()
        self.dt_input.setRange(0.0001, 1.0)
        self.dt_input.setValue(0.01)
        self.dt_input.setSingleStep(0.001)
        self.dt_input.setDecimals(4)
        self.dt_input.setSuffix(" s")

        self.print_parameters_button = QPushButton("Print parameters")

        layout.addRow(QLabel("Initial speed:"), self.velocity_input)
        layout.addRow(QLabel("Angle:"), self.angle_input)
        layout.addRow(QLabel("Mass:"), self.mass_input)
        layout.addRow(QLabel("Radius:"), self.radius_input)
        layout.addRow(QLabel("Cd:"), self.drag_coefficient_input)
        layout.addRow(QLabel("Air density:"), self.air_density_input)
        layout.addRow(
            QLabel("Linear drag coefficient:"),
            self.linear_drag_coefficient_input,
        )
        layout.addRow(QLabel("Time step:"), self.dt_input)
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
            g=9.80665,
        )
