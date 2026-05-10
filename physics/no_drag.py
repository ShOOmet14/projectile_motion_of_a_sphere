import numpy.typing as npt
import numpy as np


def calculate_position_no_drag(
    time: npt.NDArray[np.float64],
    x0: float,
    y0: float,
    vx0: float,
    vy0: float,
    g: float,
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    position_x = x0 + vx0 * time
    position_y = y0 + vy0 * time - 0.5 * g * time * time

    return (position_x, position_y)


def calculate_velocity_no_drag(
    time: npt.NDArray[np.float64], vx0: float, vy0: float, g: float
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    velocity_x = np.full_like(time, vx0)
    velocity_y = vy0 - g * time

    return (velocity_x, velocity_y)
