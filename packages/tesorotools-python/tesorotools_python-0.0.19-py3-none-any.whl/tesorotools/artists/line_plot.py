import datetime
import locale
from pathlib import Path
from typing import Any, Self

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter
from yaml.nodes import MappingNode

from tesorotools.utils.config import TemplateLoader

locale.setlocale(locale.LC_ALL, "")

from tesorotools.utils.globals import DEBUG
from tesorotools.utils.matplotlib import (
    PLOT_CONFIG,
    format_annotation,
    load_fonts,
)

load_fonts()

LINE_PLOT_CONFIG: dict[str, Any] = PLOT_CONFIG["line"]
AX_CONFIG: dict[str, Any] = PLOT_CONFIG["ax"]
FIG_CONFIG: dict[str, Any] = PLOT_CONFIG["figure"]


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
    ax.set_xlabel("")

    ax.tick_params(which="minor", size=0, width=0)
    ax.tick_params(axis="both", which="major")
    for tick in ax.get_xticklines():
        tick.set_markeredgecolor(color)
    for tick in ax.get_yticklines():
        tick.set_markeredgecolor(color)


def _style_baseline(ax: plt.Axes, reference: float = 0, **baseline_config):
    color: str = baseline_config["color"]
    bottom_lim, top_lim = ax.get_ylim()
    ax.set_ylim(bottom=min(reference, bottom_lim), top=max(reference, top_lim))
    bottom_lim, top_lim = ax.get_ylim()
    if bottom_lim == reference:
        ax.spines["bottom"].set_edgecolor(color)
    elif top_lim == reference:
        ax.spines["top"].set_edgecolor(color)
    else:
        ax.axhline(y=reference, **baseline_config)


def plot_line_chart(
    out_name: Path,
    data: pd.DataFrame,
    *,
    base_100: bool,
    annotate: bool,
    format: dict[str, Any],
    **kwargs,
):
    if base_100:
        data = data / data.iloc[0, :] * 100
    if format["units"] == "p.b.":
        data = data * 100
    fig = plt.figure(**FIG_CONFIG)
    ax = fig.add_subplot()
    data.plot(ax=ax)
    if annotate:
        pass

    reference = 100 if base_100 else 0
    _style_spines(ax, **format, **AX_CONFIG["spines"])
    _style_baseline(ax, reference, **AX_CONFIG["baseline"])
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, LINE_PLOT_CONFIG["legend_sep"]),
        ncol=(
            kwargs["legend"]["ncol"]
            if kwargs is not None and kwargs.get("legend", None) is not None
            else LINE_PLOT_CONFIG["ncol"]
        ),
    )

    fig.savefig(out_name)


def plot_line_charts(
    out_path: Path, data: pd.DataFrame, config_dicts: dict[str, Any]
):
    for name, config in config_dicts.items():
        start_date: pd.Timestamp = pd.to_datetime(config["start_date"])
        end_date_str: str | None = config["end_date"]
        end_date: pd.Timestamp = (
            data.index.max()
            if end_date_str is None
            else pd.to_datetime(end_date_str)
        )
        series: dict[str, str] = config["series"]
        trimmed_data: pd.DataFrame = data.loc[
            slice(start_date, end_date), series.keys()
        ]
        trimmed_data = trimmed_data.rename(columns=series)
        out_name: Path = out_path / f"{name}.png"
        plot_line_chart(out_name, trimmed_data, **config)


class Format:
    def __init__(self, units: str = "", decimals: int = 0):
        self.units = units
        self.decimals = decimals

    @classmethod
    def from_yaml(cls, loader: TemplateLoader, node: MappingNode) -> Self:
        loader.flatten_mapping(node)
        format_cfg: dict[str, Any] = loader.construct_mapping(node, deep=True)
        format_cfg.pop("id")
        return cls(**format_cfg)


class Legend:
    def __init__(self, ncol: int = 5, sep: float = -0.125):
        self.ncol = ncol
        self.sep = sep

    @classmethod
    def from_yaml(cls, loader: TemplateLoader, node: MappingNode) -> Self:
        legend_cfg: dict[str, Any] = loader.construct_mapping(node, deep=True)
        legend_cfg.pop("id")
        return cls(**legend_cfg)


# as more stuff is needed, seems wise to make a class
class LinePlot:
    def __init__(
        self,
        out_path: Path,
        data_path: Path,
        series: dict[str, str],
        scale: float = 1,
        start_date: datetime.datetime | None = None,
        end_date: datetime.datetime | None = None,
        base_100: bool = False,
        annotate: bool = False,
        baseline: bool = False,
        format: Format | None = None,
        legend: Legend | None = None,
    ) -> None:

        if out_path.suffix != ".png":
            raise ValueError(f"The out file {out_path} should be a .png file")
        self.out_path = out_path

        if data_path.suffix != ".feather":
            raise ValueError(
                f"The data file {data_path} must be a .feather file"
            )
        self.data = pd.read_feather(data_path)

        self.base_100 = base_100
        self.annotate = annotate  # unused for the moment
        self.format = format
        self.start_date = start_date
        self.end_date = end_date
        self.series = series
        self.legend = legend
        self.baseline = baseline
        self.scale = scale

    @classmethod
    def from_yaml(cls, loader: TemplateLoader, node: MappingNode) -> Self:
        line_plot_cfg: dict[str, Any] = loader.construct_mapping(
            node, deep=True
        )
        line_plot_cfg.pop("id")
        line_plot_cfg["out_path"] = Path(line_plot_cfg["out_path"])
        line_plot_cfg["data_path"] = Path(line_plot_cfg["data_path"])
        return cls(**line_plot_cfg)

    def plot(self) -> plt.Axes:
        start_date: pd.Timestamp = (
            self.data.index.min()
            if self.start_date is None
            else pd.to_datetime(self.start_date)
        )

        end_date: pd.Timestamp = (
            self.data.index.max()
            if self.end_date is None
            else pd.to_datetime(self.end_date)
        )

        plot_data: pd.DataFrame = self.data.loc[
            slice(start_date, end_date), self.series.keys()
        ]
        plot_data = plot_data.rename(columns=self.series)

        plot_data = plot_data * self.scale

        if self.base_100:  # maybe more flexible in the future
            plot_data = plot_data / plot_data.iloc[0, :] * 100

        fig = plt.figure(**FIG_CONFIG)
        ax = fig.add_subplot()
        plot_data.plot(ax=ax)

        if self.annotate:  # not implemented yet
            pass

        _style_spines(  # maybe make this function accept a Format object
            ax,
            decimals=self.format.decimals,
            units=self.format.units,
            **AX_CONFIG["spines"],
        )
        if self.baseline:
            reference = 100 if self.base_100 else 0
            _style_baseline(ax, reference, **AX_CONFIG["baseline"])

        if self.legend is not None:
            ax.legend(
                loc="upper center",
                bbox_to_anchor=(0.5, LINE_PLOT_CONFIG["legend_sep"]),
                ncol=self.legend.ncol,
            )
        else:
            ax.legend().set_visible(False)

        fig.savefig(self.out_path)
        return ax
