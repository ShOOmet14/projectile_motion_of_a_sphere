from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from config.app_settings import ThemeName, is_theme_name
from config.parameters import Parameters


class SettingsWindow(QDialog):
    def __init__(self, parameters: Parameters, theme: ThemeName) -> None:
        super().__init__()

        self.setWindowTitle("Settings")
        self.resize(420, 360)

        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.title_label = QLabel("Settings panel")
        self.title_label.setProperty("class", "h1")

        self.theme_input = QComboBox()
        self.theme_input.addItems(["light", "dark"])
        self.theme_input.setCurrentText(theme)

        self.open_image_folder_button = QPushButton("Open image folder")
        self.open_image_folder_button.clicked.connect(self.open_image_folder)

        self.gravity_input = QDoubleSpinBox()
        self.gravity_input.setRange(0.1, 100.0)
        self.gravity_input.setValue(parameters.g)
        self.gravity_input.setSingleStep(0.01)
        self.gravity_input.setDecimals(5)
        self.gravity_input.setSuffix(" m/s²")

        self.air_density_input = QDoubleSpinBox()
        self.air_density_input.setRange(0.0, 10.0)
        self.air_density_input.setValue(parameters.rho)
        self.air_density_input.setSingleStep(0.001)
        self.air_density_input.setDecimals(4)
        self.air_density_input.setSuffix(" kg/m³")

        self.drag_coefficient_input = QDoubleSpinBox()
        self.drag_coefficient_input.setRange(0.0, 5.0)
        self.drag_coefficient_input.setValue(parameters.cd)
        self.drag_coefficient_input.setSingleStep(0.01)
        self.drag_coefficient_input.setDecimals(3)

        self.mass_input = QDoubleSpinBox()
        self.mass_input.setRange(0.001, 100.0)
        self.mass_input.setValue(parameters.mass)
        self.mass_input.setSingleStep(0.01)
        self.mass_input.setDecimals(3)
        self.mass_input.setSuffix(" kg")

        self.radius_input = QDoubleSpinBox()
        self.radius_input.setRange(0.001, 10.0)
        self.radius_input.setValue(parameters.radius)
        self.radius_input.setSingleStep(0.001)
        self.radius_input.setDecimals(4)
        self.radius_input.setSuffix(" m")

        self.linear_drag_input = QDoubleSpinBox()
        self.linear_drag_input.setRange(0.0001, 10.0)
        self.linear_drag_input.setValue(parameters.linear_drag)
        self.linear_drag_input.setSingleStep(0.01)
        self.linear_drag_input.setDecimals(4)

        self.dt_input = QDoubleSpinBox()
        self.dt_input.setRange(0.0001, 1.0)
        self.dt_input.setValue(parameters.dt)
        self.dt_input.setSingleStep(0.001)
        self.dt_input.setDecimals(4)
        self.dt_input.setSuffix(" s")

        form_layout.addRow(QLabel("Theme:"), self.theme_input)
        form_layout.addRow(self.open_image_folder_button)
        form_layout.addRow(QLabel("Gravity (<b>g</b>):"), self.gravity_input)
        form_layout.addRow(QLabel("Air density (<b>ρ</b>):"), self.air_density_input)
        form_layout.addRow(
            QLabel("Quadratic drag coefficient (<b>Cd</b>):"),
            self.drag_coefficient_input,
        )
        form_layout.addRow(QLabel("Mass (<b>m</b>):"), self.mass_input)
        form_layout.addRow(QLabel("Radius (<b>R</b>):"), self.radius_input)
        form_layout.addRow(
            QLabel("Linear drag coefficient (<b>b</b>):"),
            self.linear_drag_input,
        )
        form_layout.addRow(QLabel("Time step (<b>dt</b>):"), self.dt_input)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        main_layout.addWidget(self.title_label)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def get_selected_theme(self) -> ThemeName:
        selected_theme = self.theme_input.currentText()

        if is_theme_name(selected_theme):
            return selected_theme

        return "light"

    def open_image_folder(self) -> None:
        image_directory = Path(__file__).resolve().parents[1] / "results" / "plots"
        image_directory.mkdir(parents=True, exist_ok=True)

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(image_directory)))

    def get_updated_parameters(self, current_parameters: Parameters) -> Parameters:
        return Parameters(
            v0=current_parameters.v0,
            angle_deg=current_parameters.angle_deg,
            mass=self.mass_input.value(),
            radius=self.radius_input.value(),
            cd=self.drag_coefficient_input.value(),
            rho=self.air_density_input.value(),
            linear_drag=self.linear_drag_input.value(),
            dt=self.dt_input.value(),
            t_max=current_parameters.t_max,
            g=self.gravity_input.value(),
            x0=current_parameters.x0,
            y0=current_parameters.y0,
        )
