from dataclasses import dataclass
from math import cos, pi, sin
import numpy as np


@dataclass(frozen=True)
class Parameters:
    v0: float
    angle_deg: float
    mass: float
    radius: float
    cd: float
    rho: float
    linear_drag: float
    dt: float
    g: float

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


G = 9.80665  # m / s^2

V0 = 50.0  # m / s
ANGLE_DEG = 45.0  # degrees
X0 = 0.0  # m
Y0 = 0.0  # m

T_MAX = 10.0  # maximum simulation time, s
DT = 0.01  # time step, s

ANGLE_RAD = np.radians(ANGLE_DEG)
VX0 = V0 * np.cos(ANGLE_RAD)
VY0 = V0 * np.sin(ANGLE_RAD)

MASS = 0.145  # kg

# LINEAR DRAG
LINEAR_DRAG_COEFFICIENT = 0.02  # kg / s
LINEAR_DRAG_CONST = LINEAR_DRAG_COEFFICIENT / MASS

# QUADRATIC DRAG
RADIUS = 0.037  # m
QUADRATIC_DRAG_COEFFICIENT = 0.47
AIR_DENSITY = 1.225  # kg / m^3

SURFACE_AREA = np.pi * RADIUS * RADIUS  # m^2
QUADRATIC_DRAG_CONSTANT = (
    AIR_DENSITY * QUADRATIC_DRAG_COEFFICIENT * SURFACE_AREA / (2 * MASS)
)
