import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt


def plot_motion(
    x_no_drag: npt.NDArray[np.float64],
    y_no_drag: npt.NDArray[np.float64],
    x_linear: npt.NDArray[np.float64],
    y_linear: npt.NDArray[np.float64],
) -> None:
    _, axis = plt.subplots()

    axis.plot(x_no_drag, y_no_drag, label="No drag", color="red")
    axis.plot(x_linear, y_linear, label="Linear drag", color="blue")

    axis.set_title("Linear drag against no drag in projectile motion of a sphere.")
    axis.set_xlabel("x [m]")
    axis.set_ylabel("y [m]")

    axis.legend()
    axis.grid(True)

    plt.show()
