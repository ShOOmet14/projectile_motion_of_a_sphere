import numpy as np
import numpy.typing as npt


def calculate_position_linear_drag(
    time: npt.NDArray[np.float64],
    x0: float,
    y0: float,
    vx0: float,
    vy0: float,
    k: float,
    g: float,
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    position_x = x0 + vx0 * (1.0 - np.exp(-k * time)) / k

    position_y = y0 + (vy0 + g / k) * (1.0 - np.exp(-k * time)) / k - g * time / k

    return position_x, position_y


def calculate_velocity_linear_drag(
    time: npt.NDArray[np.float64],
    vx0: float,
    vy0: float,
    k: float,
    g: float,
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    velocity_x = vx0 * np.exp(-k * time)
    velocity_y = (vy0 + g / k) * np.exp(-k * time) - g / k

    return velocity_x, velocity_y
