from simulation.solve import (
    solve_projectile_motion_no_drag,
    solve_projectile_motion_linear_drag,
    solve_projectile_motion_quadratic_drag,
)

from visualization.plots import plot_motion

if __name__ == "__main__":
    x_no_drag, y_no_drag = solve_projectile_motion_no_drag()
    x_linear, y_linear = solve_projectile_motion_linear_drag()
    x_quadratic, y_quadratic = solve_projectile_motion_quadratic_drag()

    plot_motion(x_no_drag, y_no_drag, x_linear, y_linear, x_quadratic, y_quadratic)
