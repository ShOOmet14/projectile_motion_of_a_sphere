from pathlib import Path

import pandas as pd

from simulation.solve import (
    ProjectileResult,
    solve_projectile_motion_no_drag,
    solve_projectile_motion_linear_drag,
    solve_projectile_motion_quadratic_drag,
)

from visualization.plots import plot_motion, plot_energy, plot_speed


def result_to_dataframe(result: ProjectileResult) -> pd.DataFrame:
    dataframe = pd.DataFrame(
        {
            "t": result["t"],
            "x": result["x"],
            "y": result["y"],
            "vx": result["vx"],
            "vy": result["vy"],
            "v": result["v"],
            "Ek": result["Ek"],
            "Ep": result["Ep"],
            "E": result["E"],
        }
    )

    return dataframe


def save_result_to_csv(path: str | Path, result: ProjectileResult) -> None:
    dataframe = result_to_dataframe(result)
    dataframe.to_csv(path, index=False)


if __name__ == "__main__":
    no_drag = solve_projectile_motion_no_drag()
    linear_drag = solve_projectile_motion_linear_drag()
    quadratic_drag = solve_projectile_motion_quadratic_drag()

    results_directory = Path("results")
    plots_directory = results_directory / "plots"

    results_directory.mkdir(exist_ok=True)
    plots_directory.mkdir(exist_ok=True)

    save_result_to_csv(results_directory / "no_drag.csv", no_drag)
    save_result_to_csv(results_directory / "linear_drag.csv", linear_drag)
    save_result_to_csv(results_directory / "quadratic_drag_rk4.csv", quadratic_drag)

    plot_motion(
        no_drag["x"],
        no_drag["y"],
        linear_drag["x"],
        linear_drag["y"],
        quadratic_drag["x"],
        quadratic_drag["y"],
        plots_directory / "trajectory_comparison.png",
    )

    plot_energy(
        no_drag["E"],
        linear_drag["E"],
        quadratic_drag["E"],
        no_drag["t"],
        linear_drag["t"],
        quadratic_drag["t"],
        plots_directory / "energy_comparison.png",
    )

    plot_speed(
        no_drag["v"],
        linear_drag["v"],
        quadratic_drag["v"],
        no_drag["t"],
        linear_drag["t"],
        quadratic_drag["t"],
        plots_directory / "speed_comparison.png",
    )
