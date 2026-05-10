import numpy as np

from config.parameters import (
    V0,
    ANGLE_DEG,
    VX0,
    VY0,
    DT,
    X0,
    Y0,
    G,
    MASS,
    LINEAR_DRAG_COEFFICIENT,
    T_MAX,
    SURFACE_AREA,
    QUADRATIC_DRAG_CONSTANT,
)

from physics.no_drag import calculate_position_no_drag, calculate_velocity_no_drag

from physics.linear_drag import (
    calculate_position_linear_drag,
    calculate_velocity_linear_drag,
)

from physics.quadratic_drag import calculate_state_quadratic_drag
from simulation.integrators import euler_step, runge_kutta_method
from simulation.solve import solve_projectile_motion

# from visualization.plots import plot_motion
from physics.interpolation import interpolate_ground_hit

if __name__ == "__main__":
    print("Projectile motion simulation")
    print(f"Initial speed: {V0} m/s")
    print(f"Launch angle: {ANGLE_DEG} degrees")
    print(f"Initial X axis speed: {VX0} m/s")
    print(f"Initial Y axis speed: {VY0} m/s")

    # flight_time = calculate_flight_time_no_drag(VY0, G)
    # flight_range = calculate_range_no_drag(VX0, flight_time)
    # max_flight_height = calculate_max_height_no_drag(Y0, VY0, G)
    # up_only_time = calculate_time_to_max_height_no_drag(VY0, G)

    # time = np.arange(0.0, flight_time + DT, DT)

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

    print(f"k = {linear_drag_const} 1/s")
    print(f"interpolated linear flight time = {t_hit_linear} ")
    print(f"interpolated linear range = {x_hit_linear} ")
    print(f"max_height linear = {max(y_linear)} ")
    print(f"interpolated no drag flight time = {t_hit_no_drag} ")
    print(f"interpolated no drag range = {x_hit_no_drag} ")
    print(f"max_height no drag = {max(y_no_drag)} ")

    max_height_index_linear = np.argmax(y_linear)
    print(f"time for max height linear: {time[max_height_index_linear]}")

    max_height_index_no_drag = np.argmax(y_no_drag)
    print(f"time for max height no drag: {time[max_height_index_no_drag]}")

    print(f"Surface are is: {SURFACE_AREA}")
    print(f"quadratoc drag constant q = {QUADRATIC_DRAG_CONSTANT}")

    state_beginning = (X0, Y0, VX0, VY0)
    print(f"Initial state:\n{state_beginning}")

    deriatives_state = calculate_state_quadratic_drag(state_beginning)
    print(f"Initial derivatives:\n{deriatives_state}")

    state_new = euler_step(state_beginning)
    print(f"State after one Euler step:\n{state_new}")

    solve_projectile_motion()

    initial_state = np.array([X0, Y0, VX0, VY0], dtype=np.float64)
    new_state = runge_kutta_method(initial_state)

    print("One step of Runge-Kutta method:")
    print(f"initial state:\n{initial_state}")
    print(f"state after one Euler step:\n{state_new}")
    print(f"state after one runge-kutta step:\n{new_state}")

    # plot_motion(x_no_drag, y_no_drag, x_linear, y_linear)
