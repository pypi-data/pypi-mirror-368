import pandas as pd


def difference(
    target: float | pd.Series, reference: float | pd.Series
) -> float | pd.Series:
    return target - reference


def inverse(target: float | pd.Series) -> float | pd.Series:
    return 1 / target
