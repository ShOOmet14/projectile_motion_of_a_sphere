import numpy as np

from config.parameters import (
    VX0,
    VY0,
    DT,
    X0,
    Y0,
    G,
    MASS,
    LINEAR_DRAG_COEFFICIENT,
    T_MAX,
)

from physics.no_drag import calculate_position_no_drag, calculate_velocity_no_drag

from physics.linear_drag import (
    calculate_position_linear_drag,
    calculate_velocity_linear_drag,
)

from simulation.solve import solve_projectile_motion

from visualization.plots import plot_motion
from physics.interpolation import interpolate_ground_hit

if __name__ == "__main__":
    time = np.arange(0.0, T_MAX, DT)

    linear_drag_const = LINEAR_DRAG_COEFFICIENT / MASS
    x_linear, y_linear = calculate_position_linear_drag(
        time, X0, Y0, VX0, VY0, G, linear_drag_const
    )
    vx_linear, vy_linear = calculate_velocity_linear_drag(
        time, VX0, VY0, G, linear_drag_const
    )

    x_no_drag, y_no_drag = calculate_position_no_drag(time, X0, Y0, VX0, VY0, G)
    vx_no_drag, vy_no_drag = calculate_velocity_no_drag(time, VX0, VY0, G)

    # making a logical mask to cut off all recorts where y < 0
    first_negative_index_no_drag = np.where(y_no_drag < 0)[0][0]
    first_negative_index_no_drag = int(first_negative_index_no_drag)

    first_negative_index_linear = np.where(y_linear < 0)[0][0]
    first_negative_index_linear = int(first_negative_index_linear)

    x_hit_linear, t_hit_linear = interpolate_ground_hit(
        time[first_negative_index_linear - 1],
        x_linear[first_negative_index_linear - 1],
        y_linear[first_negative_index_linear - 1],
        time[first_negative_index_linear],
        x_linear[first_negative_index_linear],
        y_linear[first_negative_index_linear],
    )

    x_hit_no_drag, t_hit_no_drag = interpolate_ground_hit(
        time[first_negative_index_no_drag - 1],
        x_no_drag[first_negative_index_no_drag - 1],
        y_no_drag[first_negative_index_no_drag - 1],
        time[first_negative_index_no_drag],
        x_no_drag[first_negative_index_no_drag],
        y_no_drag[first_negative_index_no_drag],
    )

    mask_linear = y_linear >= 0
    time_linear = time[mask_linear]
    x_linear = x_linear[mask_linear]
    y_linear = y_linear[mask_linear]
    vx_linear = vx_linear[mask_linear]
    vy_linear = vy_linear[mask_linear]

    mask_no_drag = y_no_drag >= 0
    time_no_drag = time[mask_no_drag]
    x_no_drag = x_no_drag[mask_no_drag]
    y_no_drag = y_no_drag[mask_no_drag]
    vx_no_drag = vx_no_drag[mask_no_drag]
    vy_no_drag = vy_no_drag[mask_no_drag]

    print(f"interpolated linear flight time = {t_hit_linear} ")
    print(f"interpolated linear range = {x_hit_linear} ")
    print(f"max_height linear = {max(y_linear)} ")

    print(f"interpolated no drag flight time = {t_hit_no_drag} ")
    print(f"interpolated no drag range = {x_hit_no_drag} ")
    print(f"max_height no drag = {max(y_no_drag)} ")

    x_quadratic, y_quadratic = solve_projectile_motion()

    plot_motion(x_no_drag, y_no_drag, x_linear, y_linear, x_quadratic, y_quadratic)
