from dataclasses import dataclass
from math import cos, pi, sin, isfinite

MAX_SIMULATION_STEPS = 1_000_000


@dataclass(frozen=True)
class Parameters:
    v0: float = 50.0
    angle_deg: float = 45.0

    mass: float = 0.145
    radius: float = 0.0366

    cd: float = 0.47
    rho: float = 1.225
    linear_drag: float = 0.02

    dt: float = 0.01
    t_max: float = 10.0
    g: float = 9.80665

    x0: float = 0.0
    y0: float = 0.0

    def __post_init__(self) -> None:
        for name in (
            "v0",
            "angle_deg",
            "mass",
            "radius",
            "cd",
            "rho",
            "linear_drag",
            "dt",
            "t_max",
            "g",
            "x0",
            "y0",
        ):
            value = getattr(self, name)

            if not isfinite(value):
                raise ValueError(f"{name} must be a finite number.")

        if self.v0 < 0:
            raise ValueError("Initial speed v0 must be greater than or equal to zero.")

        if not 0 <= self.angle_deg <= 90:
            raise ValueError("Angle must be between 0 and 90 degrees.")

        if self.mass <= 0:
            raise ValueError("Mass must be greater than zero.")

        if self.radius <= 0:
            raise ValueError("Radius must be greater than zero.")

        if self.cd < 0:
            raise ValueError(
                "Drag coefficient Cd must be greater than or equal to zero."
            )

        if self.rho < 0:
            raise ValueError("Air density rho must be greater than or equal to zero.")

        if self.linear_drag <= 0:
            raise ValueError("Linear drag coefficient must be greater than zero.")

        if self.dt <= 0:
            raise ValueError("Time step dt must be greater than zero.")

        if self.t_max <= 0:
            raise ValueError("Max simulation time t_max must be greater than zero.")

        if self.g <= 0:
            raise ValueError("Gravity g must be greater than zero.")

        if self.t_max / self.dt > MAX_SIMULATION_STEPS:
            raise ValueError(
                "Too many simulation steps. Increase dt or decrease t_max."
            )

    @property
    def angle_rad(self) -> float:
        return self.angle_deg * pi / 180.0

    @property
    def vx0(self) -> float:
        return self.v0 * cos(self.angle_rad)

    @property
    def vy0(self) -> float:
        return self.v0 * sin(self.angle_rad)

    @property
    def area(self) -> float:
        return pi * self.radius * self.radius

    @property
    def k(self) -> float:
        return self.linear_drag / self.mass

    @property
    def q(self) -> float:
        return self.rho * self.cd * self.area / (2.0 * self.mass)


DEFAULT_PARAMETERS = Parameters()
