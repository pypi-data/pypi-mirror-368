import pandas as pd

from .offsets import Stat


def flag_outliers(data: pd.DataFrame) -> pd.Series:
    return (data[Stat.VALUE.value] - data[Stat.ROLL_AVG.value]) / data[
        Stat.ROLL_STD.value
    ]


def flag_outliers_with_limit(data: pd.DataFrame, limit: float) -> pd.Series:
    return (data[Stat.VALUE.value] - data[Stat.ROLL_AVG.value]) / data[
        Stat.ROLL_STD.value
    ] > limit
