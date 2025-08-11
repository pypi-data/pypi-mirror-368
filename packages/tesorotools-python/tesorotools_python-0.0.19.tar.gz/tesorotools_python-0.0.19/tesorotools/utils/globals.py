import platform
from pathlib import Path

SYSTEM: str = platform.system()


BASE_PATH: Path = Path(__file__).parent.parent

DEBUG: Path = Path("debug")
CONFIG: Path = Path("config")
EXAMPLES: Path = Path("examples")

# various assets for the plots
ASSETS: Path = BASE_PATH / "assets"
FONTS: Path = ASSETS / "fonts"
STYLE_SHEET: Path = ASSETS / "tesoro.mplstyle"

PLOT_CONFIG_FILE: Path = ASSETS / "plots.yaml"
