from pathlib import Path

import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt

from matplotlib.figure import Figure


def save_plot(figure: Figure, save_path: str | Path) -> None:
    figure.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close(figure)


def plot_motion(
    x_no_drag: npt.NDArray[np.float64],
    y_no_drag: npt.NDArray[np.float64],
    x_linear: npt.NDArray[np.float64],
    y_linear: npt.NDArray[np.float64],
    x_quadratic: npt.NDArray[np.float64],
    y_quadratic: npt.NDArray[np.float64],
    save_path: str | Path,
) -> None:
    figure, axis = plt.subplots()

    axis.plot(x_no_drag, y_no_drag, label="No drag", color="red")
    axis.plot(x_linear, y_linear, label="Linear drag", color="blue")
    axis.plot(
        x_quadratic,
        y_quadratic,
        label="Quadratic drag RK4",
        color="green",
    )

    axis.set_title("Trajectory comparison")
    axis.set_xlabel("x [m]")
    axis.set_ylabel("y [m]")

    axis.legend()
    axis.grid(True)

    save_plot(figure, save_path)


def plot_speed(
    speed_no_drag: npt.NDArray[np.float64],
    speed_linear: npt.NDArray[np.float64],
    speed_quadratic: npt.NDArray[np.float64],
    time_no_drag: npt.NDArray[np.float64],
    time_linear: npt.NDArray[np.float64],
    time_quadratic: npt.NDArray[np.float64],
    save_path: str | Path,
) -> None:
    figure, axis = plt.subplots()

    axis.plot(
        time_no_drag,
        speed_no_drag,
        label="No drag",
        color="red",
    )

    axis.plot(
        time_linear,
        speed_linear,
        label="Linear drag",
        color="blue",
    )

    axis.plot(
        time_quadratic,
        speed_quadratic,
        label="Quadratic drag RK4",
        color="green",
    )

    axis.set_title("Speed comparison")
    axis.set_xlabel("t [s]")
    axis.set_ylabel("v [m/s]")

    axis.legend()
    axis.grid(True)

    save_plot(figure, save_path)


def plot_energy(
    mechanical_energy_no_drag: npt.NDArray[np.float64],
    mechanical_energy_linear: npt.NDArray[np.float64],
    mechanical_energy_quadratic: npt.NDArray[np.float64],
    time_no_drag: npt.NDArray[np.float64],
    time_linear: npt.NDArray[np.float64],
    time_quadratic: npt.NDArray[np.float64],
    save_path: str | Path,
) -> None:
    figure, axis = plt.subplots()

    axis.plot(
        time_no_drag,
        mechanical_energy_no_drag,
        label="No drag",
        color="red",
    )

    axis.plot(
        time_linear,
        mechanical_energy_linear,
        label="Linear drag",
        color="blue",
    )

    axis.plot(
        time_quadratic,
        mechanical_energy_quadratic,
        label="Quadratic drag RK4",
        color="green",
    )

    axis.set_title("Mechanical energy comparison")
    axis.set_xlabel("t [s]")
    axis.set_ylabel("E [J]")

    axis.legend()
    axis.grid(True)

    save_plot(figure, save_path)
