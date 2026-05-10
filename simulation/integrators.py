import numpy as np
import numpy.typing as npt

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


def state_derivative(
    state: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    _, _, vx, vy = state

    v = np.sqrt(vx * vx + vy * vy)

    return np.array(
        [
            vx,
            vy,
            -QUADRATIC_DRAG_CONSTANT * v * vx,
            -G - QUADRATIC_DRAG_CONSTANT * v * vy,
        ],
        dtype=np.float64,
    )


def runge_kutta_method(
    state_old: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:

    k1 = state_derivative(state_old)
    k2 = state_derivative(state_old + DT * k1 / 2)
    k3 = state_derivative(state_old + DT * k2 / 2)
    k4 = state_derivative(state_old + DT * k3)

    state_new = state_old + DT * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return state_new
