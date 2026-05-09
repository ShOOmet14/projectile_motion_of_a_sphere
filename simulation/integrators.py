import numpy as np

from config.parameters import DT, QUADRATIC_DRAG_CONSTANT, G


def euler_step(
    state: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    x_old, y_old, vx_old, vy_old = state

    v_old = np.sqrt(vx_old * vx_old + vy_old * vy_old)

    x_new = x_old + DT * vx_old
    y_new = y_old + DT * vy_old
    vx_new = vx_old + DT * (-QUADRATIC_DRAG_CONSTANT * v_old * vx_old)
    vy_new = vy_old + DT * (-G - QUADRATIC_DRAG_CONSTANT * v_old * vy_old)

    return x_new, y_new, vx_new, vy_new
