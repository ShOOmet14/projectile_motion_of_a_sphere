import json

from pathlib import Path
from typing import TypeGuard, cast

from config.parameters import DEFAULT_PARAMETERS, Parameters


USER_SETTINGS_PATH = Path(__file__).with_name("user_settings.json")

NumberLike = int | float | str

SETTINGS_KEYS = (
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
)


def is_number_like(value: object) -> TypeGuard[NumberLike]:
    return not isinstance(value, bool) and isinstance(value, int | float | str)


def parameters_to_settings_dict(parameters: Parameters) -> dict[str, float]:
    return {
        "v0": float(parameters.v0),
        "angle_deg": float(parameters.angle_deg),
        "mass": float(parameters.mass),
        "radius": float(parameters.radius),
        "cd": float(parameters.cd),
        "rho": float(parameters.rho),
        "linear_drag": float(parameters.linear_drag),
        "dt": float(parameters.dt),
        "t_max": float(parameters.t_max),
        "g": float(parameters.g),
    }


def settings_dict_to_parameters(settings: dict[str, float]) -> Parameters:
    return Parameters(
        v0=settings["v0"],
        angle_deg=settings["angle_deg"],
        mass=settings["mass"],
        radius=settings["radius"],
        cd=settings["cd"],
        rho=settings["rho"],
        linear_drag=settings["linear_drag"],
        dt=settings["dt"],
        t_max=settings["t_max"],
        g=settings["g"],
    )


def load_user_settings() -> Parameters:
    if not USER_SETTINGS_PATH.exists():
        return DEFAULT_PARAMETERS

    try:
        with open(USER_SETTINGS_PATH, "r", encoding="utf-8") as file:
            loaded_json: object = json.load(file)

        if not isinstance(loaded_json, dict):
            return DEFAULT_PARAMETERS

        loaded_data = cast(dict[str, object], loaded_json)

        settings = parameters_to_settings_dict(DEFAULT_PARAMETERS)

        for key in SETTINGS_KEYS:
            loaded_value = loaded_data.get(key)

            if is_number_like(loaded_value):
                settings[key] = float(loaded_value)

        return settings_dict_to_parameters(settings)

    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return DEFAULT_PARAMETERS


def save_user_settings(parameters: Parameters) -> None:
    USER_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    settings_data = parameters_to_settings_dict(parameters)

    with open(USER_SETTINGS_PATH, "w", encoding="utf-8") as file:
        json.dump(
            settings_data,
            file,
            indent=4,
            ensure_ascii=False,
        )
