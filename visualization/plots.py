import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt


def plot_motion_no_drag(
    x: npt.NDArray[np.float64], y: npt.NDArray[np.float64], title: str
) -> None:
    _, axis = plt.subplots()

    axis.plot(x, y)
    axis.set_title(title)
    axis.set_xlabel("x [m]")
    axis.set_ylabel("y [m]")
    axis.legend(title="No drag")
    axis.grid(True)

    plt.show()
