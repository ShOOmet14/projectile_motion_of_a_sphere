import numpy.typing as npt
import numpy as np

from config.parameters import LINEAR_DRAG_CONST, G


def calculate_position_linear_drag(
    time: npt.NDArray[np.float64], x0: float, y0: float, vx0: float, vy0: float
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    position_x = (
        x0 + vx0 * (1 - np.e ** (-LINEAR_DRAG_CONST * time)) / LINEAR_DRAG_CONST
    )
    position_y = (
        y0
        + (vy0 + G / LINEAR_DRAG_CONST)
        * (1 - np.e ** (-LINEAR_DRAG_CONST * time))
        / LINEAR_DRAG_CONST
        - G * time / LINEAR_DRAG_CONST
    )

    return (position_x, position_y)


def calculate_velocity_linear_drag(
    time: npt.NDArray[np.float64], vx0: float, vy0: float
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    velocity_x = vx0 * np.e ** (-LINEAR_DRAG_CONST * time)
    velocity_y = (vy0 + G / LINEAR_DRAG_CONST) * np.e ** (
        -LINEAR_DRAG_CONST * time
    ) - G / LINEAR_DRAG_CONST

    return (velocity_x, velocity_y)
