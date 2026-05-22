import pytest
import json
from pathlib import Path
from typing import cast

from src.config import settings
from src.config.settings import ThemeName


@pytest.fixture
def settings_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    config_directory = tmp_path / "config"
    style_dir = tmp_path / "style"

    monkeypatch.setattr(
        settings, "APP_SETTINGS_PATH", config_directory / "app_settings.json"
    )
    monkeypatch.setattr(
        settings, "USER_SETTINGS_PATH", config_directory / "user_settings.json"
    )
    monkeypatch.setattr(settings, "BASE_STYLE_PATH", style_dir / "style.css")
    monkeypatch.setattr(settings, "LIGHT_STYLE_PATH", style_dir / "light.css")
    monkeypatch.setattr(settings, "DARK_STYLE_PATH", style_dir / "dark.css")

    return {
        "app_settings": config_directory / "app_settings.json",
        "user_settings": config_directory / "user_settings.json",
        "base_style": style_dir / "style.css",
        "light_style": style_dir / "light.css",
        "dark_style": style_dir / "dark.css",
    }


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def test_is_settings_data() -> None:
    assert settings.is_settings_data({}) is True
    assert settings.is_settings_data({"theme": "dark"}) is True
    assert settings.is_settings_data([]) is False
    assert settings.is_settings_data(None) is False
    assert settings.is_settings_data("text") is False


def test_is_theme_name() -> None:
    assert settings.is_theme_name("light") is True
    assert settings.is_theme_name("dark") is True
    assert settings.is_theme_name("blue") is False
    assert settings.is_theme_name(None) is False


def test_is_number_like() -> None:
    assert settings.is_number_like(1) is True
    assert settings.is_number_like(1.5) is True
    assert settings.is_number_like("2.5") is True

    assert settings.is_number_like(True) is False
    assert settings.is_number_like(False) is False
    assert settings.is_number_like(None) is False
    assert settings.is_number_like([]) is False


def test_load_theme_returns_default_when_file_is_missing(
    settings_paths: dict[str, Path],
) -> None:
    assert settings.load_theme() == settings.DEFAULT_THEME


@pytest.mark.parametrize("theme_value", ["light", "dark"])
def test_load_theme_reads_valid_theme(
    settings_paths: dict[str, Path],
    theme_value: str,
) -> None:
    theme = cast(ThemeName, theme_value)

    write_json(settings_paths["app_settings"], {"theme": theme})

    assert settings.load_theme() == theme


@pytest.mark.parametrize(
    "content",
    [
        "not valid json",
        json.dumps([]),
        json.dumps({"theme": "blue"}),
        json.dumps({"theme": None}),
    ],
)
def test_load_theme_returns_default_for_invalid_file(
    settings_paths: dict[str, Path],
    content: str,
) -> None:
    settings_paths["app_settings"].parent.mkdir(parents=True, exist_ok=True)
    settings_paths["app_settings"].write_text(content, encoding="utf-8")

    assert settings.load_theme() == settings.DEFAULT_THEME
