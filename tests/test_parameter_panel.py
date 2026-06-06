import pytest
from pytestqt.qtbot import QtBot

from src.config.parameters import DEFAULT_PARAMETERS, Parameters
from src.gui.parameter_panel import ParameterPanel


@pytest.fixture
def panel(qtbot: QtBot) -> ParameterPanel:
    widget = ParameterPanel()
    qtbot.addWidget(widget)

    return widget


def test_initialization_uses_default_parameters(panel: ParameterPanel) -> None:
    assert panel.objectName() == "parameterPanel"
    assert panel.minimumWidth() == 430

    assert panel.get_parameters() == DEFAULT_PARAMETERS
    assert panel.theme_input.currentText() == "light"
    assert panel.should_show_vectors() is True


def test_initialization_uses_given_parameters_and_theme(qtbot: QtBot) -> None:
    parameters = Parameters(
        initial_velocity=12.5,
        initial_angle_degrees=30.0,
        mass=2.0,
        radius=0.5,
        drag_coefficient=0.2,
        air_density=1.1,
        linear_drag=0.3,
        time_step=0.02,
        time_max=20.0,
        g=9.81,
        wind_speed=4.0,
        wind_angle_degrees=180.0,
        initial_x=-15.0,
        initial_y=3.0,
    )

    panel = ParameterPanel(
        parameters=parameters,
        theme="dark",
    )
    qtbot.addWidget(panel)

    assert panel.get_parameters() == parameters
    assert panel.theme_input.currentText() == "dark"


def test_get_parameters_reads_current_input_values(panel: ParameterPanel) -> None:
    panel.velocity_input.setValue(24.0)
    panel.angle_input.setValue(35.0)
    panel.initial_x_input.setValue(-8.0)
    panel.initial_y_input.setValue(4.0)
    panel.mass_input.setValue(1.5)
    panel.radius_input.setValue(0.25)
    panel.drag_coefficient_input.setValue(0.4)
    panel.air_density_input.setValue(1.0)
    panel.linear_drag_coefficient_input.setValue(0.1)
    panel.dt_input.setValue(0.05)
    panel.t_max_input.setValue(15.0)
    panel.gravity_input.setValue(9.81)
    panel.wind_speed_input.setValue(3.0)
    panel.wind_angle_input.setValue(90.0)

    assert panel.get_parameters() == Parameters(
        initial_velocity=24.0,
        initial_angle_degrees=35.0,
        mass=1.5,
        radius=0.25,
        drag_coefficient=0.4,
        air_density=1.0,
        linear_drag=0.1,
        time_step=0.05,
        time_max=15.0,
        g=9.81,
        wind_speed=3.0,
        wind_angle_degrees=90.0,
        initial_x=-8.0,
        initial_y=4.0,
    )


def test_set_parameters_updates_all_inputs(panel: ParameterPanel) -> None:
    parameters = Parameters(
        initial_velocity=10.0,
        initial_angle_degrees=20.0,
        mass=0.5,
        radius=0.1,
        drag_coefficient=0.3,
        air_density=1.0,
        linear_drag=0.05,
        time_step=0.02,
        time_max=5.0,
        g=9.8,
        wind_speed=2.0,
        wind_angle_degrees=270.0,
        initial_x=-12.0,
        initial_y=6.0,
    )

    panel.set_parameters(parameters)

    assert panel.get_parameters() == parameters


def test_should_show_vectors_reads_checkbox_state(panel: ParameterPanel) -> None:
    panel.show_vectors_checkbox.setChecked(False)
    assert panel.should_show_vectors() is False

    panel.show_vectors_checkbox.setChecked(True)
    assert panel.should_show_vectors() is True


def test_theme_input_contains_supported_themes(panel: ParameterPanel) -> None:
    themes = [
        panel.theme_input.itemText(index) for index in range(panel.theme_input.count())
    ]

    assert themes == ["light", "dark"]


@pytest.mark.parametrize(
    (
        "button_name",
        "expected_text",
        "expected_object_name",
    ),
    [
        (
            "run_simulation_button",
            "Run simulation",
            "primaryButton",
        ),
        (
            "export_csv_button",
            "Export CSV",
            "secondaryButton",
        ),
        (
            "export_plots_button",
            "Export plots",
            "secondaryButton",
        ),
        (
            "export_animation_button",
            "Export animation",
            "secondaryButton",
        ),
        (
            "open_plots_folder_button",
            "Open plots folder",
            "folderButton",
        ),
        (
            "open_animations_folder_button",
            "Open GIF folder",
            "folderButton",
        ),
    ],
)
def test_button_configuration(
    panel: ParameterPanel,
    button_name: str,
    expected_text: str,
    expected_object_name: str,
) -> None:
    button = getattr(panel, button_name)

    assert button.text() == expected_text
    assert button.objectName() == expected_object_name


@pytest.mark.parametrize(
    (
        "input_name",
        "expected_minimum",
        "expected_maximum",
        "expected_step",
        "expected_decimals",
        "expected_suffix",
    ),
    [
        ("velocity_input", 0.0, 1000.0, 1.0, 2, " m/s"),
        ("angle_input", 0.0, 90.0, 0.1, 1, " °"),
        (
            "initial_x_input",
            -1_000_000.0,
            1_000_000.0,
            1.0,
            2,
            " m",
        ),
        (
            "initial_y_input",
            0.0,
            1_000_000.0,
            1.0,
            2,
            " m",
        ),
        ("mass_input", 0.001, 100.0, 0.01, 3, " kg"),
        ("radius_input", 0.001, 10.0, 0.001, 4, " m"),
        ("drag_coefficient_input", 0.0, 5.0, 0.01, 3, ""),
        ("air_density_input", 0.0, 10.0, 0.001, 4, " kg/m³"),
        (
            "linear_drag_coefficient_input",
            0.0001,
            10.0,
            0.01,
            4,
            "",
        ),
        ("dt_input", 0.0001, 1.0, 0.001, 4, " s"),
        ("t_max_input", 1.0, 1000.0, 1.0, 2, " s"),
        ("gravity_input", 0.1, 100.0, 0.01, 5, " m/s²"),
        ("wind_speed_input", 0.0, 200.0, 1.0, 2, " m/s"),
        ("wind_angle_input", 0.0, 360.0, 5.0, 1, " °"),
    ],
)
def test_numeric_input_configuration(
    panel: ParameterPanel,
    input_name: str,
    expected_minimum: float,
    expected_maximum: float,
    expected_step: float,
    expected_decimals: int,
    expected_suffix: str,
) -> None:
    input_widget = getattr(panel, input_name)

    assert input_widget.minimum() == pytest.approx(expected_minimum)
    assert input_widget.maximum() == pytest.approx(expected_maximum)
    assert input_widget.singleStep() == pytest.approx(expected_step)
    assert input_widget.decimals() == expected_decimals
    assert input_widget.suffix() == expected_suffix


def test_wind_angle_input_wraps_around(panel: ParameterPanel) -> None:
    assert panel.wind_angle_input.wrapping() is True
