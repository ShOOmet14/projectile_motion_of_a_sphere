"""Export static plots and GIF animations for projectile-motion results."""

from math import cos, sin
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch
from matplotlib.text import Text

from src.config.parameters import Parameters
from src.simulation.solve import ProjectileResult

FloatArray = npt.NDArray[np.float64]


GIF_FRAMES = 180
GIF_FPS = 24
FIGURE_DPI = 100
FIGURE_SIZE = (8, 5)


def _prepare_output_path(path: str | Path) -> Path:
    """Create missing parent directories and return a normalized output path."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    return output_path


def save_plot(figure: Figure, save_path: str | Path) -> None:
    """Save a figure as a high-resolution image and close it afterward."""

    output_path = _prepare_output_path(save_path)

    try:
        figure.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight",
        )
    finally:
        plt.close(figure)


def _get_wind_arrow_end(
    parameters: Parameters,
    start_x: float,
    start_y: float,
    length: float,
) -> tuple[float, float]:
    """Return the end point of a normalized wind-direction arrow."""

    dx = length * cos(parameters.wind_angle_radians)
    dy = length * sin(parameters.wind_angle_radians)

    return start_x + dx, start_y + dy


def _format_wind_label(parameters: Parameters) -> str:
    """Return a compact label describing wind speed and direction."""

    return (
        f"Wind: {parameters.wind_speed:.1f} m/s, {parameters.wind_angle_degrees:.0f}°"
    )


def draw_wind_vector_on_axis(axis: Axes, parameters: Parameters) -> None:
    if parameters.wind_speed <= 0:
        return

    start_x = 0.78
    start_y = 0.88
    length = 0.12

    end_x, end_y = _get_wind_arrow_end(
        parameters,
        start_x,
        start_y,
        length,
    )

    axis.annotate(
        "",
        xy=(end_x, end_y),
        xytext=(start_x, start_y),
        xycoords="axes fraction",
        arrowprops={
            "arrowstyle": "->",
            "linewidth": 2.5,
            "color": "black",
        },
    )

    axis.text(
        start_x,
        start_y - 0.07,
        _format_wind_label(parameters),
        transform=axis.transAxes,
        fontsize=9,
        bbox={
            "facecolor": "white",
            "alpha": 0.75,
            "edgecolor": "none",
        },
    )


def _draw_three_model_lines(
    axis: Axes,
    x_no_drag: FloatArray,
    y_no_drag: FloatArray,
    x_linear: FloatArray,
    y_linear: FloatArray,
    x_quadratic: FloatArray,
    y_quadratic: FloatArray,
) -> None:
    """Draw one comparison line for each projectile-motion model."""

    axis.plot(
        x_no_drag,
        y_no_drag,
        label="No drag",
        color="red",
    )

    axis.plot(
        x_linear,
        y_linear,
        label="Linear drag",
        color="blue",
    )

    axis.plot(
        x_quadratic,
        y_quadratic,
        label="Quadratic drag RK4",
        color="green",
    )


def _finish_comparison_plot(
    axis: Axes,
    title: str,
    x_label: str,
    y_label: str,
) -> None:
    """Apply common labels, legend, and grid settings to a comparison plot."""

    axis.set_title(title)
    axis.set_xlabel(x_label)
    axis.set_ylabel(y_label)
    axis.legend()
    axis.grid(True)


def plot_motion(
    x_no_drag: FloatArray,
    y_no_drag: FloatArray,
    x_linear: FloatArray,
    y_linear: FloatArray,
    x_quadratic: FloatArray,
    y_quadratic: FloatArray,
    parameters: Parameters,
    show_vectors: bool,
    save_path: str | Path,
) -> None:
    figure, axis = plt.subplots()

    _draw_three_model_lines(
        axis,
        x_no_drag,
        y_no_drag,
        x_linear,
        y_linear,
        x_quadratic,
        y_quadratic,
    )

    _finish_comparison_plot(
        axis,
        title="Trajectory comparison",
        x_label="x [m]",
        y_label="y [m]",
    )

    if show_vectors:
        draw_wind_vector_on_axis(axis, parameters)

    save_plot(figure, save_path)


def plot_speed(
    speed_no_drag: FloatArray,
    speed_linear: FloatArray,
    speed_quadratic: FloatArray,
    time_no_drag: FloatArray,
    time_linear: FloatArray,
    time_quadratic: FloatArray,
    save_path: str | Path,
) -> None:
    figure, axis = plt.subplots()

    _draw_three_model_lines(
        axis,
        time_no_drag,
        speed_no_drag,
        time_linear,
        speed_linear,
        time_quadratic,
        speed_quadratic,
    )

    _finish_comparison_plot(
        axis,
        title="Speed comparison",
        x_label="t [s]",
        y_label="v [m/s]",
    )

    save_plot(figure, save_path)


def plot_energy(
    mechanical_energy_no_drag: FloatArray,
    mechanical_energy_linear: FloatArray,
    mechanical_energy_quadratic: FloatArray,
    time_no_drag: FloatArray,
    time_linear: FloatArray,
    time_quadratic: FloatArray,
    save_path: str | Path,
) -> None:
    figure, axis = plt.subplots()

    _draw_three_model_lines(
        axis,
        time_no_drag,
        mechanical_energy_no_drag,
        time_linear,
        mechanical_energy_linear,
        time_quadratic,
        mechanical_energy_quadratic,
    )

    _finish_comparison_plot(
        axis,
        title="Mechanical energy comparison",
        x_label="t [s]",
        y_label="E [J]",
    )

    save_plot(figure, save_path)


def get_interpolated_positions(
    result: ProjectileResult,
    animation_time: FloatArray,
) -> tuple[FloatArray, FloatArray]:
    """Interpolate projectile positions at evenly spaced animation times."""

    x = np.interp(animation_time, result["t"], result["x"])
    y = np.interp(animation_time, result["t"], result["y"])

    return x, y


def get_interpolated_velocities(
    result: ProjectileResult,
    animation_time: FloatArray,
) -> tuple[FloatArray, FloatArray]:
    """Interpolate projectile velocities at evenly spaced animation times."""

    vx = np.interp(animation_time, result["t"], result["vx"])
    vy = np.interp(animation_time, result["t"], result["vy"])

    return vx, vy


def get_axis_limits(
    no_drag: ProjectileResult,
    linear_drag: ProjectileResult,
    quadratic_drag: ProjectileResult,
) -> tuple[float, float, float, float]:
    """Return padded axis limits that contain all three trajectories."""

    min_x = min(
        float(np.min(no_drag["x"])),
        float(np.min(linear_drag["x"])),
        float(np.min(quadratic_drag["x"])),
    )

    max_x = max(
        float(np.max(no_drag["x"])),
        float(np.max(linear_drag["x"])),
        float(np.max(quadratic_drag["x"])),
    )

    min_y = min(
        float(np.min(no_drag["y"])),
        float(np.min(linear_drag["y"])),
        float(np.min(quadratic_drag["y"])),
        0.0,
    )

    max_y = max(
        float(np.max(no_drag["y"])),
        float(np.max(linear_drag["y"])),
        float(np.max(quadratic_drag["y"])),
        1.0,
    )

    x_range = max(max_x - min_x, 1.0)
    y_range = max(max_y - min_y, 1.0)

    x_margin = x_range * 0.06
    y_margin = y_range * 0.10

    return (
        min_x - x_margin,
        max_x + x_margin,
        min_y - y_margin,
        max_y + y_margin,
    )


def get_velocity_scale(
    no_drag: ProjectileResult,
    linear_drag: ProjectileResult,
    quadratic_drag: ProjectileResult,
) -> float:
    """Return a scale factor that keeps velocity arrows visually readable."""

    x_min, x_max, _, _ = get_axis_limits(
        no_drag,
        linear_drag,
        quadratic_drag,
    )

    x_range = max(x_max - x_min, 1.0)

    max_speed = max(
        float(np.max(no_drag["v"])),
        float(np.max(linear_drag["v"])),
        float(np.max(quadratic_drag["v"])),
        1.0,
    )

    return 0.08 * x_range / max_speed


def animate_projectile_motion(
    no_drag: ProjectileResult,
    linear_drag: ProjectileResult,
    quadratic_drag: ProjectileResult,
    parameters: Parameters,
    show_vectors: bool,
    save_path: str | Path,
) -> None:
    output_path = _prepare_output_path(save_path)

    animation_end_time = max(
        float(no_drag["t"][-1]),
        float(linear_drag["t"][-1]),
        float(quadratic_drag["t"][-1]),
    )

    animation_time: FloatArray = np.linspace(
        0.0,
        animation_end_time,
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

    no_drag_vx, no_drag_vy = get_interpolated_velocities(no_drag, animation_time)
    linear_drag_vx, linear_drag_vy = get_interpolated_velocities(
        linear_drag,
        animation_time,
    )
    quadratic_drag_vx, quadratic_drag_vy = get_interpolated_velocities(
        quadratic_drag,
        animation_time,
    )

    x_min, x_max, y_min, y_max = get_axis_limits(
        no_drag,
        linear_drag,
        quadratic_drag,
    )

    velocity_scale = get_velocity_scale(
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

    velocity_text: Text | None = None
    wind_arrow: FancyArrowPatch | None = None
    velocity_arrows: dict[str, FancyArrowPatch] = {}

    axis.set_title("Projectile motion animation")
    axis.set_xlabel("x [m]")
    axis.set_ylabel("y [m]")
    axis.set_xlim(x_min, x_max)
    axis.set_ylim(y_min, y_max)
    axis.legend(loc="upper right")
    axis.grid(True, alpha=0.35)

    if show_vectors:
        if parameters.wind_speed > 0:
            start_x = 0.78
            start_y = 0.88
            length = 0.12

            end_x, end_y = _get_wind_arrow_end(
                parameters,
                start_x,
                start_y,
                length,
            )

            wind_arrow = FancyArrowPatch(
                (start_x, start_y),
                (end_x, end_y),
                transform=axis.transAxes,
                arrowstyle="->",
                mutation_scale=16,
                linewidth=2.5,
                color="black",
            )

            axis.add_patch(wind_arrow)

            axis.text(
                start_x,
                start_y - 0.07,
                _format_wind_label(parameters),
                transform=axis.transAxes,
                fontsize=9,
                bbox={
                    "facecolor": "white",
                    "alpha": 0.75,
                    "edgecolor": "none",
                },
            )

        arrow_data = {
            "no_drag": "red",
            "linear_drag": "blue",
            "quadratic_drag": "green",
        }

        for name, color in arrow_data.items():
            arrow = FancyArrowPatch(
                (0.0, 0.0),
                (0.0, 0.0),
                arrowstyle="->",
                mutation_scale=14,
                linewidth=2.0,
                color=color,
            )
            axis.add_patch(arrow)
            velocity_arrows[name] = arrow

        velocity_text = axis.text(
            0.02,
            0.78,
            "",
            transform=axis.transAxes,
            fontsize=9,
            bbox={
                "facecolor": "white",
                "alpha": 0.75,
                "edgecolor": "none",
            },
        )

    figure.tight_layout()

    def update(frame_index: int) -> tuple[Line2D, Line2D, Line2D, Text]:
        """Update projectile positions, velocity vectors, and labels for one frame."""

        current_time = float(animation_time[frame_index])

        current_no_drag_x = float(no_drag_x[frame_index])
        current_no_drag_y = float(no_drag_y[frame_index])

        current_linear_x = float(linear_drag_x[frame_index])
        current_linear_y = float(linear_drag_y[frame_index])

        current_quadratic_x = float(quadratic_drag_x[frame_index])
        current_quadratic_y = float(quadratic_drag_y[frame_index])

        current_no_drag_vx = float(no_drag_vx[frame_index])
        current_no_drag_vy = float(no_drag_vy[frame_index])

        current_linear_vx = float(linear_drag_vx[frame_index])
        current_linear_vy = float(linear_drag_vy[frame_index])

        current_quadratic_vx = float(quadratic_drag_vx[frame_index])
        current_quadratic_vy = float(quadratic_drag_vy[frame_index])

        no_drag_point.set_data(
            [current_no_drag_x],
            [current_no_drag_y],
        )

        linear_drag_point.set_data(
            [current_linear_x],
            [current_linear_y],
        )

        quadratic_drag_point.set_data(
            [current_quadratic_x],
            [current_quadratic_y],
        )

        time_text.set_text(f"t = {current_time:.2f} s")

        if show_vectors:
            no_drag_arrow = velocity_arrows["no_drag"]
            linear_drag_arrow = velocity_arrows["linear_drag"]
            quadratic_drag_arrow = velocity_arrows["quadratic_drag"]

            no_drag_arrow.set_positions(
                (current_no_drag_x, current_no_drag_y),
                (
                    current_no_drag_x + current_no_drag_vx * velocity_scale,
                    current_no_drag_y + current_no_drag_vy * velocity_scale,
                ),
            )

            linear_drag_arrow.set_positions(
                (current_linear_x, current_linear_y),
                (
                    current_linear_x + current_linear_vx * velocity_scale,
                    current_linear_y + current_linear_vy * velocity_scale,
                ),
            )

            quadratic_drag_arrow.set_positions(
                (current_quadratic_x, current_quadratic_y),
                (
                    current_quadratic_x + current_quadratic_vx * velocity_scale,
                    current_quadratic_y + current_quadratic_vy * velocity_scale,
                ),
            )

            assert velocity_text is not None

            velocity_text.set_text(
                "Velocity components\n"
                f"No drag: vx={current_no_drag_vx:.2f}, "
                f"vy={current_no_drag_vy:.2f} m/s\n"
                f"Linear:  vx={current_linear_vx:.2f}, "
                f"vy={current_linear_vy:.2f} m/s\n"
                f"Quad:    vx={current_quadratic_vx:.2f}, "
                f"vy={current_quadratic_vy:.2f} m/s\n"
                f"Wind:    vx={parameters.wind_vx:.2f}, "
                f"vy={parameters.wind_vy:.2f} m/s"
            )

        return (
            no_drag_point,
            linear_drag_point,
            quadratic_drag_point,
            time_text,
        )

    animation = FuncAnimation(
        figure,
        update,
        frames=GIF_FRAMES,
        interval=1000 // GIF_FPS,
        blit=False,
    )

    try:
        animation.save(
            output_path,
            writer=PillowWriter(fps=GIF_FPS),
            dpi=FIGURE_DPI,
        )
    finally:
        plt.close(figure)
