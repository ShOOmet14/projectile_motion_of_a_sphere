from src.config.parameters import Parameters


def test_default_parameters_initialization():
    parameters = Parameters()

    assert parameters.initial_velocity == 50.0
    assert parameters.initial_angle_degrees == 45.0
    assert parameters.mass == 0.145
    assert parameters.radius == 0.0366
    assert parameters.drag_coefficient == 0.47
    assert parameters.air_density == 1.225
    assert parameters.linear_drag == 0.02
    assert parameters.time_step == 0.01
    assert parameters.time_max == 10.0
    assert parameters.g == 9.80665
    assert parameters.wind_speed == 0.0
    assert parameters.wind_angle_degrees == 0.0
    assert parameters.initial_x == 0.0
    assert parameters.initial_y == 0.0
