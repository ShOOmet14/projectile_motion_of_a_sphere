from pathlib import Path

from config.parameters import DEFAULT_PARAMETERS

from simulation.solve import (
    solve_projectile_motion_no_drag,
    solve_projectile_motion_linear_drag,
    solve_projectile_motion_quadratic_drag,
)

from storage.csv_export import export_simulation_results_to_csv
# from visualization.plots import plot_motion, plot_energy, plot_speed
# from visualization.animation import animate_projectile_motion


if __name__ == "__main__":
    parameters = DEFAULT_PARAMETERS

    no_drag = solve_projectile_motion_no_drag(parameters)
    linear_drag = solve_projectile_motion_linear_drag(parameters)
    quadratic_drag = solve_projectile_motion_quadratic_drag(parameters)

    results_directory = Path("results")
    plots_directory = results_directory / "plots"
    animations_directory = results_directory / "animations"

    results_directory.mkdir(exist_ok=True)
    plots_directory.mkdir(exist_ok=True)
    animations_directory.mkdir(exist_ok=True)

    export_simulation_results_to_csv(
        no_drag,
        linear_drag,
        quadratic_drag,
        results_directory,
    )

    # plot_motion(
    #     no_drag["x"],
    #     no_drag["y"],
    #     linear_drag["x"],
    #     linear_drag["y"],
    #     quadratic_drag["x"],
    #     quadratic_drag["y"],
    #     plots_directory / "trajectory_comparison.png",
    # )

    # plot_energy(
    #     no_drag["E"],
    #     linear_drag["E"],
    #     quadratic_drag["E"],
    #     no_drag["t"],
    #     linear_drag["t"],
    #     quadratic_drag["t"],
    #     plots_directory / "energy_comparison.png",
    # )

    # plot_speed(
    #     no_drag["v"],
    #     linear_drag["v"],
    #     quadratic_drag["v"],
    #     no_drag["t"],
    #     linear_drag["t"],
    #     quadratic_drag["t"],
    #     plots_directory / "speed_comparison.png",
    # )

    # animate_projectile_motion(
    #     no_drag,
    #     linear_drag,
    #     quadratic_drag,
    #     animations_directory / "projectile_motion.gif",
    # )
