# pending to assure stylesheet data and fonts are only loaded once

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter
from pandas import Timestamp

from tesorotools.utils.config import merge
from tesorotools.utils.globals import DEBUG
from tesorotools.utils.matplotlib import (
    PLOT_CONFIG,
    format_annotation,
    load_fonts,
)

TYPE_CURVE_CONFIG: dict[str, Any] = PLOT_CONFIG["type_curve"]
AX_CONFIG: dict[str, Any] = PLOT_CONFIG["ax"]
FIG_CONFIG: dict[str, Any] = PLOT_CONFIG["figure"]

load_fonts()


def _style_spines(
    ax: plt.Axes,
    decimals: int,
    units: str,
    *,
    color: str,
    linewidth: str,
):
    ax.grid(visible=True, axis="y")
    for spine in ax.spines.values():
        spine.set_color(color)
        spine.set_linewidth(linewidth)
    ax.yaxis.tick_right()
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda y, _: format_annotation(y, decimals, units))
    )
    ax.tick_params(axis="both", which="major")
    ax.set_xticks(
        ax.get_xticks(), ax.get_xticklabels(), rotation=45, ha="right"
    )
    for tick in ax.get_xticklines():
        tick.set_markeredgecolor(color)
    for tick in ax.get_yticklines():
        tick.set_markeredgecolor(color)


def _style_baseline(ax: plt.Axes, **baseline_config):
    color: str = baseline_config["color"]
    bottom_lim, top_lim = ax.get_ylim()
    ax.set_ylim(bottom=min(0, bottom_lim), top=max(0, top_lim))
    bottom_lim, top_lim = ax.get_ylim()
    if bottom_lim == 0:
        ax.spines["bottom"].set_edgecolor(color)
    elif top_lim == 0:
        ax.spines["top"].set_edgecolor(color)
    else:
        ax.axhline(y=0, **baseline_config)


def _format_data(data: pd.DataFrame) -> dict[str, Any]:
    # metadata
    date_index: pd.DatetimeIndex = data.index
    current_date: Timestamp = date_index.max()
    current_year: int = current_date.year
    last_year: int = (current_date - pd.DateOffset(years=1)).year

    # current data
    current_data: pd.Series = data.loc[current_date, :]
    current_data.name = "current_data"

    # current year
    current_year_data: pd.DataFrame = data.loc[
        date_index.year == current_year, :
    ]
    current_year_max: pd.Series = current_year_data.max()
    current_year_max.name = "current_year_max"
    current_year_min: pd.Series = current_year_data.min()
    current_year_min.name = "current_year_min"

    # last year
    last_year_data: pd.DataFrame = data.loc[date_index.year == last_year, :]
    last_year_max: pd.Series = last_year_data.max()
    last_year_max.name = "last_year_max"
    last_year_min: pd.Series = last_year_data.min()
    last_year_min.name = "last_year_min"

    formatted_data: pd.DataFrame = pd.concat(
        [
            last_year_max,
            last_year_min,
            current_year_max,
            current_year_min,
            current_data,
        ],
        axis=1,
    )

    return {
        "data": formatted_data,
        "current_date": current_date.strftime("%d/%m/%Y"),
        "current_year": current_year,
        "last_year": last_year,
    }


def _plot_current_data(
    ax: plt.Axes,
    data: pd.DataFrame,
    date_fmt: str,
    *,
    linewidth: float,
    marker: str,
    points_to_mark: list[str],
    color: str,
    decimals: int,
    units: str,
):
    data.plot(
        ax=ax,
        color=color,
        linewidth=linewidth,
        label=date_fmt,
    )
    for point in points_to_mark:
        value = data.loc[point]
        ax.plot(
            point,
            value,
            marker=marker,
            color=color,
        )
        ax.annotate(
            format_annotation(value, decimals, units),
            (point, value),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
        )


def plot_type_curve(
    data: pd.DataFrame,
    out_file: Path,
    **config,
):
    config: dict[str, Any] = merge(config, TYPE_CURVE_CONFIG)

    if config["yaxis"]["units"] == "p.b.":
        data = data * 100

    formatted_assets: dict[str, Any] = _format_data(data)
    formatted_data: pd.DataFrame = formatted_assets["data"]
    due_index: pd.Index = formatted_data.index

    fig = plt.figure(**FIG_CONFIG)
    ax: plt.Axes = fig.add_subplot()

    last_config: dict[str, Any] = config["last"]
    ax.fill_between(
        due_index,
        formatted_data["last_year_min"],
        formatted_data["last_year_max"],
        alpha=last_config["alpha"],
        color=last_config["color"],
        edgecolor=None,
        label=f"Rango {formatted_assets['last_year']}",
    )

    current_config: dict[str, Any] = config["current"]
    ax.fill_between(
        due_index,
        formatted_data["current_year_min"],
        formatted_data["current_year_max"],
        alpha=current_config["alpha"],
        color=current_config["color"],
        edgecolor=None,
        label=f"Rango {formatted_assets['current_year']}",
    )

    _plot_current_data(
        ax,
        formatted_data["current_data"],
        formatted_assets["current_date"],
        **config["line"],
    )
    _style_spines(ax, **config["yaxis"], **AX_CONFIG["spines"])
    _style_baseline(ax, **AX_CONFIG["baseline"])
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, config["legend_sep"]),
        ncol=3,
    )
    fig.savefig(out_file)


# data is expected to be a simple time series data, columns are series and rows represents dates
def plot_type_curves(
    out_path: Path, data: pd.DataFrame, config_dicts: dict[str, Any]
):
    for name, config in config_dicts.items():
        if not name.startswith("."):  # aux entries
            series: dict[str, str] = config["series"]
            if len(series) < 2:
                raise ValueError(
                    f"In plot {name}: A type curve must have at least two due periods. Given periods: {series.keys()}"
                )
            trimmed_data: pd.DataFrame = data.loc[:, series.keys()]
            trimmed_data: pd.DataFrame = trimmed_data.rename(columns=series)
            plot_type_curve(
                data=trimmed_data,
                out_file=out_path / f"{name}.png",
                **config,
            )
