"""
Este módulo trata de recoger todas las comunalidades de las bases de datos locales que tenemos en OneDrive, para estandarizar el trabajo con ellas y evitarnos dolores de cabeza en el futuro.
"""

from pathlib import Path

from tesorotools.utils import SYSTEM
from tesorotools.utils.shortcuts import resolve_shortcut


class LocalDatabase:
    """
    Todas las bases de datos locales que tenemos deben ser una instancia de esta, ya sea directamente o a través de una subclase
    """

    def __init__(self, root_path: Path):
        self.root_path: Path = root_path

    def get_year_path(self, year: int) -> Path:
        return self.root_path / str(year)

    def get_raw_path(self, year: int) -> Path:
        return self.get_year_path(year) / "raw"

    def get_processed_path(self, year: int) -> Path:
        processed_path: Path = self.get_year_path(year) / "processed"
        processed_path.mkdir(parents=True, exist_ok=True)
        return processed_path

    def get_products_path(self, year: int) -> Path:
        products_path: Path = self.get_year_path(year) / "products"
        products_path.mkdir(parents=True, exist_ok=True)
        return products_path


class ShortcutDatabase(LocalDatabase):
    """Base de datos local cuya ruta viene data a través de un acceso directo (Windows) o enlace simbólico (Linux)"""

    def __init__(self, root_path: Path, shortcut: str):
        db_path = (
            root_path / f"{shortcut}.lnk"
            if SYSTEM == "Windows"
            else root_path / shortcut
        )
        db_resolved_path: Path = resolve_shortcut(db_path)
        super().__init__(root_path=db_resolved_path)
