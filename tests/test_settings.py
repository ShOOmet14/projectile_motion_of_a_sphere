import pytest
import json
from pathlib import Path

from src.config import settings


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
