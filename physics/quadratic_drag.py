import numpy as np
import numpy.typing as npt

from config.parameters import QUADRATIC_DRAG_CONSTANT, G, DT


def calculate_state_quadratic_drag(
    state: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    _, _, vx, vy = state

    v = np.sqrt(vx * vx + vy * vy)

    ax = -QUADRATIC_DRAG_CONSTANT * v * vx  # dvx / dt
    ay = -G - QUADRATIC_DRAG_CONSTANT * v * vy  # dvy / dt

    return np.array([vx, vy, ax, ay], dtype=np.float64)


def runge_kutta_method(
    state_old: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:

    k1 = calculate_state_quadratic_drag(state_old)
    k2 = calculate_state_quadratic_drag(state_old + DT * k1 / 2)
    k3 = calculate_state_quadratic_drag(state_old + DT * k2 / 2)
    k4 = calculate_state_quadratic_drag(state_old + DT * k3)

    state_new = state_old + DT * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return state_new
