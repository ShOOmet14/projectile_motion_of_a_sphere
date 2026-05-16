from pathlib import Path

import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.text import Text

from simulation.solve import ProjectileResult


GIF_FRAMES = 180
GIF_FPS = 24
FIGURE_DPI = 100
FIGURE_SIZE = (8, 5)


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


def get_interpolated_positions(
    result: ProjectileResult,
    animation_time: npt.NDArray[np.float64],
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    x = np.interp(animation_time, result["t"], result["x"])
    y = np.interp(animation_time, result["t"], result["y"])

    return x, y


def get_max_axis_values(
    no_drag: ProjectileResult,
    linear_drag: ProjectileResult,
    quadratic_drag: ProjectileResult,
) -> tuple[float, float]:
    max_x = max(
        float(np.max(no_drag["x"])),
        float(np.max(linear_drag["x"])),
        float(np.max(quadratic_drag["x"])),
    )

    max_y = max(
        float(np.max(no_drag["y"])),
        float(np.max(linear_drag["y"])),
        float(np.max(quadratic_drag["y"])),
    )

    return max_x, max_y


def animate_projectile_motion(
    no_drag: ProjectileResult,
    linear_drag: ProjectileResult,
    quadratic_drag: ProjectileResult,
    save_path: str | Path,
) -> None:
    animation_time: npt.NDArray[np.float64] = np.linspace(
        0.0,
        float(no_drag["t"][-1]),
        GIF_FRAMES,
        dtype=np.float64,
    )

    no_drag_x, no_drag_y = get_interpolated_positions(no_drag, animation_time)
    linear_drag_x, linear_drag_y = get_interpolated_positions(
        linear_drag,
        animation_time,
    )
    quadratic_drag_x, quadratic_drag_y = get_interpolated_positions(
        quadratic_drag,
        animation_time,
    )

    max_x, max_y = get_max_axis_values(
        no_drag,
        linear_drag,
        quadratic_drag,
    )

    figure, axis = plt.subplots(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)

    axis.plot(
        no_drag["x"],
        no_drag["y"],
        label="No drag",
        color="red",
        linewidth=1.8,
        alpha=0.45,
    )

    axis.plot(
        linear_drag["x"],
        linear_drag["y"],
        label="Linear drag",
        color="blue",
        linewidth=1.8,
        alpha=0.45,
    )

    axis.plot(
        quadratic_drag["x"],
        quadratic_drag["y"],
        label="Quadratic drag RK4",
        color="green",
        linewidth=1.8,
        alpha=0.45,
    )

    no_drag_point = axis.plot(
        [],
        [],
        "o",
        color="red",
        markersize=7,
        markeredgecolor="black",
        markeredgewidth=0.7,
        label="_nolegend_",
    )[0]

    linear_drag_point = axis.plot(
        [],
        [],
        "o",
        color="blue",
        markersize=7,
        markeredgecolor="black",
        markeredgewidth=0.7,
        label="_nolegend_",
    )[0]

    quadratic_drag_point = axis.plot(
        [],
        [],
        "o",
        color="green",
        markersize=7,
        markeredgecolor="black",
        markeredgewidth=0.7,
        label="_nolegend_",
    )[0]

    time_text = axis.text(
        0.02,
        0.95,
        "",
        transform=axis.transAxes,
        fontsize=10,
        bbox={
            "facecolor": "white",
            "alpha": 0.75,
            "edgecolor": "none",
        },
    )

    axis.set_title("Projectile motion animation")
    axis.set_xlabel("x [m]")
    axis.set_ylabel("y [m]")
    axis.set_xlim(0.0, max_x * 1.05)
    axis.set_ylim(0.0, max_y * 1.10)
    axis.legend(loc="upper right")
    axis.grid(True, alpha=0.35)

    figure.tight_layout()

    def update(frame_index: int) -> tuple[Line2D, Line2D, Line2D, Text]:
        no_drag_point.set_data(
            [float(no_drag_x[frame_index])],
            [float(no_drag_y[frame_index])],
        )

        linear_drag_point.set_data(
            [float(linear_drag_x[frame_index])],
            [float(linear_drag_y[frame_index])],
        )

        quadratic_drag_point.set_data(
            [float(quadratic_drag_x[frame_index])],
            [float(quadratic_drag_y[frame_index])],
        )

        time_text.set_text(f"t = {animation_time[frame_index]:.2f} s")

        return no_drag_point, linear_drag_point, quadratic_drag_point, time_text

    animation = FuncAnimation(
        figure,
        update,
        frames=GIF_FRAMES,
        interval=1000 // GIF_FPS,
        blit=True,
    )

    animation.save(
        save_path,
        writer=PillowWriter(fps=GIF_FPS),
        dpi=FIGURE_DPI,
    )

    plt.close(figure)
