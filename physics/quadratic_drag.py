import numpy as np
import numpy.typing as npt

from config.parameters import QUADRATIC_DRAG_CONSTANT, G


def calculate_state_quadratic_drag(
    state: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    _, _, vx, vy = state

    v = np.sqrt(vx * vx + vy * vy)

    ax = -QUADRATIC_DRAG_CONSTANT * v * vx  # dvx / dt
    ay = -G - QUADRATIC_DRAG_CONSTANT * v * vy  # dvy / dt

    return np.array([vx, vy, ax, ay], dtype=np.float64)
