import numpy as np
import numpy.typing as npt

from config.parameters import DT
from physics.quadratic_drag import calculate_state_quadratic_drag


def runge_kutta_method(
    state_old: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:

    k1 = calculate_state_quadratic_drag(state_old)
    k2 = calculate_state_quadratic_drag(state_old + DT * k1 / 2)
    k3 = calculate_state_quadratic_drag(state_old + DT * k2 / 2)
    k4 = calculate_state_quadratic_drag(state_old + DT * k3)

    state_new = state_old + DT * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return state_new
