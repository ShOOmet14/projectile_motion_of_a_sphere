import json

from pathlib import Path
from typing import Literal, TypeGuard

from src.config.parameters import DEFAULT_PARAMETERS, Parameters


ThemeName = Literal["light", "dark"]

CONFIG_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CONFIG_DIR.parent

APP_SETTINGS_PATH = CONFIG_DIR / "app_settings.json"
USER_SETTINGS_PATH = CONFIG_DIR / "user_settings.json"

STYLE_DIR = PROJECT_DIR / "style"
BASE_STYLE_PATH = STYLE_DIR / "style.css"
LIGHT_STYLE_PATH = STYLE_DIR / "light.css"
DARK_STYLE_PATH = STYLE_DIR / "dark.css"

DEFAULT_THEME: ThemeName = "light"

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
    "wind_speed",
    "wind_angle_deg",
)


def is_settings_data(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict)


def is_theme_name(value: object) -> TypeGuard[ThemeName]:
    return value in ("light", "dark")


def is_number_like(value: object) -> TypeGuard[NumberLike]:
    return not isinstance(value, bool) and isinstance(value, int | float | str)


def load_theme() -> ThemeName:
    if not APP_SETTINGS_PATH.exists():
        return DEFAULT_THEME

    try:
        with open(APP_SETTINGS_PATH, "r", encoding="utf-8") as file:
            data: object = json.load(file)

    except (OSError, json.JSONDecodeError):
        return DEFAULT_THEME

    if not is_settings_data(data):
        return DEFAULT_THEME

    theme = data.get("theme")

    if is_theme_name(theme):
        return theme

    return DEFAULT_THEME


def save_theme(theme: ThemeName) -> None:
    APP_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(APP_SETTINGS_PATH, "w", encoding="utf-8") as file:
        json.dump(
            {"theme": theme},
            file,
            indent=4,
            ensure_ascii=False,
        )


def read_style(path: Path) -> str:
    if not path.exists():
        return ""

    return path.read_text(encoding="utf-8")


def get_stylesheet(theme: ThemeName) -> str:
    base_style = read_style(BASE_STYLE_PATH)

    if theme == "dark":
        theme_style = read_style(DARK_STYLE_PATH)
    else:
        theme_style = read_style(LIGHT_STYLE_PATH)

    return base_style + "\n" + theme_style


def parameters_to_settings_dict(parameters: Parameters) -> dict[str, float]:
    return {
        "v0": float(parameters.initial_velocity),
        "angle_deg": float(parameters.initial_angle_degrees),
        "mass": float(parameters.mass),
        "radius": float(parameters.radius),
        "cd": float(parameters.drag_coefficient),
        "rho": float(parameters.air_density),
        "linear_drag": float(parameters.linear_drag),
        "dt": float(parameters.time_step),
        "t_max": float(parameters.time_max),
        "g": float(parameters.g),
        "wind_speed": float(parameters.wind_speed),
        "wind_angle_deg": float(parameters.wind_angle_degrees),
    }


def settings_dict_to_parameters(settings: dict[str, float]) -> Parameters:
    return Parameters(
        initial_velocity=settings["v0"],
        initial_angle_degrees=settings["angle_deg"],
        mass=settings["mass"],
        radius=settings["radius"],
        drag_coefficient=settings["cd"],
        air_density=settings["rho"],
        linear_drag=settings["linear_drag"],
        time_step=settings["dt"],
        time_max=settings["t_max"],
        g=settings["g"],
        wind_speed=settings["wind_speed"],
        wind_angle_degrees=settings["wind_angle_deg"],
    )


def load_user_settings() -> Parameters:
    if not USER_SETTINGS_PATH.exists():
        return DEFAULT_PARAMETERS

    try:
        with open(USER_SETTINGS_PATH, "r", encoding="utf-8") as file:
            loaded_json: object = json.load(file)

        if not is_settings_data(loaded_json):
            return DEFAULT_PARAMETERS

        settings = parameters_to_settings_dict(DEFAULT_PARAMETERS)

        for key in SETTINGS_KEYS:
            loaded_value = loaded_json.get(key)

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
