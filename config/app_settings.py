import json

from pathlib import Path
from typing import Literal, cast

ThemeName = Literal["light", "dark"]

APP_SETTINGS_PATH = Path(__file__).with_name("app_settings.json")
DEFAULT_THEME: ThemeName = "light"


def load_theme() -> ThemeName:
    if not APP_SETTINGS_PATH.exists():
        return DEFAULT_THEME

    try:
        with open(APP_SETTINGS_PATH, "r", encoding="utf-8") as file:
            data: object = json.load(file)

        if not isinstance(data, dict):
            return DEFAULT_THEME

        theme = data.get("theme")

        if theme in ("light", "dark"):
            return cast(ThemeName, theme)

    except (OSError, json.JSONDecodeError):
        return DEFAULT_THEME

    return DEFAULT_THEME


def save_theme(theme: ThemeName) -> None:
    APP_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(APP_SETTINGS_PATH, "w", encoding="utf-8") as file:
        json.dump({"theme": theme}, file, indent=4, ensure_ascii=False)
