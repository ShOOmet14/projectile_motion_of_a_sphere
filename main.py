from simulation.solve import (
    solve_projectile_motion_no_drag,
    solve_projectile_motion_linear_drag,
    solve_projectile_motion_quadratic_drag,
)

from visualization.plots import plot_speed

if __name__ == "__main__":
    x_no_drag, y_no_drag, time_no_drag, mechanical_energy_no_drag, speed_no_drag = (
        solve_projectile_motion_no_drag()
    )
    (
        x_linear,
        y_linear,
        time_linear_drag,
        mechanical_energy_linear_drag,
        speed_linear_drag,
    ) = solve_projectile_motion_linear_drag()
    (
        x_quadratic,
        y_quadratic,
        time_quadratic_drag,
        mechanical_energy_quadratic_drag,
        speed_quadratic_drag,
    ) = solve_projectile_motion_quadratic_drag()

    # plot_motion(x_no_drag, y_no_drag, x_linear, y_linear, x_quadratic, y_quadratic)

    plot_speed(
        speed_no_drag,
        time_no_drag,
        speed_linear_drag,
        time_linear_drag,
        speed_quadratic_drag,
        time_quadratic_drag,
    )

    # plot_energy(
    #     mechanical_energy_no_drag,
    #     time_no_drag,
    #     mechanical_energy_linear_drag,
    #     time_linear_drag,
    #     mechanical_energy_quadratic_drag,
    #     time_quadratic_drag,
    # )
