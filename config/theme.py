from pathlib import Path

from config.app_settings import ThemeName

STYLE_DIR = Path(__file__).resolve().parents[1] / "style"

BASE_STYLE_PATH = STYLE_DIR / "style.css"
LIGHT_STYLE_PATH = STYLE_DIR / "light.css"
DARK_STYLE_PATH = STYLE_DIR / "dark.css"


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
