import json

from dataclasses import asdict
from pathlib import Path
from typing import Any

from config.parameters import DEFAULT_PARAMETERS, Parameters


USER_SETTINGS_PATH = Path(__file__).with_name("user_settings.json")

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


def parameters_to_settings_dict(parameters: Parameters) -> dict[str, float]:
    parameters_as_dict = asdict(parameters)

    return {key: float(parameters_as_dict[key]) for key in SETTINGS_KEYS}


def load_user_settings() -> Parameters:
    if not USER_SETTINGS_PATH.exists():
        return DEFAULT_PARAMETERS

    try:
        with open(USER_SETTINGS_PATH, "r", encoding="utf-8") as file:
            loaded_data: Any = json.load(file)

        if not isinstance(loaded_data, dict):
            return DEFAULT_PARAMETERS

        default_data = asdict(DEFAULT_PARAMETERS)

        for key in SETTINGS_KEYS:
            if key in loaded_data:
                default_data[key] = float(loaded_data[key])

        return Parameters(**default_data)

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
