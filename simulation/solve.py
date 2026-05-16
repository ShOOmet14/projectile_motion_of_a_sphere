import numpy as np
import numpy.typing as npt

from config.parameters import DEFAULT_PARAMETERS, Parameters

# Type constants:
ProjectileResult = dict[str, npt.NDArray[np.float64]]


def calculate_position_linear_drag(
    time: npt.NDArray[np.float64],
    x0: float,
    y0: float,
    vx0: float,
    vy0: float,
    k: float,
    g: float,
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    position_x = x0 + vx0 * (1.0 - np.exp(-k * time)) / k

    position_y = y0 + (vy0 + g / k) * (1.0 - np.exp(-k * time)) / k - g * time / k

    return position_x, position_y


def calculate_position_no_drag(
    time: npt.NDArray[np.float64],
    x0: float,
    y0: float,
    vx0: float,
    vy0: float,
    g: float,
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    position_x = x0 + vx0 * time
    position_y = y0 + vy0 * time - 0.5 * g * time * time

    return position_x, position_y


def calculate_velocity_no_drag(
    time: npt.NDArray[np.float64],
    vx0: float,
    vy0: float,
    g: float,
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    velocity_x = np.full_like(time, vx0)
    velocity_y = vy0 - g * time

    return velocity_x, velocity_y


def calculate_velocity_linear_drag(
    time: npt.NDArray[np.float64],
    vx0: float,
    vy0: float,
    k: float,
    g: float,
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    velocity_x = vx0 * np.exp(-k * time)
    velocity_y = (vy0 + g / k) * np.exp(-k * time) - g / k

    return velocity_x, velocity_y


def calculate_state_quadratic_drag(
    state: npt.NDArray[np.float64],
    q: float,
    g: float,
) -> npt.NDArray[np.float64]:
    _, _, vx, vy = state

    v = np.hypot(vx, vy)

    ax = -q * v * vx
    ay = -g - q * v * vy

    return np.array([vx, vy, ax, ay], dtype=np.float64)


def runge_kutta_method(
    state_old: npt.NDArray[np.float64],
    dt: float,
    q: float,
    g: float,
) -> npt.NDArray[np.float64]:
    k1 = calculate_state_quadratic_drag(state_old, q, g)
    k2 = calculate_state_quadratic_drag(state_old + dt * k1 / 2.0, q, g)
    k3 = calculate_state_quadratic_drag(state_old + dt * k2 / 2.0, q, g)
    k4 = calculate_state_quadratic_drag(state_old + dt * k3, q, g)

    state_new = state_old + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0

    return state_new


def interpolate_value_at_ground(
    value_1: float,
    value_2: float,
    y1: float,
    y2: float,
) -> float:
    value_hit = value_1 + (-y1 / (y2 - y1)) * (value_2 - value_1)

    return value_hit


def calculate_speed(
    vx: npt.NDArray[np.float64],
    vy: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    speed = np.hypot(vx, vy)  # note to myself: this is the same as sqrt(vx*vx + vy*vy)

    return speed


def calculate_kinetic_energy(
    speed: npt.NDArray[np.float64],
    mass: float,
) -> npt.NDArray[np.float64]:
    return 0.5 * mass * speed * speed


def calculate_potential_energy(
    y: npt.NDArray[np.float64],
    mass: float,
    g: float,
) -> npt.NDArray[np.float64]:
    return mass * g * y


def calculate_mechanical_energy(
    kinetic_energy: npt.NDArray[np.float64],
    potential_energy: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    mechanical_energy = kinetic_energy + potential_energy

    return mechanical_energy


def solve_projectile_motion_no_drag(
    parameters: Parameters = DEFAULT_PARAMETERS,
) -> ProjectileResult:

    time = np.arange(0.0, parameters.t_max, parameters.dt, dtype=np.float64)

    x, y = calculate_position_no_drag(
        time,
        parameters.x0,
        parameters.y0,
        parameters.vx0,
        parameters.vy0,
        parameters.g,
    )

    vx, vy = calculate_velocity_no_drag(
        time,
        parameters.vx0,
        parameters.vy0,
        parameters.g,
    )

    negative_indices = np.where(y < 0)[0]
    if len(negative_indices) == 0:
        raise ValueError(
            "No-drag projectile did not hit the ground. Increase parameters.t_max."
        )

    first_negative_index = int(negative_indices[0])

    x_hit = interpolate_value_at_ground(
        x[first_negative_index - 1],
        x[first_negative_index],
        y[first_negative_index - 1],
        y[first_negative_index],
    )

    t_hit = interpolate_value_at_ground(
        time[first_negative_index - 1],
        time[first_negative_index],
        y[first_negative_index - 1],
        y[first_negative_index],
    )

    vx_hit = interpolate_value_at_ground(
        vx[first_negative_index - 1],
        vx[first_negative_index],
        y[first_negative_index - 1],
        y[first_negative_index],
    )

    vy_hit = interpolate_value_at_ground(
        vy[first_negative_index - 1],
        vy[first_negative_index],
        y[first_negative_index - 1],
        y[first_negative_index],
    )

    mask = y >= 0

    time_no_drag = np.append(time[mask], t_hit)
    x = np.append(x[mask], x_hit)
    y = np.append(y[mask], 0.0)
    vx = np.append(vx[mask], vx_hit)
    vy = np.append(vy[mask], vy_hit)

    speed = calculate_speed(vx, vy)

    kinetic_energy = calculate_kinetic_energy(speed, parameters.mass)
    potential_energy = calculate_potential_energy(y, parameters.mass, parameters.g)

    mechanical_energy = calculate_mechanical_energy(kinetic_energy, potential_energy)

    return {
        "t": time_no_drag,
        "x": x,
        "y": y,
        "vx": vx,
        "vy": vy,
        "v": speed,
        "Ek": kinetic_energy,
        "Ep": potential_energy,
        "E": mechanical_energy,
    }


def solve_projectile_motion_linear_drag(
    parameters: Parameters = DEFAULT_PARAMETERS,
) -> ProjectileResult:

    time = np.arange(0.0, parameters.t_max, parameters.dt, dtype=np.float64)

    x, y = calculate_position_linear_drag(
        time,
        parameters.x0,
        parameters.y0,
        parameters.vx0,
        parameters.vy0,
        parameters.k,
        parameters.g,
    )

    vx, vy = calculate_velocity_linear_drag(
        time,
        parameters.vx0,
        parameters.vy0,
        parameters.k,
        parameters.g,
    )

    negative_indices = np.where(y < 0)[0]
    if len(negative_indices) == 0:
        raise ValueError(
            "Linear-drag projectile did not hit the ground. Increase parameters.t_max."
        )

    first_negative_index = int(negative_indices[0])

    x_hit = interpolate_value_at_ground(
        x[first_negative_index - 1],
        x[first_negative_index],
        y[first_negative_index - 1],
        y[first_negative_index],
    )

    t_hit = interpolate_value_at_ground(
        time[first_negative_index - 1],
        time[first_negative_index],
        y[first_negative_index - 1],
        y[first_negative_index],
    )

    vx_hit = interpolate_value_at_ground(
        vx[first_negative_index - 1],
        vx[first_negative_index],
        y[first_negative_index - 1],
        y[first_negative_index],
    )

    vy_hit = interpolate_value_at_ground(
        vy[first_negative_index - 1],
        vy[first_negative_index],
        y[first_negative_index - 1],
        y[first_negative_index],
    )

    mask = y >= 0

    time_linear = np.append(time[mask], t_hit)
    x = np.append(x[mask], x_hit)
    y = np.append(y[mask], 0.0)
    vx = np.append(vx[mask], vx_hit)
    vy = np.append(vy[mask], vy_hit)

    speed = calculate_speed(vx, vy)

    kinetic_energy = calculate_kinetic_energy(speed, parameters.mass)
    potential_energy = calculate_potential_energy(y, parameters.mass, parameters.g)

    mechanical_energy = calculate_mechanical_energy(kinetic_energy, potential_energy)

    return {
        "t": time_linear,
        "x": x,
        "y": y,
        "vx": vx,
        "vy": vy,
        "v": speed,
        "Ek": kinetic_energy,
        "Ep": potential_energy,
        "E": mechanical_energy,
    }


def solve_projectile_motion_quadratic_drag(
    parameters: Parameters = DEFAULT_PARAMETERS,
) -> ProjectileResult:

    time_quadratic: list[float] = [0.0]
    x: list[float] = [parameters.x0]
    y: list[float] = [parameters.y0]
    vx: list[float] = [parameters.vx0]
    vy: list[float] = [parameters.vy0]

    while True:
        current_state = np.array([x[-1], y[-1], vx[-1], vy[-1]], dtype=np.float64)
        x_new, y_new, vx_new, vy_new = runge_kutta_method(
            current_state,
            parameters.dt,
            parameters.q,
            parameters.g,
        )

        time_quadratic.append(time_quadratic[-1] + parameters.dt)
        x.append(x_new)
        y.append(y_new)
        vx.append(vx_new)
        vy.append(vy_new)

        if y_new < 0:
            break

        if time_quadratic[-1] >= parameters.t_max:
            raise ValueError(
                "Quadratic-drag projectile did not hit the ground. Increase parameters.t_max."
            )

    x_hit = interpolate_value_at_ground(
        x[-2],
        x[-1],
        y[-2],
        y[-1],
    )

    t_hit = interpolate_value_at_ground(
        time_quadratic[-2],
        time_quadratic[-1],
        y[-2],
        y[-1],
    )

    vx_hit = interpolate_value_at_ground(
        vx[-2],
        vx[-1],
        y[-2],
        y[-1],
    )

    vy_hit = interpolate_value_at_ground(
        vy[-2],
        vy[-1],
        y[-2],
        y[-1],
    )

    x[-1] = x_hit
    y[-1] = 0.0
    vx[-1] = vx_hit
    vy[-1] = vy_hit
    time_quadratic[-1] = t_hit

    x_as_array = np.array(x, dtype=np.float64)
    y_as_array = np.array(y, dtype=np.float64)
    vx_as_array = np.array(vx, dtype=np.float64)
    vy_as_array = np.array(vy, dtype=np.float64)
    time_as_array = np.array(time_quadratic, dtype=np.float64)

    speed = calculate_speed(vx_as_array, vy_as_array)

    kinetic_energy = calculate_kinetic_energy(speed, parameters.mass)
    potential_energy = calculate_potential_energy(
        y_as_array, parameters.mass, parameters.g
    )

    mechanical_energy = calculate_mechanical_energy(kinetic_energy, potential_energy)

    return {
        "t": time_as_array,
        "x": x_as_array,
        "y": y_as_array,
        "vx": vx_as_array,
        "vy": vy_as_array,
        "v": speed,
        "Ek": kinetic_energy,
        "Ep": potential_energy,
        "E": mechanical_energy,
    }
