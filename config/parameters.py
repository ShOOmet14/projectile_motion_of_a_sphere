# File that contains all the constants required for this project
# Contant = Some value + units in comments
import numpy as np

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
LINEAR_DRAG_COEFFICIENT = 0.02  # kg / s
