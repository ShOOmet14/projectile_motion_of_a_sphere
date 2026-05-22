import json
from pathlib import Path
from typing import cast

import pytest

from src.config import settings
from src.config.parameters import DEFAULT_PARAMETERS, Parameters
from src.config.settings import ThemeName


@pytest.fixture
def settings_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> dict[str, Path]:
    config_dir = tmp_path / "config"
    style_dir = tmp_path / "style"

    monkeypatch.setattr(settings, "APP_SETTINGS_PATH", config_dir / "app_settings.json")
    monkeypatch.setattr(
        settings, "USER_SETTINGS_PATH", config_dir / "user_settings.json"
    )

    monkeypatch.setattr(settings, "BASE_STYLE_PATH", style_dir / "style.css")
    monkeypatch.setattr(settings, "LIGHT_STYLE_PATH", style_dir / "light.css")
    monkeypatch.setattr(settings, "DARK_STYLE_PATH", style_dir / "dark.css")

    return {
        "app_settings": config_dir / "app_settings.json",
        "user_settings": config_dir / "user_settings.json",
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


def test_save_theme_writes_theme_to_file(
    settings_paths: dict[str, Path],
) -> None:
    settings.save_theme("dark")

    saved_data = json.loads(settings_paths["app_settings"].read_text(encoding="utf-8"))

    assert saved_data == {"theme": "dark"}


def test_read_style_returns_empty_string_when_file_is_missing(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.css"

    assert settings.read_style(missing_path) == ""


def test_read_style_reads_existing_file(tmp_path: Path) -> None:
    style_path = tmp_path / "style.css"
    style_path.write_text("QWidget { color: red; }", encoding="utf-8")

    assert settings.read_style(style_path) == "QWidget { color: red; }"


def test_get_stylesheet_uses_light_theme(
    settings_paths: dict[str, Path],
) -> None:
    settings_paths["base_style"].parent.mkdir(parents=True, exist_ok=True)
    settings_paths["base_style"].write_text("base", encoding="utf-8")
    settings_paths["light_style"].write_text("light", encoding="utf-8")
    settings_paths["dark_style"].write_text("dark", encoding="utf-8")

    assert settings.get_stylesheet("light") == "base\nlight"


def test_get_stylesheet_uses_dark_theme(
    settings_paths: dict[str, Path],
) -> None:
    settings_paths["base_style"].parent.mkdir(parents=True, exist_ok=True)
    settings_paths["base_style"].write_text("base", encoding="utf-8")
    settings_paths["light_style"].write_text("light", encoding="utf-8")
    settings_paths["dark_style"].write_text("dark", encoding="utf-8")

    assert settings.get_stylesheet("dark") == "base\ndark"


def test_parameters_to_settings_dict() -> None:
    parameters = Parameters(
        initial_velocity=12.0,
        initial_angle_degrees=30.0,
        mass=2.0,
        radius=0.5,
        drag_coefficient=0.1,
        air_density=1.1,
        linear_drag=0.3,
        time_step=0.02,
        time_max=4.0,
        g=9.81,
        wind_speed=3.0,
        wind_angle_degrees=180.0,
    )

    result = settings.parameters_to_settings_dict(parameters)

    assert result == {
        "v0": 12.0,
        "angle_deg": 30.0,
        "mass": 2.0,
        "radius": 0.5,
        "cd": 0.1,
        "rho": 1.1,
        "linear_drag": 0.3,
        "dt": 0.02,
        "t_max": 4.0,
        "g": 9.81,
        "wind_speed": 3.0,
        "wind_angle_deg": 180.0,
    }


def test_settings_dict_to_parameters() -> None:
    data: dict[str, float] = {
        "v0": 12.0,
        "angle_deg": 30.0,
        "mass": 2.0,
        "radius": 0.5,
        "cd": 0.1,
        "rho": 1.1,
        "linear_drag": 0.3,
        "dt": 0.02,
        "t_max": 4.0,
        "g": 9.81,
        "wind_speed": 3.0,
        "wind_angle_deg": 180.0,
    }

    result = settings.settings_dict_to_parameters(data)

    assert result == Parameters(
        initial_velocity=12.0,
        initial_angle_degrees=30.0,
        mass=2.0,
        radius=0.5,
        drag_coefficient=0.1,
        air_density=1.1,
        linear_drag=0.3,
        time_step=0.02,
        time_max=4.0,
        g=9.81,
        wind_speed=3.0,
        wind_angle_degrees=180.0,
    )


def test_load_user_settings_returns_default_when_file_is_missing(
    settings_paths: dict[str, Path],
) -> None:
    assert settings.load_user_settings() == DEFAULT_PARAMETERS


def test_load_user_settings_reads_complete_file(
    settings_paths: dict[str, Path],
) -> None:
    parameters = Parameters(
        initial_velocity=20.0,
        initial_angle_degrees=60.0,
        mass=1.5,
        radius=0.2,
        drag_coefficient=0.2,
        air_density=1.0,
        linear_drag=0.1,
        time_step=0.05,
        time_max=5.0,
        g=9.8,
        wind_speed=4.0,
        wind_angle_degrees=90.0,
    )

    write_json(
        settings_paths["user_settings"],
        settings.parameters_to_settings_dict(parameters),
    )

    assert settings.load_user_settings() == parameters


def test_load_user_settings_uses_defaults_for_missing_keys(
    settings_paths: dict[str, Path],
) -> None:
    write_json(
        settings_paths["user_settings"],
        {
            "v0": 25,
            "angle_deg": "30",
        },
    )

    result = settings.load_user_settings()

    assert result.initial_velocity == 25.0
    assert result.initial_angle_degrees == 30.0
    assert result.mass == DEFAULT_PARAMETERS.mass
    assert result.radius == DEFAULT_PARAMETERS.radius
    assert result.g == DEFAULT_PARAMETERS.g


@pytest.mark.parametrize(
    "content",
    [
        "not valid json",
        json.dumps([]),
        json.dumps({"v0": "not a number"}),
        json.dumps({"mass": 0.0}),
    ],
)
def test_load_user_settings_returns_default_for_invalid_file(
    settings_paths: dict[str, Path],
    content: str,
) -> None:
    settings_paths["user_settings"].parent.mkdir(parents=True, exist_ok=True)
    settings_paths["user_settings"].write_text(content, encoding="utf-8")

    assert settings.load_user_settings() == DEFAULT_PARAMETERS


def test_load_user_settings_ignores_bool_values(
    settings_paths: dict[str, Path],
) -> None:
    write_json(
        settings_paths["user_settings"],
        {
            "v0": True,
            "angle_deg": 30.0,
        },
    )

    result = settings.load_user_settings()

    assert result.initial_velocity == DEFAULT_PARAMETERS.initial_velocity
    assert result.initial_angle_degrees == 30.0


def test_save_user_settings_writes_parameters_to_file(
    settings_paths: dict[str, Path],
) -> None:
    parameters = Parameters(
        initial_velocity=20.0,
        initial_angle_degrees=60.0,
        mass=1.5,
        radius=0.2,
        drag_coefficient=0.2,
        air_density=1.0,
        linear_drag=0.1,
        time_step=0.05,
        time_max=5.0,
        g=9.8,
        wind_speed=4.0,
        wind_angle_degrees=90.0,
    )

    settings.save_user_settings(parameters)

    saved_data = json.loads(settings_paths["user_settings"].read_text(encoding="utf-8"))

    assert saved_data == settings.parameters_to_settings_dict(parameters)


def test_save_and_load_user_settings_round_trip(
    settings_paths: dict[str, Path],
) -> None:
    parameters = Parameters(
        initial_velocity=15.0,
        initial_angle_degrees=40.0,
        mass=0.5,
        radius=0.1,
        drag_coefficient=0.3,
        air_density=1.2,
        linear_drag=0.05,
        time_step=0.02,
        time_max=3.0,
        g=9.81,
        wind_speed=2.0,
        wind_angle_degrees=45.0,
    )

    settings.save_user_settings(parameters)

    assert settings.load_user_settings() == parameters
