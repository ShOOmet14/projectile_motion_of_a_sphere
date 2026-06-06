"""Provide GUI controls for simulation parameters and display settings."""

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from src.config.parameters import DEFAULT_PARAMETERS, Parameters
from src.config.settings import ThemeName


_THEME_NAMES: tuple[ThemeName, ...] = (
    "light",
    "dark",
)


def _create_double_spin_box(
    *,
    minimum: float,
    maximum: float,
    value: float,
    decimals: int,
    step: float,
    suffix: str = "",
    wrapping: bool = False,
) -> QDoubleSpinBox:
    """Create and configure a numeric input widget."""

    input_widget = QDoubleSpinBox()
    input_widget.setRange(minimum, maximum)
    input_widget.setDecimals(decimals)
    input_widget.setValue(value)
    input_widget.setSingleStep(step)
    input_widget.setSuffix(suffix)
    input_widget.setWrapping(wrapping)

    return input_widget


def _create_button(text: str, object_name: str) -> QPushButton:
    """Create a button with the stylesheet selector used by the GUI."""

    button = QPushButton(text)
    button.setObjectName(object_name)

    return button


class ParameterPanel(QWidget):
    """Collect simulation parameters and expose export-related GUI actions."""

    def __init__(
        self,
        parameters: Parameters = DEFAULT_PARAMETERS,
        theme: ThemeName = "light",
    ) -> None:
        """Create parameter controls initialized from the supplied settings."""

        super().__init__()

        self.setMinimumWidth(430)
        self.setObjectName("parameterPanel")

        layout = QFormLayout()

        self.parameters_label = QLabel("Parameters")
        self.parameters_label.setProperty("class", "h1")

        # Launch conditions
        self.velocity_input = _create_double_spin_box(
            minimum=0.0,
            maximum=1000.0,
            value=parameters.initial_velocity,
            decimals=2,
            step=1.0,
            suffix=" m/s",
        )

        self.angle_input = _create_double_spin_box(
            minimum=0.0,
            maximum=90.0,
            value=parameters.initial_angle_degrees,
            decimals=1,
            step=0.1,
            suffix=" °",
        )

        self.initial_x_input = _create_double_spin_box(
            minimum=-1_000_000.0,
            maximum=1_000_000.0,
            value=parameters.initial_x,
            decimals=2,
            step=1.0,
            suffix=" m",
        )

        self.initial_y_input = _create_double_spin_box(
            minimum=0.0,
            maximum=1_000_000.0,
            value=parameters.initial_y,
            decimals=2,
            step=1.0,
            suffix=" m",
        )

        # Projectile properties
        self.mass_input = _create_double_spin_box(
            minimum=0.001,
            maximum=100.0,
            value=parameters.mass,
            decimals=3,
            step=0.01,
            suffix=" kg",
        )

        self.radius_input = _create_double_spin_box(
            minimum=0.001,
            maximum=10.0,
            value=parameters.radius,
            decimals=4,
            step=0.001,
            suffix=" m",
        )

        # Drag-model parameters
        self.drag_coefficient_input = _create_double_spin_box(
            minimum=0.0,
            maximum=5.0,
            value=parameters.drag_coefficient,
            decimals=3,
            step=0.01,
        )

        self.air_density_input = _create_double_spin_box(
            minimum=0.0,
            maximum=10.0,
            value=parameters.air_density,
            decimals=4,
            step=0.001,
            suffix=" kg/m³",
        )

        self.linear_drag_coefficient_input = _create_double_spin_box(
            minimum=0.0001,
            maximum=10.0,
            value=parameters.linear_drag,
            decimals=4,
            step=0.01,
        )

        # Numerical simulation settings
        self.dt_input = _create_double_spin_box(
            minimum=0.0001,
            maximum=1.0,
            value=parameters.time_step,
            decimals=4,
            step=0.001,
            suffix=" s",
        )

        self.t_max_input = _create_double_spin_box(
            minimum=1.0,
            maximum=1000.0,
            value=parameters.time_max,
            decimals=2,
            step=1.0,
            suffix=" s",
        )

        self.gravity_input = _create_double_spin_box(
            minimum=0.1,
            maximum=100.0,
            value=parameters.g,
            decimals=5,
            step=0.01,
            suffix=" m/s²",
        )

        # Wind conditions
        self.wind_speed_input = _create_double_spin_box(
            minimum=0.0,
            maximum=200.0,
            value=parameters.wind_speed,
            decimals=2,
            step=1.0,
            suffix=" m/s",
        )

        self.wind_angle_input = _create_double_spin_box(
            minimum=0.0,
            maximum=360.0,
            value=parameters.wind_angle_degrees,
            decimals=1,
            step=5.0,
            suffix=" °",
            wrapping=True,
        )

        # Simulation and export actions
        self.run_simulation_button = _create_button(
            "Run simulation",
            "primaryButton",
        )

        self.export_csv_button = _create_button(
            "Export CSV",
            "secondaryButton",
        )

        self.export_plots_button = _create_button(
            "Export plots",
            "secondaryButton",
        )

        self.export_animation_button = _create_button(
            "Export animation",
            "secondaryButton",
        )

        # Display settings
        self.settings_label = QLabel("Settings")
        self.settings_label.setProperty("class", "h1")

        self.theme_input = QComboBox()
        self.theme_input.addItems(list(_THEME_NAMES))
        self.theme_input.setCurrentText(theme)

        self.show_vectors_checkbox = QCheckBox("Show wind and velocity vectors")
        self.show_vectors_checkbox.setChecked(True)

        # Output-folder actions
        self.open_plots_folder_button = _create_button(
            "Open plots folder",
            "folderButton",
        )

        self.open_animations_folder_button = _create_button(
            "Open GIF folder",
            "folderButton",
        )

        layout.addRow(self.parameters_label)
        layout.addRow(QLabel("Initial speed (<b>v0</b>):"), self.velocity_input)
        layout.addRow(QLabel("Angle (<b>α</b>):"), self.angle_input)
        layout.addRow(
            QLabel("Initial x position (<b>x0</b>):"),
            self.initial_x_input,
        )
        layout.addRow(
            QLabel("Initial y position (<b>y0</b>):"),
            self.initial_y_input,
        )
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
        layout.addRow(QLabel("Air density (<b>ρ</b>):"), self.air_density_input)
        layout.addRow(QLabel("Time step (<b>dt</b>):"), self.dt_input)
        layout.addRow(QLabel("Max time (<b>Tmax</b>):"), self.t_max_input)
        layout.addRow(QLabel("Gravity (<b>g</b>):"), self.gravity_input)
        layout.addRow(QLabel("Wind speed:"), self.wind_speed_input)
        layout.addRow(QLabel("Wind angle:"), self.wind_angle_input)
        layout.addRow(self.run_simulation_button)
        layout.addRow(self.export_csv_button)
        layout.addRow(self.export_plots_button)
        layout.addRow(self.export_animation_button)

        layout.addRow(self.settings_label)
        layout.addRow(QLabel("Theme:"), self.theme_input)
        layout.addRow(self.show_vectors_checkbox)

        layout.addRow(self.open_plots_folder_button)
        layout.addRow(self.open_animations_folder_button)

        self.setLayout(layout)

    def get_parameters(self) -> Parameters:
        """Return validated simulation parameters read from the GUI controls."""

        return Parameters(
            initial_velocity=self.velocity_input.value(),
            initial_angle_degrees=self.angle_input.value(),
            mass=self.mass_input.value(),
            radius=self.radius_input.value(),
            drag_coefficient=self.drag_coefficient_input.value(),
            air_density=self.air_density_input.value(),
            linear_drag=self.linear_drag_coefficient_input.value(),
            time_step=self.dt_input.value(),
            time_max=self.t_max_input.value(),
            g=self.gravity_input.value(),
            wind_speed=self.wind_speed_input.value(),
            wind_angle_degrees=self.wind_angle_input.value(),
            initial_x=self.initial_x_input.value(),
            initial_y=self.initial_y_input.value(),
        )

    def set_parameters(self, parameters: Parameters) -> None:
        """Update all simulation input widgets from validated parameters."""

        self.velocity_input.setValue(parameters.initial_velocity)
        self.angle_input.setValue(parameters.initial_angle_degrees)
        self.initial_x_input.setValue(parameters.initial_x)
        self.initial_y_input.setValue(parameters.initial_y)
        self.mass_input.setValue(parameters.mass)
        self.radius_input.setValue(parameters.radius)
        self.drag_coefficient_input.setValue(parameters.drag_coefficient)
        self.air_density_input.setValue(parameters.air_density)
        self.linear_drag_coefficient_input.setValue(parameters.linear_drag)
        self.dt_input.setValue(parameters.time_step)
        self.t_max_input.setValue(parameters.time_max)
        self.gravity_input.setValue(parameters.g)
        self.wind_speed_input.setValue(parameters.wind_speed)
        self.wind_angle_input.setValue(parameters.wind_angle_degrees)

    def should_show_vectors(self) -> bool:
        """Return whether wind and velocity vectors should be displayed."""

        return self.show_vectors_checkbox.isChecked()
