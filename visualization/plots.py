import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt


def plot_motion(
    x_no_drag: npt.NDArray[np.float64],
    y_no_drag: npt.NDArray[np.float64],
    x_linear: npt.NDArray[np.float64],
    y_linear: npt.NDArray[np.float64],
    x_quadratic: npt.NDArray[np.float64],
    y_quadratic: npt.NDArray[np.float64],
) -> None:
    _, axis = plt.subplots()

    axis.plot(x_no_drag, y_no_drag, label="No drag", color="red")
    axis.plot(x_linear, y_linear, label="Linear drag", color="blue")
    axis.plot(
        x_quadratic, y_quadratic, label="Quadratic drag Runge-Kutta", color="green"
    )

    axis.set_title("Projectile motion comparison.")
    axis.set_xlabel("x [m]")
    axis.set_ylabel("y [m]")

    axis.legend()
    axis.grid(True)

    plt.show()


def plot_energy(
    mechanical_energy_no_drag: npt.NDArray[np.float64],
    time_no_drag: npt.NDArray[np.float64],
    mechanical_energy_linear_drag: npt.NDArray[np.float64],
    time_linear_drag: npt.NDArray[np.float64],
    mechanical_energy_quadratic_drag: npt.NDArray[np.float64],
    time_quadratic_drag: npt.NDArray[np.float64],
) -> None:

    _, axis = plt.subplots()

    axis.plot(
        time_no_drag,
        mechanical_energy_no_drag,
        label="Mechanical energy no drag",
        color="red",
    )
    axis.plot(
        time_linear_drag,
        mechanical_energy_linear_drag,
        label="Mechanical energy linear drag",
        color="blue",
    )
    axis.plot(
        time_quadratic_drag,
        mechanical_energy_quadratic_drag,
        label="Mechanical energy quadratic drag",
        color="green",
    )

    axis.set_title("Projectile energy comparison.")
    axis.set_xlabel("t [s]")
    axis.set_ylabel("E [J]")

    axis.legend()
    axis.grid(True)

    plt.show()
