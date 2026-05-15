import numpy as np
import numpy.typing as npt


def calculate_state_quadratic_drag(
    state: npt.NDArray[np.float64],
    q: float,
    g: float,
) -> npt.NDArray[np.float64]:
    _, _, vx, vy = state

    v = np.hypot(vx, vy)

    ax = -q * v * vx
    ay = -g - q * v * vy

    return np.array([vx, vy, ax, ay], dtype=np.float64)


def runge_kutta_method(
    state_old: npt.NDArray[np.float64],
    dt: float,
    q: float,
    g: float,
) -> npt.NDArray[np.float64]:
    k1 = calculate_state_quadratic_drag(state_old, q, g)
    k2 = calculate_state_quadratic_drag(state_old + dt * k1 / 2.0, q, g)
    k3 = calculate_state_quadratic_drag(state_old + dt * k2 / 2.0, q, g)
    k4 = calculate_state_quadratic_drag(state_old + dt * k3, q, g)

    state_new = state_old + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0

    return state_new
