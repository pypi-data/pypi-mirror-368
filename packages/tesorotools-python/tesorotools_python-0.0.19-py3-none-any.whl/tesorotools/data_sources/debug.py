import numpy as np
import pandas as pd

from tesorotools.utils.config import read_config
from tesorotools.utils.globals import DEBUG, EXAMPLES

# just mocking
CATALOG: dict[str, str] = read_config(EXAMPLES / "data.yaml")["debug"]


def get_series(start: str, end: str, series: list[str]) -> pd.DataFrame:
    # series is a list of agnostic ids
    specific_ids = []
    for agnostic_id in series:
        specific_id: str | None = CATALOG.get(agnostic_id, None)
        if specific_id is None:
            raise KeyError(f"{agnostic_id} not found in debug configuration")
        specific_ids.append(specific_id)

    index: pd.DatetimeIndex = pd.date_range(start=start, end=end).sort_values()
    df: pd.DataFrame = pd.DataFrame(
        data=np.random.randn(len(index), len(series)),
        index=index,
        columns=series,
    )
    return df
