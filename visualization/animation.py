from pathlib import Path

import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.lines import Line2D
from matplotlib.text import Text

from simulation.solve import ProjectileResult


GIF_FRAMES = 360
GIF_FPS = 30
FIGURE_DPI = 150
FIGURE_SIZE = (10, 6)


def get_interpolated_position(
    result: ProjectileResult,
    animation_time: float,
) -> tuple[float, float]:
    x = float(np.interp(animation_time, result["t"], result["x"]))
    y = float(np.interp(animation_time, result["t"], result["y"]))

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
        0.0, float(no_drag["t"][-1]), GIF_FRAMES, dtype=np.float64
    )

    max_x, max_y = get_max_axis_values(no_drag, linear_drag, quadratic_drag)

    figure, axis = plt.subplots(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)

    axis.plot(
        no_drag["x"],
        no_drag["y"],
        label="No drag",
        color="red",
        linewidth=2.0,
        alpha=0.45,
    )

    axis.plot(
        linear_drag["x"],
        linear_drag["y"],
        label="Linear drag",
        color="blue",
        linewidth=2.0,
        alpha=0.45,
    )

    axis.plot(
        quadratic_drag["x"],
        quadratic_drag["y"],
        label="Quadratic drag RK4",
        color="green",
        linewidth=2.0,
        alpha=0.45,
    )

    no_drag_point = axis.plot([], [], "o", color="red", markersize=8)[0]

    linear_drag_point = axis.plot([], [], "o", color="blue", markersize=8)[0]

    quadratic_drag_point = axis.plot([], [], "o", color="green", markersize=8)[0]

    time_text = axis.text(
        0.02,
        0.95,
        "",
        transform=axis.transAxes,
        fontsize=11,
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
        current_time = float(animation_time[frame_index])

        x_no_drag, y_no_drag = get_interpolated_position(no_drag, current_time)
        x_linear, y_linear = get_interpolated_position(linear_drag, current_time)
        x_quadratic, y_quadratic = get_interpolated_position(
            quadratic_drag, current_time
        )

        no_drag_point.set_data([x_no_drag], [y_no_drag])
        linear_drag_point.set_data([x_linear], [y_linear])
        quadratic_drag_point.set_data([x_quadratic], [y_quadratic])

        time_text.set_text(f"t = {current_time:.2f} s")

        return no_drag_point, linear_drag_point, quadratic_drag_point, time_text

    animation = FuncAnimation(
        figure,
        update,
        frames=len(animation_time),
        interval=1000 // GIF_FPS,
        blit=True,
    )

    animation.save(
        save_path,
        writer=PillowWriter(fps=GIF_FPS),
        dpi=FIGURE_DPI,
    )

    plt.close(figure)
