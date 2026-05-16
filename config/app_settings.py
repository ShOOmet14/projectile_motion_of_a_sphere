import json

from pathlib import Path
from typing import Literal, TypeGuard


ThemeName = Literal["light", "dark"]

APP_SETTINGS_PATH = Path(__file__).with_name("app_settings.json")
DEFAULT_THEME: ThemeName = "light"


def is_settings_data(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict)


def is_theme_name(value: object) -> TypeGuard[ThemeName]:
    return value in ("light", "dark")


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
