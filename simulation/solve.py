import numpy as np

from config.parameters import X0, Y0, VX0, VY0, DT
from simulation.integrators import euler_step
from physics.interpolation import interpolate_ground_hit


def solve_projectile_motion():
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
        current_state = (x[i], y[i], vx[i], vy[i])
        x_new, y_new, vx_new, vy_new = euler_step(current_state)

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

    print("Quadratic drag - Euler")
    print(f"flight time = {t_hit}")
    print(f"range = {x_hit}")

    index_max_height = np.argmax(y)
    print(f"max height = {max(y)}")
    print(f"time at max height = {time[index_max_height]}")

    print(
        f"last above the ground: {time[last_index - 1], x[last_index - 1], y[last_index - 1]}"
    )
    print(f"first below ground: {time[last_index], x[last_index], y[last_index]}")
