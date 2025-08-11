from typing import Any

import matplotlib
import matplotlib.font_manager

from .config import read_config
from .globals import FONTS, PLOT_CONFIG_FILE

# this should only be done once
PLOT_CONFIG: dict[str, Any] = read_config(PLOT_CONFIG_FILE)


def load_fonts() -> None:
    for font in FONTS.iterdir():
        if font.suffix == ".otf":
            matplotlib.font_manager.fontManager.addfont(font)
    matplotlib.rcParams["font.family"] = PLOT_CONFIG["style"]["font"]


# this is not really matplotlib specific, so it should be elsewhere
def format_annotation(value: float, decimals: int, units: str) -> str:
    decimal_formatted: str = f"{value:_.{decimals}f}".replace(".", ",").replace(
        "_", "."
    )
    decimal_formatted = (
        decimal_formatted[1:]
        if (decimal_formatted.startswith("-0") and decimals == 0)
        else decimal_formatted
    )
    return f"{decimal_formatted}{units}"


def is_zero(value: float, decimals: int) -> bool:
    formatted = format_annotation(value, decimals, units="")
    unique = "".join(set(formatted.replace(",", "").replace(".", "")))
    if unique == "0":
        return True
    return False
