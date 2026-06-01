import math
from dataclasses import FrozenInstanceError
from typing import Any, cast

import pytest

from src.config.parameters import DEFAULT_PARAMETERS, MAX_SIMULATION_STEPS, Parameters


@pytest.fixture
def parameters() -> Parameters:
    return Parameters()


def test_default_parameters_initialization(parameters: Parameters) -> None:
    assert parameters.initial_velocity == 50.0
    assert parameters.initial_angle_degrees == 45.0
    assert parameters.mass == 0.145
    assert parameters.radius == 0.0366
    assert parameters.drag_coefficient == 0.47
    assert parameters.air_density == 1.225
    assert parameters.linear_drag == 0.02
    assert parameters.time_step == 0.01
    assert parameters.time_max == 10.0
    assert parameters.g == 9.80665
    assert parameters.wind_speed == 0.0
    assert parameters.wind_angle_degrees == 0.0
    assert parameters.initial_x == 0.0
    assert parameters.initial_y == 0.0


def test_default_parameters_constant() -> None:
    assert DEFAULT_PARAMETERS == Parameters()


def test_parameters_are_frozen(parameters: Parameters) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(parameters, "mass", 1.0)


@pytest.mark.parametrize(
    ("degrees", "radians_expected"),
    [
        (0.0, 0.0),
        (45.0, math.pi / 4),
        (90.0, math.pi / 2),
    ],
)
def test_initial_angle_radians(degrees: float, radians_expected: float) -> None:
    parameters = Parameters(initial_angle_degrees=degrees)

    assert parameters.initial_angle_radians == pytest.approx(radians_expected)


@pytest.mark.parametrize(
    ("degrees", "radians_expected"),
    [
        (0.0, 0.0),
        (90.0, math.pi / 2),
        (180.0, math.pi),
        (270.0, 3 * math.pi / 2),
        (360.0, 2 * math.pi),
    ],
)
def test_wind_angle_radians(degrees: float, radians_expected: float) -> None:
    parameters = Parameters(wind_angle_degrees=degrees)

    assert parameters.wind_angle_radians == pytest.approx(radians_expected)


@pytest.mark.parametrize(
    ("angle", "expected_vx", "expected_vy"),
    [
        (0.0, 50.0, 0.0),
        (45.0, 50.0 / math.sqrt(2), 50.0 / math.sqrt(2)),
        (90.0, 0.0, 50.0),
    ],
)
def test_initial_velocity_components(
    angle: float,
    expected_vx: float,
    expected_vy: float,
) -> None:
    parameters = Parameters(
        initial_velocity=50.0,
        initial_angle_degrees=angle,
    )

    assert parameters.vx0 == pytest.approx(expected_vx)
    assert parameters.vy0 == pytest.approx(expected_vy)


@pytest.mark.parametrize(
    ("angle", "expected_vx", "expected_vy"),
    [
        (0.0, 10.0, 0.0),
        (90.0, 0.0, 10.0),
        (180.0, -10.0, 0.0),
        (270.0, 0.0, -10.0),
        (360.0, 10.0, 0.0),
    ],
)
def test_wind_velocity_components(
    angle: float,
    expected_vx: float,
    expected_vy: float,
) -> None:
    parameters = Parameters(
        wind_speed=10.0,
        wind_angle_degrees=angle,
    )

    assert parameters.wind_vx == pytest.approx(expected_vx)
    assert parameters.wind_vy == pytest.approx(expected_vy)


def test_area() -> None:
    parameters = Parameters(radius=0.0366)

    expected = math.pi * 0.0366 * 0.0366

    assert parameters.area == pytest.approx(expected)


def test_linear_drag_factor_k() -> None:
    parameters = Parameters(
        linear_drag=0.02,
        mass=0.145,
    )

    assert parameters.linear_drag_factor == pytest.approx(0.02 / 0.145)


def test_quadratic_drag_factor_q() -> None:
    parameters = Parameters(
        air_density=1.225,
        drag_coefficient=0.47,
        radius=0.0366,
        mass=0.145,
    )

    area = math.pi * 0.0366 * 0.0366
    expected = 1.225 * 0.47 * area / (2.0 * 0.145)

    assert parameters.quadratic_drag_factor == pytest.approx(expected)


@pytest.mark.parametrize(
    "field_name",
    [
        "initial_velocity",
        "initial_angle_degrees",
        "mass",
        "radius",
        "drag_coefficient",
        "air_density",
        "linear_drag",
        "time_step",
        "time_max",
        "g",
        "wind_speed",
        "wind_angle_degrees",
        "initial_x",
        "initial_y",
    ],
)
@pytest.mark.parametrize("bad_value", [math.inf, -math.inf, math.nan])
def test_rejects_non_finite_values(field_name: str, bad_value: float) -> None:
    kwargs: dict[str, float] = {field_name: bad_value}

    with pytest.raises(ValueError, match="must be a finite number"):
        Parameters(**cast(Any, kwargs))


@pytest.mark.parametrize(
    "kwargs",
    [
        {"initial_velocity": -0.1},
        {"initial_angle_degrees": -0.1},
        {"initial_angle_degrees": 90.1},
        {"mass": 0.0},
        {"mass": -1.0},
        {"radius": 0.0},
        {"radius": -1.0},
        {"drag_coefficient": -0.1},
        {"air_density": -0.1},
        {"linear_drag": 0.0},
        {"linear_drag": -0.1},
        {"time_step": 0.0},
        {"time_step": -0.1},
        {"time_max": 0.0},
        {"time_max": -1.0},
        {"g": 0.0},
        {"g": -1.0},
        {"wind_speed": -0.1},
        {"wind_angle_degrees": -0.1},
        {"wind_angle_degrees": 360.1},
    ],
)
def test_rejects_invalid_ranges(kwargs: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        Parameters(**cast(Any, kwargs))


def test_accepts_valid_boundary_values() -> None:
    parameters = Parameters(
        initial_velocity=0.0,
        initial_angle_degrees=0.0,
        drag_coefficient=0.0,
        air_density=0.0,
        wind_speed=0.0,
        wind_angle_degrees=360.0,
    )

    assert parameters.initial_velocity == 0.0
    assert parameters.initial_angle_degrees == 0.0
    assert parameters.drag_coefficient == 0.0
    assert parameters.air_density == 0.0
    assert parameters.wind_speed == 0.0
    assert parameters.wind_angle_degrees == 360.0


def test_accepts_angle_90_degrees() -> None:
    params = Parameters(initial_angle_degrees=90.0)

    assert params.initial_angle_degrees == 90.0
    assert params.vx0 == pytest.approx(0.0)
    assert params.vy0 == pytest.approx(params.initial_velocity)


def test_accepts_wind_angle_360_degrees() -> None:
    params = Parameters(
        wind_speed=10.0,
        wind_angle_degrees=360.0,
    )

    assert params.wind_angle_degrees == 360.0
    assert params.wind_vx == pytest.approx(10.0)
    assert params.wind_vy == pytest.approx(0.0)


def test_rejects_zero_time_step() -> None:
    with pytest.raises(ValueError, match="time_step must be greater than zero."):
        Parameters(time_step=0.0)


def test_rejects_negative_time_step() -> None:
    with pytest.raises(ValueError, match="time_step must be greater than zero."):
        Parameters(time_step=-0.01)


def test_rejects_zero_time_max() -> None:
    with pytest.raises(ValueError):
        Parameters(time_max=0.0)


def test_rejects_negative_time_max() -> None:
    with pytest.raises(ValueError):
        Parameters(time_max=-1.0)


def test_rejects_too_many_simulation_steps() -> None:
    time_step = 0.01
    time_max = time_step * (MAX_SIMULATION_STEPS + 1)

    with pytest.raises(ValueError, match="Too many simulation steps"):
        Parameters(
            time_step=time_step,
            time_max=time_max,
        )


def test_accepts_exactly_maximum_simulation_steps() -> None:
    time_step = 0.01
    time_max = time_step * MAX_SIMULATION_STEPS

    params = Parameters(
        time_step=time_step,
        time_max=time_max,
    )

    assert params.time_max / params.time_step == MAX_SIMULATION_STEPS


def test_custom_initial_position_is_stored() -> None:
    params = Parameters(
        initial_x=12.5,
        initial_y=3.25,
    )

    assert params.initial_x == 12.5
    assert params.initial_y == 3.25


def test_dataclass_equality() -> None:
    params_1 = Parameters()
    params_2 = Parameters()
    params_3 = Parameters(initial_velocity=60.0)

    assert params_1 == params_2
    assert params_1 != params_3


def test_negative_initial_y_is_rejected() -> None:
    with pytest.raises(ValueError, match="initial_y"):
        Parameters(initial_y=-1.0)
