from pathlib import Path

import docx
import pandas as pd

from tesorotools.artists.table import generate_tables_from_flash
from tesorotools.render.content.table import render_table
from tesorotools.utils.config import read_config
from tesorotools.utils.globals import DEBUG, EXAMPLES

if __name__ == "__main__":
    # test tables here
    table_config_file: Path = EXAMPLES / "tables.yaml"
    offsets_config_file: Path = EXAMPLES / "offsets.yaml"

    config_dicts = read_config(table_config_file)
    offsets_config = read_config(offsets_config_file)

    flash = pd.read_feather("derivates.feather")
    generate_tables_from_flash(flash, config_dicts)

    document = docx.Document("template.docx")
    for table_path in (DEBUG / "table").iterdir():
        if table_path.stem.endswith(("color", "shade")):
            continue
        table_dict = config_dicts[table_path.stem]
        table: pd.DataFrame = pd.read_feather(table_path)
        color: pd.DataFrame = pd.read_feather(
            table_path.parent / f"{table_path.stem}_color.feather"
        )
        shade: pd.DataFrame = pd.read_feather(
            table_path.parent / f"{table_path.stem}_shade.feather"
        )

        render_table(table, color, shade, document, **table_dict)
        document.add_paragraph()
    document.save("test.docx")
