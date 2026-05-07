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
)
# from physics.no_drag import (
#     calculate_position_no_drag,
#     calculate_velocity_no_drag,
#     calculate_flight_time_no_drag,
#     calculate_max_height_no_drag,
#     calculate_range_no_drag,
#     calculate_time_to_max_height_no_drag
# )

from physics.linear_drag import (
    calculate_position_linear_drag,
    calculate_velocity_linear_drag,
)

# from visualization.plots import plot_motion_no_drag
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
    x, y = calculate_position_linear_drag(time, X0, Y0, VX0, VY0, G, linear_drag_const)
    vx, vy = calculate_velocity_linear_drag(time, VX0, VY0, G, linear_drag_const)

    # making a logical mask to cut off all recorts where y < 0
    first_negative_index = np.where(y < 0)[0][0]
    first_negative_index = int(first_negative_index)

    x_hit, t_hit = interpolate_ground_hit(
        time[first_negative_index - 1],
        x[first_negative_index - 1],
        y[first_negative_index - 1],
        time[first_negative_index],
        x[first_negative_index],
        y[first_negative_index],
    )
    mask = y >= 0
    time = time[mask]
    x = x[mask]
    y = y[mask]
    vx = vx[mask]
    vy = vy[mask]

    print(f"k = {linear_drag_const} 1/s")
    print(f"interpolated flight time = {t_hit} ")
    print(f"interpolated range = {x_hit} ")
    print(f"max_height = {max(y)} ")

    max_height_index = np.argmax(y)
    print(f"time for max height: {time[max_height_index]}")

    # plot_motion_no_drag(x, y, "Projectile motion without air resistance.")
