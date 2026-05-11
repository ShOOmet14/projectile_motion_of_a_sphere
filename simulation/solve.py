import numpy as np
import numpy.typing as npt

from config.parameters import X0, Y0, VX0, VY0, T_MAX, DT

from physics.no_drag import calculate_position_no_drag, calculate_velocity_no_drag
from physics.linear_drag import (
    calculate_position_linear_drag,
    calculate_velocity_linear_drag,
)
from physics.quadratic_drag import runge_kutta_method


time = np.arange(0, T_MAX, DT)


def interpolate_ground_hit(
    time_1: float, x1: float, y1: float, time_2: float, x2: float, y2: float
) -> tuple[float, float]:
    x_hit = x1 + (-y1 / (y2 - y1)) * (x2 - x1)
    t_hit = time_1 + (-y1 / (y2 - y1)) * (time_2 - time_1)

    return (x_hit, t_hit)


def solve_projectile_motion_no_drag() -> tuple[npt.NDArray[np.float64], ...]:
    x, y = calculate_position_no_drag(time, X0, Y0, VX0, VY0)
    vx, vy = calculate_velocity_no_drag(time, VX0, VY0)

    first_negative_index = np.where(y < 0)[0][0]
    first_negative_index = int(first_negative_index)

    x_hit, t_hit = interpolate_ground_hit(
        time[first_negative_index - 1],
        x[first_negative_index - 1],
        y[first_negative_index - 1],
        time[first_negative_index],
        x[first_negative_index],
        y[first_negative_index],
    )

    mask = y >= 0
    # time_no_drag = time[mask]
    x = x[mask]
    y = y[mask]
    vx = vx[mask]
    vy = vy[mask]

    print(f"interpolated no drag flight time = {t_hit} ")
    print(f"interpolated no drag range = {x_hit} ")
    print(f"max_height no drag = {max(y)} ")

    return x, y


def solve_projectile_motion_linear_drag() -> tuple[npt.NDArray[np.float64], ...]:
    x, y = calculate_position_linear_drag(time, X0, Y0, VX0, VY0)
    vx, vy = calculate_velocity_linear_drag(time, VX0, VY0)

    first_negative_index = np.where(y < 0)[0][0]
    first_negative_index = int(first_negative_index)

    x_hit, t_hit = interpolate_ground_hit(
        time[first_negative_index - 1],
        x[first_negative_index - 1],
        y[first_negative_index - 1],
        time[first_negative_index],
        x[first_negative_index],
        y[first_negative_index],
    )

    mask = y >= 0
    # time_linear = time[mask]
    x = x[mask]
    y = y[mask]
    vx = vx[mask]
    vy = vy[mask]

    print(f"interpolated linear flight time = {t_hit} ")
    print(f"interpolated linear range = {x_hit} ")
    print(f"max_height linear = {max(y)} ")

    return x, y


def solve_projectile_motion_quadratic_drag() -> tuple[npt.NDArray[np.float64], ...]:
    x: list[float] = []
    y: list[float] = []
    vx: list[float] = []
    vy: list[float] = []

    x.append(X0)
    y.append(Y0)
    vx.append(VX0)
    vy.append(VY0)

    i = 0

    while True:
        current_state = np.array([x[i], y[i], vx[i], vy[i]], dtype=np.float64)
        x_new, y_new, vx_new, vy_new = runge_kutta_method(current_state)

        x.append(x_new)
        y.append(y_new)
        vx.append(vx_new)
        vy.append(vy_new)

        if y_new < 0:
            break

        i += 1

    last_index = len(x) - 1

    x_hit, t_hit = interpolate_ground_hit(
        time[last_index - 1],
        x[last_index - 1],
        y[last_index - 1],
        time[last_index],
        x[last_index],
        y[last_index],
    )

    print("Quadratic drag - Runge-Kutta method")
    print(f"flight time = {t_hit}")
    print(f"range = {x_hit}")
    print(f"max height = {max(y)}")

    return np.array(x, dtype=np.float64), np.array(y, dtype=np.float64)
