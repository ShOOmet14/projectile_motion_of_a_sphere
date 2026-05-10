import numpy as np
import numpy.typing as npt

from config.parameters import X0, Y0, VX0, VY0, DT
from simulation.integrators import runge_kutta_method
from physics.interpolation import interpolate_ground_hit


def solve_projectile_motion() -> tuple[npt.NDArray[np.float64], ...]:
    time: list[float] = []
    x: list[float] = []
    y: list[float] = []
    vx: list[float] = []
    vy: list[float] = []

    time.append(0)
    x.append(X0)
    y.append(Y0)
    vx.append(VX0)
    vy.append(VY0)

    i = 0

    while True:
        current_state = np.array([x[i], y[i], vx[i], vy[i]], dtype=np.float64)
        x_new, y_new, vx_new, vy_new = runge_kutta_method(current_state)

        time.append(time[i] + DT)
        x.append(x_new)
        y.append(y_new)
        vx.append(vx_new)
        vy.append(vy_new)

        if y_new < 0:
            break

        i += 1

    last_index = len(time) - 1

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
