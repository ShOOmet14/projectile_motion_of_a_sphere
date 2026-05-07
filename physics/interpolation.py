def interpolate_ground_hit(
    time_1: float, x1: float, y1: float, time_2: float, x2: float, y2: float
) -> tuple[float, float]:
    x_hit = x1 + (-y1 / (y2 - y1)) * (x2 - x1)
    t_hit = time_1 + (-y1 / (y2 - y1)) * (time_2 - time_1)

    return (x_hit, t_hit)
