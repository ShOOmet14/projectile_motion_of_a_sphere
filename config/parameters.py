from dataclasses import dataclass
from math import cos, pi, sin


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
