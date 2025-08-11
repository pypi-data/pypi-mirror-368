from collections.abc import Callable
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np
import pandas as pd

# stats and stat functions
type StatFunction = Callable[[pd.Series], np.float64]
type StatRollingFunction = Callable[..., float]


class Stat(Enum):
    VALUE = "value"
    ROLL_AVG = "roll_avg"
    ROLL_STD = "roll_std"

    @property
    def stat_function(self) -> StatFunction:
        match self:
            case self.VALUE:
                return lambda x: x.iloc[-1]
            case self.ROLL_AVG:
                return lambda x: np.mean(x)
            case self.ROLL_STD:
                return lambda x: np.std(x, ddof=0)

    @property
    def update_function(self) -> StatRollingFunction:
        match self:
            case self.VALUE:
                return lambda **kwargs: kwargs["newest_point"]
            case self.ROLL_AVG:
                return lambda **kwargs: _update_rolling_avg(**kwargs)
            case self.ROLL_STD:
                return lambda **kwargs: _update_rolling_std(**kwargs)


# offsets and offset functions
type OffsetFunction = Callable[[pd.DatetimeIndex], pd.DatetimeIndex]


def _fixed_date_offset_function(reference_date: datetime) -> OffsetFunction:
    return lambda dates: pd.DatetimeIndex([reference_date] * len(dates))


class FloatingOffset(Enum):
    NO = "no"
    BDAY = "bday"
    FTD = "ftd"
    MTD = "mtd"
    YTD = "ytd"

    @property
    def offset_function(self) -> OffsetFunction:
        match self:
            case self.BDAY:
                return lambda dates: dates - pd.tseries.offsets.BDay(1)
            case self.FTD:
                return lambda dates: dates - pd.tseries.offsets.Week(weekday=4)
            case self.MTD:
                return (
                    lambda dates: dates
                    - pd.offsets.MonthBegin()
                    - pd.tseries.offsets.BDay(1)
                )
            case self.YTD:
                return (
                    lambda dates: dates
                    - pd.offsets.YearBegin()
                    - pd.tseries.offsets.BDay(1)
                )


# differences and difference functions
type DifferenceFunction = Callable[[pd.Series, pd.Series], pd.Series]


class Difference(Enum):
    NO = "no"
    ABS = "absolute"
    REL = "relative"

    @property
    def difference_function(self) -> DifferenceFunction:
        match self:
            case self.ABS:
                return lambda original, offset: original - offset
            case self.REL:
                return lambda original, offset: (original - offset) / offset


def process_raw_data(raw_data: pd.DataFrame, **config) -> pd.DataFrame:
    # preprocess index
    dates: pd.DatetimeIndex = pd.to_datetime(raw_data.index)
    raw_data.index = dates
    raw_data = raw_data.sort_index()

    # parse config and compute common values
    window: int = min(config["window"], len(raw_data.index))
    offsets_dict = _parse_offsets(config["offsets"], dates)
    differences_dict = _parse_differences(config["differences"])
    stats_dict = _parse_stats(config["stats"])

    names = ["date", "offset", "difference_type"]
    columns = stats_dict.keys()

    offset_df, raw_df = _result_templates(
        dates,
        offsets_dict.keys(),
        differences_dict.keys(),
        names,
        columns,
        columns_name="stat",
    )

    # computing enriched data
    enriched_data: pd.DataFrame = raw_data.apply(
        lambda x: _process_raw_data(
            x,
            offsets_dict,
            differences_dict,
            stats_dict,
            raw_df=raw_df,
            offset_df=offset_df,
            window=window,
        )
    )
    return enriched_data


def _parse_offsets(
    offsets_cfg: list[str | datetime], dates: pd.DatetimeIndex
) -> dict[str, pd.DatetimeIndex]:
    offsets: dict[str | datetime, OffsetFunction] = {}
    for offset_str in offsets_cfg:
        if offset_str is FloatingOffset.NO:
            continue
        if offset_str in FloatingOffset:
            offset_enum = FloatingOffset(offset_str)
            offsets[offset_str] = offset_enum.offset_function
        else:
            offsets[str(offset_str)] = _fixed_date_offset_function(offset_str)
    offsets_dict: dict[str, pd.DatetimeIndex] = {
        offset_str: offset_function(dates)
        for offset_str, offset_function in offsets.items()
    }
    return offsets_dict


def _parse_differences(
    differences_cfg: list[str],
) -> dict[str, DifferenceFunction]:
    differences: dict[str, DifferenceFunction] = {
        diff_str: Difference(diff_str).difference_function
        for diff_str in differences_cfg
        if diff_str is not Difference.NO
    }
    return differences


def _parse_stats(
    stats_cfg: list[str], update: bool = False
) -> dict[str, StatFunction]:
    if update:
        stats: dict[str, StatFunction] = {
            stat_str: Stat(stat_str).update_function for stat_str in stats_cfg
        }
        stats[Stat.VALUE.value] = Stat.VALUE.update_function
    else:
        stats: dict[str, StatFunction] = {
            stat_str: Stat(stat_str).stat_function for stat_str in stats_cfg
        }
        stats[Stat.VALUE.value] = Stat.VALUE.stat_function
    return stats


def _result_templates(
    dates: pd.DatetimeIndex,
    offsets: list[str],
    differences: list[str],
    names: list[str],
    columns: list[str],
    columns_name: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:

    offset_idx: pd.MultiIndex = pd.MultiIndex.from_product(
        [
            dates,
            offsets,
            differences,
        ],
        names=names,
    )
    offset_df: pd.DataFrame = pd.DataFrame(
        index=offset_idx,
        columns=columns,
    )
    offset_df.columns.name = columns_name

    raw_idx: pd.MultiIndex = pd.MultiIndex.from_product(
        [
            dates,
            [FloatingOffset.NO.value],
            [Difference.NO.value],
        ],
        names=names,
    )

    raw_df: pd.DataFrame = pd.DataFrame(
        index=raw_idx,
        columns=columns,
    )
    raw_df.columns.name = columns_name

    return offset_df, raw_df


def _process_raw_data(
    column: pd.Series,
    offsets_dict: dict[str, pd.DatetimeIndex],
    differences_dict: dict[str, DifferenceFunction],
    stats_dict: dict[str, StatFunction],
    *,
    raw_df: pd.DataFrame,
    offset_df: pd.DataFrame,
    window: int,
) -> pd.Series:

    stat_functions = list(stats_dict.values())

    # for every non trivial offset and difference apply all the stats
    for offset_str, offset_idx in offsets_dict.items():
        for diff_str, diff_func in differences_dict.items():
            offset_data = column.reindex(offset_idx)
            offset_data.index = column.index
            diff_data = diff_func(column, offset_data)
            stat_data: pd.DataFrame = diff_data.rolling(
                window=window, min_periods=0
            ).agg(stat_functions)
            offset_df.loc[(slice(None), offset_str, diff_str), :] = (
                stat_data.values
            )
    offset_series: pd.Series = offset_df.stack()

    # apply the stats to the original data
    stat_data: pd.DataFrame = column.rolling(window=window, min_periods=0).agg(
        stat_functions
    )
    raw_df.loc[(slice(None)), :] = stat_data.values
    raw_series: pd.Series = raw_df.stack()

    result = pd.concat([offset_series, raw_series])
    result = result.apply(pd.to_numeric, errors="coerce")
    return result


def trim(full_data: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    indexer = (
        slice(None),
        FloatingOffset.NO.value,
        Difference.NO.value,
        Stat.VALUE.value,
    )
    if isinstance(full_data, pd.DataFrame):
        trimmed_data: pd.DataFrame = full_data.loc[indexer, :]
    else:
        trimmed_data: pd.Series = full_data.loc[indexer]
    trimmed_data.index = trimmed_data.index.get_level_values(level=0)
    return trimmed_data


def add_rows(
    old_full_df: pd.DataFrame,
    new_trimmed_df: pd.DataFrame,
    offsets_cfg: dict[str, Any],
):
    ## sanity check (raise if failed)
    # same columns
    # simple index
    # datetime index
    # sorted index
    # dates not in the old df

    dates: pd.DatetimeIndex = old_full_df.index.get_level_values(
        level=0
    ).unique()
    window: int = min(
        offsets_cfg["window"],
        len(dates) + len(new_trimmed_df.index),
    )
    offsets_dict = _parse_offsets(offsets_cfg["offsets"], new_trimmed_df.index)
    differences_dict = _parse_differences(offsets_cfg["differences"])
    stats_dict = _parse_stats(offsets_cfg["stats"], update=True)
    names = ["date", "offset", "difference_type"]
    columns = stats_dict.keys()
    offset_df, raw_df = _result_templates(
        new_trimmed_df.index,
        offsets_dict.keys(),
        differences_dict.keys(),
        names,
        columns,
        columns_name="stat",
    )
    updated_data: pd.DataFrame = new_trimmed_df.apply(
        lambda x: _process_new_data(
            x,
            old_full_df.loc[:, x.name],
            offsets_dict,
            differences_dict,
            stats_dict,
            raw_df=raw_df,
            offset_df=offset_df,
            window=window,
        )
    )
    result = pd.concat([old_full_df, updated_data])
    return result


def _process_new_data(
    new_trimmed_column: pd.Series,
    old_full_column: pd.Series,
    offsets_dict: dict[str, pd.DatetimeIndex],
    differences_dict: dict[str, DifferenceFunction],
    stats_dict: dict[str, StatFunction],
    *,
    raw_df: pd.DataFrame,
    offset_df: pd.DataFrame,
    window: int,
) -> pd.Series:

    old_trimmed_column: pd.Series = trim(old_full_column)
    fused_trimmed_column: pd.Series = pd.concat(
        [old_trimmed_column, new_trimmed_column]
    )

    # for every non trivial offset and difference apply all the stats
    for offset_str, offset_idx in offsets_dict.items():
        for diff_str, diff_func in differences_dict.items():
            offset_data = fused_trimmed_column.reindex(offset_idx)
            offset_data.index = new_trimmed_column.index
            diff_data = diff_func(new_trimmed_column, offset_data)
            old_diff_stats: pd.Series = old_full_column.loc[
                (slice(None), offset_str, diff_str)
            ]
            stat_data: pd.DataFrame = _rolling_update(
                window, diff_data, old_diff_stats, stats_dict
            )
            offset_df.loc[(stat_data.index.values, offset_str, diff_str), :] = (
                stat_data.values
            )
    offset_series: pd.Series = offset_df.stack()

    # apply the stats to the original data
    old_stats: pd.Series = old_full_column.loc[
        (slice(None), FloatingOffset.NO.value, Difference.NO.value)
    ]
    stat_data: pd.DataFrame = _rolling_update(
        window, new_trimmed_column, old_stats, stats_dict
    )
    raw_df.loc[(slice(None)), :] = stat_data.values
    raw_series: pd.Series = raw_df.stack()

    result = pd.concat([offset_series, raw_series])
    result = result.apply(pd.to_numeric, errors="coerce")
    return result


def _rolling_update(
    window: int,
    new_trimmed_data: pd.Series,
    old_full_data: pd.Series,
    stats_dict: dict[str, StatRollingFunction],
):
    result_df: pd.DataFrame = old_full_data.unstack(level=-1)
    fused_values = pd.concat(
        [result_df.loc[:, Stat.VALUE.value], new_trimmed_data]
    )
    result_df = result_df.reindex(fused_values.index)
    for index, value in new_trimmed_data.items():
        current_position = fused_values.index.get_loc(index)
        previous_position = max(current_position - window, 0)
        previous_value = fused_values.iloc[previous_position]
        actual_window = min(window, current_position + 1)
        expanding = actual_window < window
        for f_name, function in stats_dict.items():
            result_df.loc[index, f_name] = function(
                window=actual_window,
                expanding=expanding,
                old_stat=result_df.iloc[current_position - 1][f_name],
                oldest_point=previous_value,
                newest_point=value,
                other_stats=result_df.iloc[current_position - 1],
            )
    return result_df.loc[new_trimmed_data.index, :]


def _update_rolling_std(
    window: int,
    expanding: bool,
    old_stat: float,
    oldest_point: float,
    newest_point: float,
    other_stats: pd.Series,
    **_,
) -> float:
    old_rolling_mean: float = other_stats[Stat.ROLL_AVG.value]
    if expanding:
        # https://math.stackexchange.com/questions/374881/recursive-formula-for-variance
        new_rolling_var = (
            old_stat**2
            + (1 / (window + 1)) * (old_rolling_mean - newest_point) ** 2
        ) * (window / (window + 1))
    else:
        # https://jonisalonen.com/2014/efficient-and-accurate-rolling-standard-deviation/

        delta = newest_point - oldest_point
        new_rolling_mean = old_rolling_mean + (delta / window)
        new_rolling_var = old_stat**2 + (delta / window) * (
            newest_point - new_rolling_mean + oldest_point - old_rolling_mean
        )
    new_rolling_var = max(new_rolling_var, 0)  # avoid complex numbers
    return new_rolling_var**0.5


def _update_rolling_avg(
    window: int,
    expanding: bool,
    old_stat: float,
    oldest_point: float,
    newest_point: float,
    **_,
) -> float:
    if expanding:
        return ((window - 1) * old_stat + newest_point) / window
    else:
        return old_stat + (newest_point - oldest_point) / window
