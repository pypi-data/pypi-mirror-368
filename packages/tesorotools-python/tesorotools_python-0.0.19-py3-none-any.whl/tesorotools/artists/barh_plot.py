from enum import Enum
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.container import BarContainer
from matplotlib.ticker import FuncFormatter

from tesorotools.offsets.offsets import Difference, FloatingOffset, Stat
from tesorotools.offsets.outliers import flag_outliers
from tesorotools.utils.globals import DEBUG
from tesorotools.utils.matplotlib import (
    PLOT_CONFIG,
    format_annotation,
    load_fonts,
)

BARH_CONFIG: dict[str, Any] = PLOT_CONFIG["barh"]
AX_CONFIG: dict[str, Any] = PLOT_CONFIG["ax"]
FIG_CONFIG: dict[str, Any] = PLOT_CONFIG["figure"]

load_fonts()


class Column(Enum):
    VALUE = "value"
    AXIS = "axis"
    DEVIATION = "deviation"
    COLOR = "color"
    ALPHA = "alpha"


def _style_spines(
    ax: plt.Axes,
    decimals: int,
    units: str,
    *,
    color: str,
    linewidth: str,
):
    ax.grid(visible=True, axis="x")
    for spine in ax.spines.values():
        spine.set_color(color)
        spine.set_linewidth(linewidth)
    ax.xaxis.set_major_formatter(
        FuncFormatter(lambda x, _: format_annotation(x, decimals, units))
    )
    ax.tick_params(axis="both", which="major")
    for tick in ax.get_xticklines():
        tick.set_markeredgecolor(color)
    for tick in ax.get_yticklines():
        tick.set_markeredgecolor(color)


def _style_baseline(ax: plt.Axes, **baseline_config):
    color: str = baseline_config["color"]
    left_lim, right_lim = ax.get_xlim()
    ax.set_xlim(left=min(0, left_lim), right=max(0, right_lim))
    left_lim, right_lim = ax.get_xlim()
    if left_lim == 0:
        ax.spines["left"].set_edgecolor(color)
    elif right_lim == 0:
        ax.spines["right"].set_edgecolor(color)
    else:
        ax.axvline(x=0, **baseline_config)


def _collect_series(
    blocks: dict[str, Any] | None, series: dict[str, str] | None
) -> dict[str, str]:
    if series is None and blocks is None:
        raise ValueError("blocks and series cannot be both missing")
    if series is None and blocks is not None:
        return _collect_block_series(blocks)
    else:
        return series


def _collect_block_series(blocks: dict[str, Any]) -> dict[str, str]:
    series = {}
    for _, block_cfg in blocks.items():
        series = series | block_cfg["series"]
    return series


def _infer_colors(
    value_series: pd.Series, blocks: dict[str, Any] | None
) -> pd.Series:
    color_series: pd.Series = pd.Series(
        index=value_series.index, name=Column.COLOR.value, dtype=str
    )
    if blocks is not None:
        for idx, block_cfg in enumerate(blocks.values()):
            block_series: dict[str, str] = block_cfg["series"]
            color_series.loc[block_series.keys()] = f"C{idx}"
    else:
        color_series[value_series >= 0] = "C0"
        color_series[value_series < 0] = "C1"
    return color_series


def _highlight_series(
    alias: dict[str, str], value_series: pd.Series
) -> pd.Series:
    alpha_series: pd.Series = pd.Series(
        index=value_series.index, name=Column.ALPHA.value
    )
    alpha_series.loc[:] = 1
    high_series = [k for k, v in alias.items() if v.endswith("*")]
    alpha_series.loc[high_series] = BARH_CONFIG["highlight_factor"]
    return alpha_series


def _format_yaxis(
    alias: dict[str, str],
    axis_format: dict[str, Any],
    value_series: pd.Series,
    axis_series: pd.Series | None,
) -> pd.Series:
    # format y axis ticker labels
    renamer = {_: label.replace("*", "") for _, label in alias.items()}
    value_series = value_series.rename(renamer)
    if axis_format is not None:
        decimals: int = axis_format["decimals"]
        units: str = axis_format["units"]
        axis_series: pd.Series = axis_series.rename(renamer).apply(
            lambda x: format_annotation(x, decimals, units)
        )
        value_series = value_series.rename(
            lambda x: f"{x} ({axis_series.loc[x]})"
        )
    return value_series


def _annotate(
    fig: plt.Figure,
    ax: plt.Axes,
    bar_container: BarContainer,
    *,
    decimals: int,
    units: str,
):
    # annotate
    labels = ax.bar_label(
        container=bar_container,
        fmt=lambda x: format_annotation(x, decimals, units),
        padding=BARH_CONFIG["padding"],
    )

    # rescale
    fig.canvas.draw_idle()
    for label in labels:
        bbox = label.get_window_extent()
        bbox_data = bbox.transformed(ax.transData.inverted())
        ax.update_datalim(bbox_data.corners())
        ax.autoscale_view()


def _plot_barh_chart(
    out_file: Path,
    standard_dict: dict[Column, pd.Series | None],
    alias: dict[str, str],
    sorted: bool,
    format: dict,
    annot_format: dict,
    axis_format: dict | None = None,
    blocks: dict | None = None,
    **kwargs,
):
    # infer colors
    value_series: pd.Series = standard_dict[Column.VALUE]
    color_series: pd.Series = _infer_colors(value_series, blocks)
    alpha_series: pd.Series = _highlight_series(alias, value_series)

    # format y axis ticker labels
    axis_series = standard_dict[Column.AXIS]
    value_series = _format_yaxis(alias, axis_format, value_series, axis_series)
    color_series.index = value_series.index
    alpha_series.index = value_series.index

    data: pd.DataFrame = pd.concat(
        [value_series, color_series, alpha_series], axis=1
    )

    # sort if required
    if sorted:
        data = data.sort_values(by=Column.VALUE.value)

    # plot
    fig = plt.figure(**FIG_CONFIG)
    ax = fig.add_subplot()

    bar_container: BarContainer = ax.barh(
        y=data.index,
        width=data[Column.VALUE.value],
        color=data[Column.COLOR.value],
    )
    for bar, alpha in zip(bar_container, data[Column.ALPHA.value]):
        bar.set_alpha(alpha)

    _annotate(fig, ax, bar_container, **annot_format)
    _style_spines(ax, **format, **AX_CONFIG["spines"])
    _style_baseline(ax, **AX_CONFIG["baseline"])

    fig.savefig(out_file)


def _normalize_from_flash(
    flash: pd.DataFrame,
    axis: bool,
    *,
    date: str | pd.Timestamp | None,
    offset: str,
    difference: str,
    deviations: bool,
    units_bar: str,
    units_axis: str,
) -> dict[Column, pd.Series | None]:

    # format parameters
    date: pd.Timestamp = (
        flash.index.get_level_values(level=0).max()
        if date is None
        else pd.to_datetime(date)
    )
    offset: FloatingOffset = FloatingOffset(offset)
    difference: Difference = Difference(difference)

    # value column
    values_series: pd.Series = flash.loc[
        (date, offset.value, difference.value, Stat.VALUE.value),
        :,
    ].copy()
    values_series.name = Column.VALUE.value
    values_series = (
        values_series * 100 if difference is Difference.REL else values_series
    )
    values_series = (
        values_series * 100
        if (difference is Difference.ABS and units_bar == "p.b.")
        else values_series
    )

    # axis column
    if axis:
        axis_series: pd.Series = flash.loc[
            (
                date,
                FloatingOffset.NO.value,
                Difference.NO.value,
                Stat.VALUE.value,
            ),
            :,
        ].copy()
        axis_series = (
            axis_series * 100
            if (difference is Difference.ABS and units_axis == "p.b.")
            else axis_series
        )

        axis_series.name = Column.AXIS.value
    else:
        axis_series = None

    # deviations column
    if deviations:
        deviations_df: pd.DataFrame = flash.loc[
            (
                date,
                offset.value,
                difference.value,
                [Stat.VALUE.value, Stat.ROLL_AVG.value, Stat.ROLL_STD._value_],
            ),
            :,
        ].T.copy()
        deviations_df.columns = deviations_df.columns.get_level_values(level=-1)
        deviations_df.columns.name = None
        deviations_series: pd.Series = flag_outliers(deviations_df)
        deviations_series.name = Column.DEVIATION.value
    else:
        deviations_series = None

    return {
        Column.VALUE: values_series,
        Column.AXIS: axis_series,
        Column.DEVIATION: deviations_series,
    }


def plot_barh_charts_from_flash(
    out_path: Path, flash: pd.DataFrame, config_dicts: dict[str, dict]
):
    for name, config in config_dicts.items():
        blocks: dict[str, Any] = config.get("blocks", None)
        series: dict[str, str] | None = config.get("series", None)
        alias = _collect_series(blocks, series)
        trimmed_flash: pd.DataFrame = flash.loc[:, alias.keys()]
        flash_config: dict[str, Any] = config["flash"]
        axis_format: dict[str, Any] = config.get("axis_format", None)
        axis = axis_format is not None
        standard_dict: dict[Column, pd.Series | None] = _normalize_from_flash(
            trimmed_flash,
            axis,
            **flash_config,
            units_bar=config["format"]["units"],
            units_axis=config.get("axis_format", {"units": ""})["units"],
        )
        out_file = out_path / f"{name}.png"
        _plot_barh_chart(out_file, standard_dict, alias, **config)
