from math import floor
from pathlib import Path
from typing import Any

import pandas as pd

from tesorotools.dependencies.resolution import collect_series
from tesorotools.offsets.outliers import flag_outliers
from tesorotools.utils.globals import DEBUG
from tesorotools.utils.matplotlib import format_annotation, is_zero

# this file is by far the worst and most spaghettified, must be rewritten

# to global config
GOOD: str = "00c800"
BAD: str = "c80000"
THRESHOLD: float = 1
SHADE_LEVELS = 2


def _shade_intensity(
    ratio: float, shade_levels: int = 2, continuous: bool = False
) -> str:
    # intensity may vary from 150 (highest) to 255 (lowest), a grand difference of 105
    # there are SHADE_LEVELS levels, so increments will be of 105/SHADE_LEVELS
    corrected_ratio: float = min(ratio, shade_levels)
    corrected_ratio: float = (
        floor(corrected_ratio) if not continuous else corrected_ratio
    )
    increment: float = (corrected_ratio - 1) * (105 / shade_levels)
    intensity: float = 255 - increment
    intensity_hex: str = f"{int(intensity):x}"
    return intensity_hex


def _generate_column(
    column_data: pd.Series,
    column_cfg: dict[str, Any],
    outliers_flags: pd.Series | None = None,
):
    # TODO: factor out
    # data
    if column_cfg["show_units_in_title"]:
        column_data.name = f"{column_cfg["name"]} ({column_cfg["unit"]})"
    else:
        column_data.name = column_cfg["name"]
    column_cfg["formatted_name"] = column_data.name

    unit = (
        column_cfg["unit"]
        if column_cfg["show_units_in_cell"] and column_cfg["unit"] is not None
        else ""
    )
    scaled_data: pd.Series = column_data * column_cfg["scale"]
    formatted_data = scaled_data.apply(
        lambda x: format_annotation(
            x, decimals=column_cfg["decimals"], units=unit
        )
    )
    zeros: pd.Series = scaled_data.apply(
        lambda x: is_zero(x, decimals=column_cfg["decimals"])
    )
    positives: pd.Series = scaled_data > 0
    negatives: pd.Series = scaled_data < 0

    # colors
    colors_cfg: bool = column_cfg["colors"]
    color_data: pd.Series = pd.Series(
        index=formatted_data.index, name=column_data.name, dtype=str
    )
    if colors_cfg:
        positive_good: bool = column_cfg["positive_good"]
        color_data[positives] = GOOD if positive_good else BAD
        color_data.loc[negatives] = BAD if positive_good else GOOD
        color_data.loc[zeros.values] = pd.NA

    # shades
    shade_data: pd.Series = pd.Series(
        index=formatted_data.index, name=column_data.name, dtype=str
    )
    if outliers_flags is not None:
        thresholds: pd.Series = abs(outliers_flags / THRESHOLD)
        intensities: pd.Series = thresholds.apply(
            lambda x: _shade_intensity(x, SHADE_LEVELS)
        )
        shade_data[(thresholds >= 1) & (outliers_flags > 0)] = intensities[
            (thresholds >= 1) & (outliers_flags > 0)
        ].apply(lambda x: f"00{x}00" if positive_good else f"{x}0000")
        shade_data[(thresholds >= 1) & (outliers_flags < 0)] = intensities[
            (thresholds >= 1) & (outliers_flags < 0)
        ].apply(lambda x: f"{x}0000" if positive_good else f"00{x}00")

    return formatted_data, color_data, shade_data


def _generate_block(block_data: pd.DataFrame, block_cfg: dict[str, Any]):
    columns: dict[str, Any] = block_cfg["columns"]
    formatted_columns: list[pd.Series] = []
    color_columns: list[pd.Series] = []
    shade_columns: list[pd.Series] = []
    sort_idx: pd.Index | None = None
    for column_name, column_cfg in columns.items():
        last_date: pd.Timestamp = block_data.index.get_level_values(
            level=0
        ).max()
        block_data = block_data.rename(columns=block_cfg["series"])
        offset: str = column_cfg["offset"]
        difference: str = column_cfg["difference"]
        stat: str = column_cfg["stat"]
        outliers: bool = column_cfg["outliers"]

        stat_data = block_data.loc[
            (last_date, offset, difference, slice(None)), :
        ]
        stat_data.index = stat_data.index.get_level_values(level=-1)

        outliers_flags: pd.Series | None = None
        if outliers:
            outliers_flags = flag_outliers(stat_data.T)

        column_data: pd.Series = stat_data.loc[stat, :]
        # sort capability
        sort: str = block_cfg.get("sort", None)
        if sort is not None and column_name == sort:
            column_data: pd.Series = column_data.sort_values(ascending=False)
            sort_idx = column_data.index
        formatted_column, color_column, shade_column = _generate_column(
            column_data, column_cfg, outliers_flags
        )
        formatted_columns.append(formatted_column)
        color_columns.append(color_column)
        shade_columns.append(shade_column)

    if sort_idx is not None:
        formatted_columns = [s.reindex(sort_idx) for s in formatted_columns]
        color_columns = [s.reindex(sort_idx) for s in color_columns]
        shade_columns = [s.reindex(sort_idx) for s in shade_columns]

    formatted_block: pd.DataFrame = pd.concat(formatted_columns, axis=1)
    color_block: pd.DataFrame = pd.concat(color_columns, axis=1)
    shade_block: pd.DataFrame = pd.concat(shade_columns, axis=1)

    formatted_block.columns.name = block_cfg["title"]
    color_block.columns.name = block_cfg["title"]
    shade_block.columns.name = block_cfg["title"]
    return formatted_block, color_block, shade_block


def generate_table(table_data: pd.DataFrame, table_cfg: dict[str, Any]):
    blocks: dict[str, dict] = table_cfg["blocks"]
    formatted_blocks: list[pd.DataFrame] = []
    color_blocks: list[pd.DataFrame] = []
    shade_blocks: list[pd.DataFrame] = []
    axis = 0 if table_cfg["axis"] == "vertical" else 1
    # sorting capabilities
    for block_name, block_cfg in blocks.items():
        series_dict: dict[str, str] = block_cfg["series"]
        block_data: pd.DataFrame = table_data.loc[:, series_dict.keys()]
        formatted_block, color_block, shade_block = _generate_block(
            block_data, block_cfg
        )
        formatted_blocks.append(formatted_block)
        color_blocks.append(color_block)
        shade_blocks.append(shade_block)
    formatted_table = pd.concat(
        formatted_blocks,
        axis=axis,
        keys=[
            formatted_block.columns.name for formatted_block in formatted_blocks
        ],
    )
    color_table = pd.concat(
        color_blocks,
        axis=axis,
        keys=[
            formatted_block.columns.name for formatted_block in formatted_blocks
        ],
    )
    shade_table = pd.concat(
        shade_blocks,
        axis=axis,
        keys=[
            formatted_block.columns.name for formatted_block in formatted_blocks
        ],
    )
    return formatted_table, color_table, shade_table


def generate_tables_from_flash(
    out_path: Path, flash: pd.DataFrame, config_dicts: dict[str, dict]
):
    for table_name, table_cfg in config_dicts.items():
        series: list[str] = list(collect_series(table_cfg))
        table_data: pd.DataFrame = flash.loc[:, series]
        formatted_table, color_table, shade_table = generate_table(
            table_data, table_cfg
        )
        formatted_table.to_feather(out_path / f"{table_name}.feather")
        color_table.to_feather(out_path / f"{table_name}_color.feather")
        shade_table.to_feather(out_path / f"{table_name}_shade.feather")
