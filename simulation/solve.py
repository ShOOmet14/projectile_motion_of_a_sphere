import numpy as np
import numpy.typing as npt

from config.parameters import X0, Y0, VX0, VY0, T_MAX, DT, MASS, G

from physics.no_drag import calculate_position_no_drag, calculate_velocity_no_drag
from physics.linear_drag import (
    calculate_position_linear_drag,
    calculate_velocity_linear_drag,
)
from physics.quadratic_drag import runge_kutta_method


time = np.arange(0, T_MAX, DT)


def interpolate_value_at_ground(
    value_1: float,
    value_2: float,
    y1: float,
    y2: float,
) -> float:
    value_hit = value_1 + (-y1 / (y2 - y1)) * (value_2 - value_1)

    return value_hit


def calculate_speed(
    vx: npt.NDArray[np.float64],
    vy: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    speed = np.hypot(vx, vy)  # note to myself: this is the same as sqrt(vx*vx + vy*vy)

    return speed


def calculate_kinetic_energy(
    speed: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    kinetic_energy = 0.5 * MASS * speed * speed

    return kinetic_energy


def calculate_potential_energy(
    y: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    potential_energy = MASS * G * y

    return potential_energy


def calculate_mechanical_energy(
    kinetic_energy: npt.NDArray[np.float64],
    potential_energy: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    mechanical_energy = kinetic_energy + potential_energy

    return mechanical_energy


def solve_projectile_motion_no_drag() -> tuple[
    npt.NDArray[np.float64],
    npt.NDArray[np.float64],
    npt.NDArray[np.float64],
    npt.NDArray[np.float64],
]:
    x, y = calculate_position_no_drag(time, X0, Y0, VX0, VY0)
    vx, vy = calculate_velocity_no_drag(time, VX0, VY0)

    negative_indices = np.where(y < 0)[0]
    if len(negative_indices) == 0:
        raise ValueError("No-drag projectile did not hit the ground. Increase T_MAX.")

    first_negative_index = int(negative_indices[0])

    x_hit = interpolate_value_at_ground(
        x[first_negative_index - 1],
        x[first_negative_index],
        y[first_negative_index - 1],
        y[first_negative_index],
    )

    t_hit = interpolate_value_at_ground(
        time[first_negative_index - 1],
        time[first_negative_index],
        y[first_negative_index - 1],
        y[first_negative_index],
    )

    vx_hit = interpolate_value_at_ground(
        vx[first_negative_index - 1],
        vx[first_negative_index],
        y[first_negative_index - 1],
        y[first_negative_index],
    )

    vy_hit = interpolate_value_at_ground(
        vy[first_negative_index - 1],
        vy[first_negative_index],
        y[first_negative_index - 1],
        y[first_negative_index],
    )

    mask = y >= 0

    time_no_drag = np.append(time[mask], t_hit)
    x = np.append(x[mask], x_hit)
    y = np.append(y[mask], 0.0)
    vx = np.append(vx[mask], vx_hit)
    vy = np.append(vy[mask], vy_hit)

    print("No drag")
    print(f"interpolated flight time = {t_hit}")
    print(f"interpolated range = {x_hit}")
    print(f"max height = {max(y)}")

    speed = calculate_speed(vx, vy)
    kinetic_energy = calculate_kinetic_energy(speed)
    potential_energy = calculate_potential_energy(y)

    mechanical_energy = calculate_mechanical_energy(kinetic_energy, potential_energy)

    print(f"initial energy = {mechanical_energy[0]}")
    print(f"max energy = {max(mechanical_energy)}")
    print(f"min energy = {min(mechanical_energy)}")
    print(f"final energy = {mechanical_energy[-1]}")

    return x, y, time_no_drag, mechanical_energy


def solve_projectile_motion_linear_drag() -> tuple[
    npt.NDArray[np.float64],
    npt.NDArray[np.float64],
    npt.NDArray[np.float64],
    npt.NDArray[np.float64],
]:
    x, y = calculate_position_linear_drag(time, X0, Y0, VX0, VY0)
    vx, vy = calculate_velocity_linear_drag(time, VX0, VY0)

    negative_indices = np.where(y < 0)[0]
    if len(negative_indices) == 0:
        raise ValueError(
            "Linear-drag projectile did not hit the ground. Increase T_MAX."
        )

    first_negative_index = int(negative_indices[0])

    x_hit = interpolate_value_at_ground(
        x[first_negative_index - 1],
        x[first_negative_index],
        y[first_negative_index - 1],
        y[first_negative_index],
    )

    t_hit = interpolate_value_at_ground(
        time[first_negative_index - 1],
        time[first_negative_index],
        y[first_negative_index - 1],
        y[first_negative_index],
    )

    vx_hit = interpolate_value_at_ground(
        vx[first_negative_index - 1],
        vx[first_negative_index],
        y[first_negative_index - 1],
        y[first_negative_index],
    )

    vy_hit = interpolate_value_at_ground(
        vy[first_negative_index - 1],
        vy[first_negative_index],
        y[first_negative_index - 1],
        y[first_negative_index],
    )

    mask = y >= 0

    time_linear = np.append(time[mask], t_hit)
    x = np.append(x[mask], x_hit)
    y = np.append(y[mask], 0.0)
    vx = np.append(vx[mask], vx_hit)
    vy = np.append(vy[mask], vy_hit)

    print("Linear drag")
    print(f"interpolated flight time = {t_hit}")
    print(f"interpolated range = {x_hit}")
    print(f"max height = {max(y)}")

    speed = calculate_speed(vx, vy)
    kinetic_energy = calculate_kinetic_energy(speed)
    potential_energy = calculate_potential_energy(y)

    mechanical_energy = calculate_mechanical_energy(kinetic_energy, potential_energy)

    print(f"initial energy = {mechanical_energy[0]}")
    print(f"max energy = {max(mechanical_energy)}")
    print(f"min energy = {min(mechanical_energy)}")
    print(f"final energy = {mechanical_energy[-1]}")

    return x, y, time_linear, mechanical_energy


def solve_projectile_motion_quadratic_drag() -> tuple[
    npt.NDArray[np.float64],
    npt.NDArray[np.float64],
    npt.NDArray[np.float64],
    npt.NDArray[np.float64],
]:
    time_quadratic: list[float] = [0.0]
    x: list[float] = [X0]
    y: list[float] = [Y0]
    vx: list[float] = [VX0]
    vy: list[float] = [VY0]

    while True:
        current_state = np.array([x[-1], y[-1], vx[-1], vy[-1]], dtype=np.float64)
        x_new, y_new, vx_new, vy_new = runge_kutta_method(current_state)

        time_quadratic.append(time_quadratic[-1] + DT)
        x.append(x_new)
        y.append(y_new)
        vx.append(vx_new)
        vy.append(vy_new)

        if y_new < 0:
            break

        if time_quadratic[-1] >= T_MAX:
            raise ValueError(
                "Quadratic-drag projectile did not hit the ground. Increase T_MAX."
            )

    x_hit = interpolate_value_at_ground(
        x[-2],
        x[-1],
        y[-2],
        y[-1],
    )

    t_hit = interpolate_value_at_ground(
        time_quadratic[-2],
        time_quadratic[-1],
        y[-2],
        y[-1],
    )

    vx_hit = interpolate_value_at_ground(
        vx[-2],
        vx[-1],
        y[-2],
        y[-1],
    )

    vy_hit = interpolate_value_at_ground(
        vy[-2],
        vy[-1],
        y[-2],
        y[-1],
    )

    x[-1] = x_hit
    y[-1] = 0.0
    vx[-1] = vx_hit
    vy[-1] = vy_hit
    time_quadratic[-1] = t_hit

    x_as_array = np.array(x, dtype=np.float64)
    y_as_array = np.array(y, dtype=np.float64)
    vx_as_array = np.array(vx, dtype=np.float64)
    vy_as_array = np.array(vy, dtype=np.float64)
    time_as_array = np.array(time_quadratic, dtype=np.float64)

    print("Quadratic drag - Runge-Kutta method")
    print(f"flight time = {t_hit}")
    print(f"range = {x_hit}")
    print(f"max height = {max(y_as_array)}")

    speed = calculate_speed(vx_as_array, vy_as_array)
    kinetic_energy = calculate_kinetic_energy(speed)
    potential_energy = calculate_potential_energy(y_as_array)

    mechanical_energy = calculate_mechanical_energy(kinetic_energy, potential_energy)

    print(f"initial energy = {mechanical_energy[0]}")
    print(f"max energy = {max(mechanical_energy)}")
    print(f"min energy = {min(mechanical_energy)}")
    print(f"final energy = {mechanical_energy[-1]}")

    return x_as_array, y_as_array, time_as_array, mechanical_energy
