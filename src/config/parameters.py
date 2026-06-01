"""Define and validate the parameters used by projectile-motion models."""

from dataclasses import dataclass
from math import cos, isfinite, pi, radians, sin

MAX_SIMULATION_STEPS: int = 1_000_000

_FINITE_PARAMETER_NAMES: tuple[str, ...] = (
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
)


@dataclass(frozen=True)
class Parameters:
    """Store validated inputs for projectile-motion calculations.

    Angles are provided in degrees by the GUI and converted to radians when
    needed by trigonometric calculations. Distances are measured in metres,
    time in seconds, mass in kilograms, and velocities in metres per second.

    The instance is immutable so that one simulation run always uses a
    consistent set of physical and numerical parameters.
    """

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
        """Return the launch angle in radians."""

        return radians(self.initial_angle_degrees)

    @property
    def wind_angle_radians(self) -> float:
        """Return the wind direction in radians."""

        return radians(self.wind_angle_degrees)

    @property
    def vx0(self) -> float:
        """Return the initial horizontal velocity component in metres per second."""

        return self.initial_velocity * cos(self.initial_angle_radians)

    @property
    def vy0(self) -> float:
        """Return the initial vertical velocity component in metres per second."""

        return self.initial_velocity * sin(self.initial_angle_radians)

    @property
    def wind_vx(self) -> float:
        """Return the horizontal wind velocity component in metres per second."""

        return self.wind_speed * cos(self.wind_angle_radians)

    @property
    def wind_vy(self) -> float:
        """Return the vertical wind velocity component in metres per second."""

        return self.wind_speed * sin(self.wind_angle_radians)

    @property
    def area(self) -> float:
        """Return the projectile cross-sectional area in square metres."""

        return pi * self.radius**2

    @property
    def linear_drag_factor(self) -> float:
        """Return the linear-drag coefficient divided by projectile mass."""

        return self.linear_drag / self.mass

    @property
    def quadratic_drag_factor(self) -> float:
        """Return the constant factor used by the quadratic-drag equations."""

        return self.air_density * self.drag_coefficient * self.area / (2.0 * self.mass)

    def __post_init__(self) -> None:
        """Validate values immediately after dataclass initialization."""

        self._validate_finite_values()
        self._validate_ranges()
        self._validate_step_count()

    def _validate_finite_values(self) -> None:
        """Reject NaN and infinite values before checking numerical ranges."""

        for name in _FINITE_PARAMETER_NAMES:
            value = getattr(self, name)

            if not isfinite(value):
                raise ValueError(f"{name} must be a finite number.")

    def _validate_ranges(self) -> None:
        """Reject parameter values outside the supported physical ranges."""

        if self.initial_velocity < 0:
            raise ValueError("initial_velocity must be greater than or equal to zero.")

        if not 0 <= self.initial_angle_degrees <= 90:
            raise ValueError("initial_angle_degrees must be between 0 and 90 degrees.")

        if self.mass <= 0:
            raise ValueError("mass must be greater than zero.")

        if self.radius <= 0:
            raise ValueError("radius must be greater than zero.")

        if self.drag_coefficient < 0:
            raise ValueError("drag_coefficient must be greater than or equal to zero.")

        if self.air_density < 0:
            raise ValueError("air_density must be greater than or equal to zero.")

        if self.linear_drag <= 0:
            raise ValueError("linear_drag must be greater than zero.")

        if self.time_step <= 0:
            raise ValueError("time_step must be greater than zero.")

        if self.time_max <= 0:
            raise ValueError("time_max must be greater than zero.")

        if self.g <= 0:
            raise ValueError("g must be greater than zero.")

        if self.wind_speed < 0:
            raise ValueError("wind_speed must be greater than or equal to zero.")

        if not 0 <= self.wind_angle_degrees <= 360:
            raise ValueError("wind_angle_degrees must be between 0 and 360 degrees.")

    def _validate_step_count(self) -> None:
        """Prevent simulations that would generate an excessive number of samples."""

        if self.time_max / self.time_step > MAX_SIMULATION_STEPS:
            raise ValueError(
                "Too many simulation steps. Increase time_step or decrease time_max."
            )


DEFAULT_PARAMETERS = Parameters()
