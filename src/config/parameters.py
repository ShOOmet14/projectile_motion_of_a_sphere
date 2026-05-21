from dataclasses import dataclass
from math import cos, pi, sin, isfinite

MAX_SIMULATION_STEPS: int = 1_000_000


@dataclass(frozen=True)
class Parameters:
    initial_velocity: float = 50.0
    initial_angle_degrees: float = 45.0

    mass: float = 0.145
    radius: float = 0.0366

    drag_coefficient: float = 0.47
    air_density: float = 1.225
    linear_drag: float = 0.02

    time_step: float = 0.01
    time_max: float = 10.0
    g: float = 9.80665

    wind_speed: float = 0.0
    wind_angle_degrees: float = 0.0

    initial_x: float = 0.0
    initial_y: float = 0.0

    @property
    def initial_angle_radians(self) -> float:
        return self.initial_angle_degrees * pi / 180.0

    @property
    def wind_angle_radians(self) -> float:
        return self.wind_angle_degrees * pi / 180.0

    @property
    def vx0(self) -> float:
        return self.initial_velocity * cos(self.initial_angle_radians)

    @property
    def vy0(self) -> float:
        return self.initial_velocity * sin(self.initial_angle_radians)

    @property
    def wind_vx(self) -> float:
        return self.wind_speed * cos(self.wind_angle_radians)

    @property
    def wind_vy(self) -> float:
        return self.wind_speed * sin(self.wind_angle_radians)

    @property
    def area(self) -> float:
        return pi * self.radius * self.radius

    @property
    def linear_drag_factor(self) -> float:
        return self.linear_drag / self.mass

    @property
    def quadratic_drag_factor(self) -> float:
        return self.air_density * self.drag_coefficient * self.area / (2.0 * self.mass)

    def __post_init__(self) -> None:
        for name in (
            "initial_velocity",
            "initial_angle_degrees",
            "mass",
            "radius",
            "drag_coefficient",
            "air_density",
            "linear_drag",
            "time_step",
            "time_max",
            "g",
            "wind_speed",
            "wind_angle_degrees",
            "initial_x",
            "initial_y",
        ):
            value = getattr(self, name)

            if not isfinite(value):
                raise ValueError(f"{name} must be a finite number.")

        if self.initial_velocity < 0:
            raise ValueError(
                "Initial speed initial_velocity must be greater than or equal to zero."
            )

        if not 0 <= self.initial_angle_degrees <= 90:
            raise ValueError("Angle must be between 0 and 90 degrees.")

        if self.mass <= 0:
            raise ValueError("Mass must be greater than zero.")

        if self.radius <= 0:
            raise ValueError("Radius must be greater than zero.")

        if self.drag_coefficient < 0:
            raise ValueError("drag_coefficient must be greater than or equal to zero.")

        if self.air_density < 0:
            raise ValueError("air_density must be greater than or equal to zero.")

        if self.linear_drag <= 0:
            raise ValueError("Linear drag coefficient must be greater than zero.")

        if self.time_step <= 0:
            raise ValueError("time_step must be greater than zero.")

        if self.time_max <= 0:
            raise ValueError("Max simulation time time_max must be greater than zero.")

        if self.g <= 0:
            raise ValueError("Gravity g must be greater than zero.")

        if self.wind_speed < 0:
            raise ValueError("Wind speed must be greater than or equal to zero.")

        if not 0 <= self.wind_angle_degrees <= 360:
            raise ValueError("Wind angle must be between 0 and 360 degrees.")

        if self.time_max / self.time_step > MAX_SIMULATION_STEPS:
            raise ValueError(
                "Too many simulation steps. Increase time_step or decrease time_max."
            )


DEFAULT_PARAMETERS = Parameters()
