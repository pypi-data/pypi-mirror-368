from importlib.resources.abc import Traversable

VERSION: str = "16.0.0"
__version__ = VERSION
BUILD: int = 0

_gh_repo = "hfg-gmuend/openmoji"

LICENSE: str = "CC BY-SA 4.0"
LICENSE_URL: str = "https://creativecommons.org/licenses/by-sa/4.0/"
LICENSE_TEXT_URL: str = f"https://raw.githubusercontent.com/{_gh_repo}/{VERSION}/LICENSE.txt"

ATTRIBUTION: str = (
    "All emojis designed by OpenMoji – the open-source emoji and icon project. "
    "License: CC BY-SA 4.0"
)

SOURCE_URL: str = f"https://github.com/{_gh_repo}"
SOURCE_RELEASE_URL: str = f"{SOURCE_URL}/releases/tag/{VERSION}"
SVG_SOURCE_URL: str = f"{SOURCE_URL}/releases/download/{VERSION}/openmoji-svg-color.zip"
FONT_SOURCE_URL: str = f"{SOURCE_URL}/releases/download/{VERSION}/openmoji-font.zip"

del _gh_repo

_data_dir_name = f"openmoji"


def _get_openmoji_data_dir() -> str:
    from pathlib import Path
    return (Path(__file__).resolve().parent / _data_dir_name).as_posix()


def get_openmoji_data() -> Traversable:
    from importlib.resources import files
    return files(f"openmoji_dist") / _data_dir_name


def get_openmoji_svg_data() -> Traversable:
    return get_openmoji_data() / "svg"


def get_openmoji_font_data() -> Traversable:
    return get_openmoji_data() / "font"
