"""Solve projectile motion with no drag, linear drag, or quadratic drag.

The no-drag and linear-drag models use analytical equations evaluated on a regular time grid. The quadratic-drag model has no simple closed-form solution, so it is integrated numerically using the fourth-order Runge–Kutta method.

Each solver returns the trajectory until the projectile reaches ground level. The exact ground-hit point is estimated by linear interpolation between the last sample above ground and the first sample below ground.
"""

from typing import TypedDict

import numpy as np
import numpy.typing as npt

from src.config.parameters import DEFAULT_PARAMETERS, Parameters

# Type aliases
FloatArray = npt.NDArray[np.float64]


class ProjectileResult(TypedDict):
    """Store sampled trajectory values and derived energy values."""

    t: FloatArray
    x: FloatArray
    y: FloatArray
    vx: FloatArray
    vy: FloatArray
    v: FloatArray
    Ek: FloatArray
    Ep: FloatArray
    E: FloatArray


TrajectoryArrays = tuple[
    FloatArray,
    FloatArray,
    FloatArray,
    FloatArray,
    FloatArray,
]


def calculate_position_no_drag(
    time: FloatArray,
    x0: float,
    y0: float,
    vx0: float,
    vy0: float,
    g: float,
) -> tuple[FloatArray, FloatArray]:
    """Return analytical projectile positions without air resistance."""

    position_x = x0 + vx0 * time
    position_y = y0 + vy0 * time - 0.5 * g * time**2

    return position_x, position_y


def calculate_velocity_no_drag(
    time: FloatArray,
    vx0: float,
    vy0: float,
    g: float,
) -> tuple[FloatArray, FloatArray]:
    """Return analytical projectile velocities without air resistance."""

    velocity_x = np.full_like(time, vx0)
    velocity_y = vy0 - g * time

    return velocity_x, velocity_y


def calculate_position_linear_drag(
    time: FloatArray,
    x0: float,
    y0: float,
    vx0: float,
    vy0: float,
    k: float,
    g: float,
    wind_vx: float,
    wind_vy: float,
) -> tuple[FloatArray, FloatArray]:
    """Return analytical projectile positions with linear drag and wind."""

    decay = np.exp(-k * time)
    position_x = x0 + wind_vx * time + (vx0 - wind_vx) * (1.0 - decay) / k
    position_y = (
        y0 + (wind_vy - g / k) * time + (vy0 - wind_vy + g / k) * (1.0 - decay) / k
    )

    return position_x, position_y


def calculate_velocity_linear_drag(
    time: npt.NDArray[np.float64],
    vx0: float,
    vy0: float,
    k: float,
    g: float,
    wind_vx: float,
    wind_vy: float,
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """Return analytical projectile velocities with linear drag and wind."""

    decay = np.exp(-k * time)

    velocity_x = wind_vx + (vx0 - wind_vx) * decay
    velocity_y = wind_vy - g / k + (vy0 - wind_vy + g / k) * decay

    return velocity_x, velocity_y


def calculate_quadratic_drag_derivative(
    state: FloatArray,
    q: float,
    g: float,
    wind_vx: float,
    wind_vy: float,
) -> FloatArray:
    """Return the derivative of the quadratic-drag state vector.

    The state vector contains ``[x, y, vx, vy]``. The returned derivative
    contains ``[vx, vy, ax, ay]``. Drag is calculated relative to the wind
    velocity rather than relative to the ground.
    """

    _, _, vx, vy = state

    relative_vx = vx - wind_vx
    relative_vy = vy - wind_vy
    relative_speed = np.hypot(relative_vx, relative_vy)

    ax = -q * relative_speed * relative_vx
    ay = -g - q * relative_speed * relative_vy

    return np.array([vx, vy, ax, ay], dtype=np.float64)


def runge_kutta_step(
    state_old: FloatArray,
    dt: float,
    q: float,
    g: float,
    wind_vx: float,
    wind_vy: float,
) -> FloatArray:
    """Advance the quadratic-drag state by one RK4 integration step."""

    k1 = calculate_quadratic_drag_derivative(state_old, q, g, wind_vx, wind_vy)

    k2 = calculate_quadratic_drag_derivative(
        state_old + dt * k1 / 2.0, q, g, wind_vx, wind_vy
    )

    k3 = calculate_quadratic_drag_derivative(
        state_old + dt * k2 / 2.0, q, g, wind_vx, wind_vy
    )

    k4 = calculate_quadratic_drag_derivative(
        state_old + dt * k3, q, g, wind_vx, wind_vy
    )

    return state_old + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0


def interpolate_value_at_ground(
    value_1: float,
    value_2: float,
    y1: float,
    y2: float,
) -> float:
    """Linearly interpolate a sampled value at the point where height reaches zero."""

    return value_1 + (-y1 / (y2 - y1)) * (value_2 - value_1)


def calculate_speed(
    vx: FloatArray,
    vy: FloatArray,
) -> FloatArray:
    """Return speed magnitudes calculated from horizontal and vertical velocity."""

    return np.hypot(vx, vy)


def calculate_kinetic_energy(
    speed: FloatArray,
    mass: float,
) -> FloatArray:
    """Return kinetic energy values."""

    return 0.5 * mass * speed**2


def calculate_potential_energy(
    y: FloatArray,
    mass: float,
    g: float,
) -> FloatArray:
    """Return gravitational potential energy values relative to ground level."""

    return mass * g * y


def calculate_mechanical_energy(
    kinetic_energy: FloatArray,
    potential_energy: FloatArray,
) -> FloatArray:
    """Return total mechanical energy values."""

    return kinetic_energy + potential_energy


def _build_projectile_result(
    time: FloatArray,
    x: FloatArray,
    y: FloatArray,
    vx: FloatArray,
    vy: FloatArray,
    mass: float,
    g: float,
) -> ProjectileResult:
    """Build a complete solver result from sampled position and velocity arrays."""

    speed = calculate_speed(vx, vy)
    kinetic_energy = calculate_kinetic_energy(speed, mass)
    potential_energy = calculate_potential_energy(y, mass, g)
    mechanical_energy = calculate_mechanical_energy(
        kinetic_energy,
        potential_energy,
    )

    return {
        "t": time,
        "x": x,
        "y": y,
        "vx": vx,
        "vy": vy,
        "v": speed,
        "Ek": kinetic_energy,
        "Ep": potential_energy,
        "E": mechanical_energy,
    }


def _truncate_trajectory_at_ground(
    time: FloatArray,
    x: FloatArray,
    y: FloatArray,
    vx: FloatArray,
    vy: FloatArray,
    model_name: str,
) -> TrajectoryArrays:
    """Trim samples below ground and append an interpolated ground-hit sample."""

    below_ground_indices = np.flatnonzero(y < 0.0)

    if len(below_ground_indices) == 0:
        raise ValueError(
            f"{model_name} projectile did not hit the ground. "
            "Increase parameters.t_max."
        )

    first_below_ground_index = int(below_ground_indices[0])
    previous_index = first_below_ground_index - 1

    y_before_hit = y[previous_index]

    if y_before_hit == 0.0:
        return (
            time[:first_below_ground_index],
            x[:first_below_ground_index],
            y[:first_below_ground_index],
            vx[:first_below_ground_index],
            vy[:first_below_ground_index],
        )

    y_after_hit = y[first_below_ground_index]

    time_hit = interpolate_value_at_ground(
        time[previous_index],
        time[first_below_ground_index],
        y_before_hit,
        y_after_hit,
    )

    x_hit = interpolate_value_at_ground(
        x[previous_index],
        x[first_below_ground_index],
        y_before_hit,
        y_after_hit,
    )

    vx_hit = interpolate_value_at_ground(
        vx[previous_index],
        vx[first_below_ground_index],
        y_before_hit,
        y_after_hit,
    )

    vy_hit = interpolate_value_at_ground(
        vy[previous_index],
        vy[first_below_ground_index],
        y_before_hit,
        y_after_hit,
    )

    return (
        np.append(time[:first_below_ground_index], time_hit),
        np.append(x[:first_below_ground_index], x_hit),
        np.append(y[:first_below_ground_index], 0.0),
        np.append(vx[:first_below_ground_index], vx_hit),
        np.append(vy[:first_below_ground_index], vy_hit),
    )


def solve_projectile_motion_no_drag(
    parameters: Parameters = DEFAULT_PARAMETERS,
) -> ProjectileResult:
    """Solve projectile motion analytically without air resistance."""

    time = np.arange(
        0.0,
        parameters.time_max,
        parameters.time_step,
        dtype=np.float64,
    )

    x, y = calculate_position_no_drag(
        time,
        parameters.initial_x,
        parameters.initial_y,
        parameters.vx0,
        parameters.vy0,
        parameters.g,
    )

    vx, vy = calculate_velocity_no_drag(
        time,
        parameters.vx0,
        parameters.vy0,
        parameters.g,
    )

    time, x, y, vx, vy = _truncate_trajectory_at_ground(
        time,
        x,
        y,
        vx,
        vy,
        model_name="No-drag",
    )

    return _build_projectile_result(
        time,
        x,
        y,
        vx,
        vy,
        parameters.mass,
        parameters.g,
    )


def solve_projectile_motion_linear_drag(
    parameters: Parameters = DEFAULT_PARAMETERS,
) -> ProjectileResult:
    """Solve projectile motion analytically with linear drag and wind."""

    time = np.arange(
        0.0,
        parameters.time_max,
        parameters.time_step,
        dtype=np.float64,
    )

    x, y = calculate_position_linear_drag(
        time,
        parameters.initial_x,
        parameters.initial_y,
        parameters.vx0,
        parameters.vy0,
        parameters.linear_drag_factor,
        parameters.g,
        parameters.wind_vx,
        parameters.wind_vy,
    )

    vx, vy = calculate_velocity_linear_drag(
        time,
        parameters.vx0,
        parameters.vy0,
        parameters.linear_drag_factor,
        parameters.g,
        parameters.wind_vx,
        parameters.wind_vy,
    )

    time, x, y, vx, vy = _truncate_trajectory_at_ground(
        time,
        x,
        y,
        vx,
        vy,
        model_name="Linear-drag",
    )

    return _build_projectile_result(
        time,
        x,
        y,
        vx,
        vy,
        parameters.mass,
        parameters.g,
    )


def solve_projectile_motion_quadratic_drag(
    parameters: Parameters = DEFAULT_PARAMETERS,
) -> ProjectileResult:
    """Solve projectile motion numerically with quadratic drag and wind."""

    time_values: list[float] = [0.0]
    x_values: list[float] = [parameters.initial_x]
    y_values: list[float] = [parameters.initial_y]
    vx_values: list[float] = [parameters.vx0]
    vy_values: list[float] = [parameters.vy0]

    while True:
        current_state = np.array(
            [
                x_values[-1],
                y_values[-1],
                vx_values[-1],
                vy_values[-1],
            ],
            dtype=np.float64,
        )

        x_new, y_new, vx_new, vy_new = runge_kutta_step(
            current_state,
            parameters.time_step,
            parameters.quadratic_drag_factor,
            parameters.g,
            parameters.wind_vx,
            parameters.wind_vy,
        )

        time_values.append(time_values[-1] + parameters.time_step)
        x_values.append(x_new)
        y_values.append(y_new)
        vx_values.append(vx_new)
        vy_values.append(vy_new)

        if y_new < 0:
            break

        if time_values[-1] >= parameters.time_max:
            raise ValueError(
                "Quadratic-drag projectile did not hit the ground. "
                "Increase parameters.t_max."
            )

    time = np.array(time_values, dtype=np.float64)
    x = np.array(x_values, dtype=np.float64)
    y = np.array(y_values, dtype=np.float64)
    vx = np.array(vx_values, dtype=np.float64)
    vy = np.array(vy_values, dtype=np.float64)

    time, x, y, vx, vy = _truncate_trajectory_at_ground(
        time,
        x,
        y,
        vx,
        vy,
        model_name="Quadratic-drag",
    )

    return _build_projectile_result(
        time,
        x,
        y,
        vx,
        vy,
        parameters.mass,
        parameters.g,
    )
