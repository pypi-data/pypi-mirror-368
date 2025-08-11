# this file may migrate to the utils package

from pathlib import Path

import pandas as pd

from tesorotools.artists.barh_plot import plot_barh_charts_from_flash
from tesorotools.artists.line_plot import plot_line_charts
from tesorotools.artists.table import generate_tables_from_flash
from tesorotools.artists.type_curve import plot_type_curves
from tesorotools.dependencies.resolution import (
    compute_derivate_series,
    concat_derivate_series,
    resolve_series,
)
from tesorotools.offsets.offsets import trim
from tesorotools.utils.config import read_config


def index_replace(old: str, new: str, index: pd.MultiIndex) -> pd.MultiIndex:
    return pd.MultiIndex.from_tuples(
        [
            tuple(
                [
                    x.replace(old, new) if isinstance(x, str) else x
                    for x in tuple_index
                ]
            )
            for tuple_index in index
        ]
    )


def cheap_convert(old_file: Path) -> pd.DataFrame:
    old = pd.read_feather(old_file)

    trimmed = old.loc[(slice(None), "no", "absolute", "value"), :].copy()

    old = old.loc[
        (
            slice(None),
            ["day", "mtd", "week", "year", "tariff_crisis"],
            slice(None),
            slice(None),
        ),
        :,
    ]
    old.index = index_replace("day", "bday", old.index)
    old.index = index_replace("week", "ftd", old.index)
    old.index = index_replace("year", "ytd", old.index)
    old.index = index_replace("roll_var", "roll_std", old.index)
    old.index = index_replace("tariff_crisis", "2025-04-02", old.index)

    trimmed.index = index_replace("absolute", "no", trimmed.index)

    new = pd.concat([old, trimmed])
    return new


if __name__ == "__main__":
    preprocess = True
    barh_config_dicts = read_config(Path("examples") / "barh_plots.yaml")
    line_config_dicts = read_config(Path("examples") / "line_plots.yaml")
    type_config_dicts = read_config(Path("examples") / "type_curves.yaml")
    table_config_dicts = read_config(Path("examples") / "tables.yaml")

    if preprocess:
        old_file: Path = Path("debug") / "flash.feather"
        dependencies_cfg = read_config(Path("examples") / "dependencies.yaml")
        flash: pd.DataFrame = cheap_convert(old_file)
        resolved_dict = resolve_series(
            [
                barh_config_dicts,
                line_config_dicts,
                type_config_dicts,
                table_config_dicts,
            ],
            dependencies_cfg,
        )
        independent_full_df = flash.loc[:, list(resolved_dict["independent"])]
        independent_trimmed_df = trim(independent_full_df)
        dependent_trimmed_df = compute_derivate_series(
            resolved_dict["dependent"], independent_trimmed_df
        )
        offsets_config = read_config(Path("examples") / "offsets.yaml")
        full_df = concat_derivate_series(
            independent_full_df,
            dependent_trimmed_df,
            offsets_config,
            # force_trim=True,
        )
        full_df.to_feather("derivates.feather")

    full_df = pd.read_feather("derivates.feather")
    trimmed_df = trim(full_df)
    plot_barh_charts_from_flash(full_df, barh_config_dicts)
    plot_line_charts(trimmed_df, line_config_dicts)
    plot_type_curves(trimmed_df, type_config_dicts)
    generate_tables_from_flash(full_df, table_config_dicts)
