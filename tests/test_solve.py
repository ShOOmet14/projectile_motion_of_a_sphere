from collections.abc import Callable
from typing import Literal

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from src.config.parameters import Parameters
from src.simulation.solve import (
    ProjectileResult,
    calculate_kinetic_energy,
    calculate_mechanical_energy,
    calculate_position_linear_drag,
    calculate_position_no_drag,
    calculate_potential_energy,
    calculate_quadratic_drag_derivative,
    calculate_speed,
    calculate_velocity_linear_drag,
    calculate_velocity_no_drag,
    interpolate_value_at_ground,
    runge_kutta_step,
    solve_projectile_motion_linear_drag,
    solve_projectile_motion_no_drag,
    solve_projectile_motion_quadratic_drag,
)


ProjectileResultKey = Literal[
    "t",
    "x",
    "y",
    "vx",
    "vy",
    "v",
    "Ek",
    "Ep",
    "E",
]

Solver = Callable[[Parameters], ProjectileResult]

RESULT_KEYS: tuple[ProjectileResultKey, ...] = (
    "t",
    "x",
    "y",
    "vx",
    "vy",
    "v",
    "Ek",
    "Ep",
    "E",
)


def make_parameters(**overrides: float) -> Parameters:
    values: dict[str, float] = {
        "initial_velocity": 10.0,
        "initial_angle_degrees": 30.0,
        "mass": 2.0,
        "radius": 0.1,
        "drag_coefficient": 0.4,
        "air_density": 1.2,
        "linear_drag": 0.4,
        "time_step": 0.05,
        "time_max": 5.0,
        "g": 10.0,
        "wind_speed": 0.0,
        "wind_angle_degrees": 0.0,
        "initial_x": 2.0,
        "initial_y": 1.0,
    }
    values.update(overrides)
    return Parameters(**values)


def assert_valid_projectile_result(result: ProjectileResult) -> None:
    assert set(result) == set(RESULT_KEYS)

    arrays = tuple(result[key] for key in RESULT_KEYS)

    lengths = {len(values) for values in arrays}
    assert len(lengths) == 1
    assert lengths.pop() >= 1

    for values in arrays:
        assert values.dtype == np.float64
        assert np.all(np.isfinite(values))

    assert result["t"][0] == pytest.approx(0.0)
    assert np.all(np.diff(result["t"]) > 0.0)
    assert result["y"][-1] == pytest.approx(0.0)
    assert np.all(result["y"] >= 0.0)

    assert_allclose(result["v"], np.hypot(result["vx"], result["vy"]))
    assert_allclose(result["E"], result["Ek"] + result["Ep"])


def test_calculate_position_no_drag() -> None:
    time = np.array([0.0, 0.5, 1.0], dtype=np.float64)

    x, y = calculate_position_no_drag(
        time=time,
        x0=1.0,
        y0=2.0,
        vx0=4.0,
        vy0=5.0,
        g=10.0,
    )

    assert_array_equal(x, np.array([1.0, 3.0, 5.0]))
    assert_array_equal(y, np.array([2.0, 3.25, 2.0]))


def test_calculate_velocity_no_drag() -> None:
    time = np.array([0.0, 0.5, 1.0], dtype=np.float64)

    vx, vy = calculate_velocity_no_drag(
        time=time,
        vx0=4.0,
        vy0=5.0,
        g=10.0,
    )

    assert_array_equal(vx, np.array([4.0, 4.0, 4.0]))
    assert_array_equal(vy, np.array([5.0, 0.0, -5.0]))


def test_calculate_position_linear_drag_with_wind() -> None:
    time = np.array([0.0, 1.0, 2.0], dtype=np.float64)

    x, y = calculate_position_linear_drag(
        time=time,
        x0=1.0,
        y0=2.0,
        vx0=4.0,
        vy0=5.0,
        k=0.5,
        g=10.0,
        wind_vx=1.0,
        wind_vy=-1.0,
    )

    assert_allclose(x, np.array([1.0, 4.36081604, 6.79272335]))
    assert_allclose(y, np.array([2.0, 1.46040569, -7.12973094]))


def test_calculate_velocity_linear_drag_with_wind() -> None:
    time = np.array([0.0, 1.0, 2.0], dtype=np.float64)

    vx, vy = calculate_velocity_linear_drag(
        time=time,
        vx0=4.0,
        vy0=5.0,
        k=0.5,
        g=10.0,
        wind_vx=1.0,
        wind_vy=-1.0,
    )

    assert_allclose(vx, np.array([4.0, 2.81959198, 2.10363832]))
    assert_allclose(vy, np.array([5.0, -5.23020285, -11.43513453]))


def test_calculate_quadratic_drag_derivative_uses_relative_velocity() -> None:
    state = np.array([10.0, 20.0, 5.0, -1.0], dtype=np.float64)

    derivative = calculate_quadratic_drag_derivative(
        state=state,
        q=0.5,
        g=10.0,
        wind_vx=2.0,
        wind_vy=-5.0,
    )

    relative_speed = 5.0
    assert_allclose(derivative, np.array([5.0, -1.0, -7.5, -20.0]))
    assert relative_speed == pytest.approx(np.hypot(3.0, 4.0))


def test_runge_kutta_step_is_exact_for_constant_acceleration() -> None:
    state = np.array([1.0, 2.0, 4.0, 5.0], dtype=np.float64)

    state_new = runge_kutta_step(
        state_old=state,
        dt=0.5,
        q=0.0,
        g=10.0,
        wind_vx=3.0,
        wind_vy=-7.0,
    )

    assert_allclose(state_new, np.array([3.0, 3.25, 4.0, 0.0]))


def test_interpolate_value_at_ground() -> None:
    result = interpolate_value_at_ground(
        value_1=10.0,
        value_2=14.0,
        y1=3.0,
        y2=-1.0,
    )

    assert result == pytest.approx(13.0)


def test_calculate_speed() -> None:
    vx = np.array([3.0, 5.0, 0.0], dtype=np.float64)
    vy = np.array([4.0, 12.0, -2.0], dtype=np.float64)

    assert_array_equal(calculate_speed(vx, vy), np.array([5.0, 13.0, 2.0]))


def test_energy_calculations() -> None:
    speed = np.array([2.0, 4.0], dtype=np.float64)
    y = np.array([3.0, 5.0], dtype=np.float64)

    kinetic = calculate_kinetic_energy(speed=speed, mass=2.0)
    potential = calculate_potential_energy(y=y, mass=2.0, g=10.0)
    mechanical = calculate_mechanical_energy(kinetic, potential)

    assert_array_equal(kinetic, np.array([4.0, 16.0]))
    assert_array_equal(potential, np.array([60.0, 100.0]))
    assert_array_equal(mechanical, np.array([64.0, 116.0]))


def test_solve_projectile_motion_no_drag_returns_interpolated_ground_hit() -> None:
    parameters = make_parameters(time_step=0.3)

    result = solve_projectile_motion_no_drag(parameters)

    assert_valid_projectile_result(result)
    assert result["t"][-1] == pytest.approx(1.1636363636363636)
    assert result["x"][-1] == pytest.approx(12.077386516764378)
    assert result["vx"][-1] == pytest.approx(parameters.vx0)
    assert result["vy"][-1] == pytest.approx(-6.636363636363637)


def test_solve_projectile_motion_no_drag_conserves_energy_for_sampled_points() -> None:
    parameters = make_parameters(time_step=0.05)

    result = solve_projectile_motion_no_drag(parameters)

    assert_allclose(result["E"][:-1], result["E"][0], rtol=1e-12, atol=1e-12)


def test_solve_projectile_motion_linear_drag_returns_valid_result() -> None:
    parameters = make_parameters(
        wind_speed=3.0,
        wind_angle_degrees=180.0,
    )

    result = solve_projectile_motion_linear_drag(parameters)

    assert_valid_projectile_result(result)
    assert result["x"][0] == pytest.approx(parameters.initial_x)
    assert result["y"][0] == pytest.approx(parameters.initial_y)
    assert result["vx"][0] == pytest.approx(parameters.vx0)
    assert result["vy"][0] == pytest.approx(parameters.vy0)


def test_solve_projectile_motion_quadratic_drag_returns_valid_result() -> None:
    parameters = make_parameters(
        wind_speed=2.0,
        wind_angle_degrees=90.0,
    )

    result = solve_projectile_motion_quadratic_drag(parameters)

    assert_valid_projectile_result(result)
    assert result["x"][0] == pytest.approx(parameters.initial_x)
    assert result["y"][0] == pytest.approx(parameters.initial_y)
    assert result["vx"][0] == pytest.approx(parameters.vx0)
    assert result["vy"][0] == pytest.approx(parameters.vy0)


def test_quadratic_drag_solver_matches_no_drag_solver_when_drag_is_zero() -> None:
    parameters = make_parameters(
        drag_coefficient=0.0,
        time_step=0.05,
    )

    no_drag = solve_projectile_motion_no_drag(parameters)
    quadratic_drag = solve_projectile_motion_quadratic_drag(parameters)

    assert set(quadratic_drag) == set(no_drag)

    for key in RESULT_KEYS:
        assert_allclose(
            quadratic_drag[key],
            no_drag[key],
            rtol=1e-12,
            atol=1e-12,
        )


@pytest.mark.parametrize(
    ("solver", "message"),
    [
        (
            solve_projectile_motion_no_drag,
            "No-drag projectile did not hit the ground",
        ),
        (
            solve_projectile_motion_linear_drag,
            "Linear-drag projectile did not hit the ground",
        ),
        (
            solve_projectile_motion_quadratic_drag,
            "Quadratic-drag projectile did not hit the ground",
        ),
    ],
)
def test_solver_raises_when_projectile_does_not_hit_ground_before_time_max(
    solver: Solver,
    message: str,
) -> None:
    parameters = make_parameters(
        initial_velocity=50.0,
        initial_angle_degrees=90.0,
        time_step=0.1,
        time_max=0.2,
    )

    with pytest.raises(ValueError, match=message):
        solver(parameters)


@pytest.mark.parametrize(
    "solver",
    [
        solve_projectile_motion_no_drag,
        solve_projectile_motion_linear_drag,
        solve_projectile_motion_quadratic_drag,
    ],
)
def test_solver_returns_single_sample_for_horizontal_launch_from_ground(
    solver: Solver,
) -> None:
    parameters = make_parameters(
        initial_angle_degrees=0.0,
        initial_y=0.0,
    )

    result = solver(parameters)

    assert_valid_projectile_result(result)
    assert_array_equal(
        result["t"],
        np.array([0.0], dtype=np.float64),
    )
    assert_array_equal(
        result["y"],
        np.array([0.0], dtype=np.float64),
    )
