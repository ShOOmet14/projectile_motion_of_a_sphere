"""Manage theme preferences, stylesheets, and saved simulation parameters.

This module loads and saves JSON configuration files, combines the base
stylesheet with a theme-specific stylesheet, and converts between persisted
settings values and validated ``Parameters`` instances.
"""

import json
from pathlib import Path
from typing import Literal, TypeGuard

from src.config.parameters import DEFAULT_PARAMETERS, Parameters


ThemeName = Literal["light", "dark"]

_CONFIG_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CONFIG_DIR.parent.parent
_STYLE_DIR = _PROJECT_ROOT / "style"

APP_SETTINGS_PATH = _CONFIG_DIR / "app_settings.json"
USER_SETTINGS_PATH = _CONFIG_DIR / "user_settings.json"

BASE_STYLE_PATH = _STYLE_DIR / "style.css"
LIGHT_STYLE_PATH = _STYLE_DIR / "light.css"
DARK_STYLE_PATH = _STYLE_DIR / "dark.css"

DEFAULT_THEME: ThemeName = "light"

_NumberLike = int | float | str

# JSON keys used to persist simulation parameters and load saved overrides.
_SETTINGS_KEYS: tuple[str, ...] = (
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
    "initial_x",
    "initial_y",
)


def is_settings_data(value: object) -> TypeGuard[dict[str, object]]:
    """Check whether the provided value is a dictionary.

    Args:
        value: The object to check.

    Returns:
        True if the value is a dictionary; otherwise, False.
    """

    return isinstance(value, dict)


def is_theme_name(value: object) -> TypeGuard[ThemeName]:
    """Check whether the provided value is a supported theme name.

    Args:
        value: The object to check.

    Returns:
        True if the value is either ``"light"`` or ``"dark"``; otherwise,
        False.
    """

    return value in ("light", "dark")


def is_number_like(value: object) -> TypeGuard[_NumberLike]:
    """Check whether the provided value has a supported settings-value type.

    Args:
        value: The object to check.

    Returns:
        True if the value is an integer, float, or string, excluding Boolean
        values; otherwise, False.
    """

    # bool is a subclass of int, so it must be rejected explicitly.
    return not isinstance(value, bool) and isinstance(value, int | float | str)


def load_theme() -> ThemeName:
    """Load the saved application theme.

    Returns:
        The saved theme name, or ``DEFAULT_THEME`` if the settings file is
        missing, cannot be opened, contains malformed JSON, or does not contain
        a supported theme name.
    """

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
    """Save the selected application theme.

    Args:
        theme: The theme name to save.

    Raises:
        OSError: If the settings directory or file cannot be written.
    """

    APP_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(APP_SETTINGS_PATH, "w", encoding="utf-8") as file:
        json.dump(
            {"theme": theme},
            file,
            indent=4,
            ensure_ascii=False,
        )


def read_style(path: Path) -> str:
    """Read a stylesheet file.

    Args:
        path: The path to the stylesheet file.

    Returns:
        The stylesheet content, or an empty string if the file does not exist.

    Raises:
        OSError: If an existing stylesheet file cannot be read.
        UnicodeDecodeError: If the file does not contain valid UTF-8 text.
    """

    if not path.exists():
        return ""

    return path.read_text(encoding="utf-8")


def get_stylesheet(theme: ThemeName) -> str:
    """Build the complete stylesheet for the selected application theme.

    Args:
        theme: The theme whose stylesheet should be loaded.

    Returns:
        The base stylesheet followed by the selected theme stylesheet.

    Raises:
        OSError: If an existing stylesheet file cannot be read.
        UnicodeDecodeError: If a stylesheet does not contain valid UTF-8 text.
    """

    base_style = read_style(BASE_STYLE_PATH)

    if theme == "dark":
        theme_style = read_style(DARK_STYLE_PATH)
    else:
        theme_style = read_style(LIGHT_STYLE_PATH)

    return base_style + "\n" + theme_style


def parameters_to_settings_dict(parameters: Parameters) -> dict[str, float]:
    """Convert simulation parameters to JSON-compatible settings values.

    Args:
        parameters: The simulation parameters to convert.

    Returns:
        A dictionary mapping persisted setting names to floating-point values.
    """

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
        "initial_x": float(parameters.initial_x),
        "initial_y": float(parameters.initial_y),
    }


def settings_dict_to_parameters(settings: dict[str, float]) -> Parameters:
    """Create validated simulation parameters from a settings dictionary.

    Args:
        settings: A dictionary containing all required simulation settings.

    Returns:
        A validated ``Parameters`` instance.

    Raises:
        KeyError: If a required setting is missing.
        TypeError: If a setting has an incompatible type.
        ValueError: If a setting value is outside its supported range.
    """

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
        initial_x=settings["initial_x"],
        initial_y=settings["initial_y"],
    )


def load_user_settings() -> Parameters:
    """Load saved simulation parameters and apply valid overrides to defaults.

    Saved integer, float, and string values override the corresponding default
    values. Missing keys and values with unsupported types retain their default
    values. If file access, JSON parsing, numeric conversion, or parameter
    validation fails, the complete default configuration is returned.

    Returns:
        The loaded and validated simulation parameters, or
        ``DEFAULT_PARAMETERS`` if loading fails.
    """

    if not USER_SETTINGS_PATH.exists():
        return DEFAULT_PARAMETERS

    try:
        with open(USER_SETTINGS_PATH, "r", encoding="utf-8") as file:
            loaded_json: object = json.load(file)

        if not is_settings_data(loaded_json):
            return DEFAULT_PARAMETERS

        # Start with defaults so that missing saved values need no special case.
        settings = parameters_to_settings_dict(DEFAULT_PARAMETERS)

        for key in _SETTINGS_KEYS:
            loaded_value = loaded_json.get(key)

            if is_number_like(loaded_value):
                settings[key] = float(loaded_value)

        return settings_dict_to_parameters(settings)

    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return DEFAULT_PARAMETERS


def save_user_settings(parameters: Parameters) -> None:
    """Save simulation parameters as JSON.

    Args:
        parameters: The simulation parameters to save.

    Raises:
        OSError: If the settings directory or file cannot be written.
    """

    USER_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    settings_data = parameters_to_settings_dict(parameters)

    with open(USER_SETTINGS_PATH, "w", encoding="utf-8") as file:
        json.dump(
            settings_data,
            file,
            indent=4,
            ensure_ascii=False,
        )
