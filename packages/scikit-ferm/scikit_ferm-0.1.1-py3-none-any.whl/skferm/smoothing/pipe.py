from typing import Literal

import pandas as pd

from skferm.smoothing.moving_average import exponential_moving_average, rolling_average


def smooth_group(df, x: str, y: str, method: str, **kwargs):
    methods = {
        "rolling": rolling_average,
        "ema": exponential_moving_average,
    }
    if method not in methods:
        raise ValueError(f"Unknown smoothing method: {method}. Available methods: {list(methods.keys())}")
    return methods[method](df, x=x, y=y, **kwargs)


def smooth(
    df: pd.DataFrame, x: str, y: str, groupby_col: str, method: Literal["rolling", "ema"] = "rolling", **kwargs
) -> pd.DataFrame:
    """
    Applies smoothing to each unique fermentation curve (grouped by sample_id).

    Parameters:
    - df: Pandas DataFrame with columns ['time', 'pH', 'sample_id'].
    - x: Column name for the x-axis values.
    - y: Column name for the y-axis values.
    - groupby_col: Column name to group by (e.g., 'sample_id').
    - method: smoothing method, one of "rolling", "ema", "savgol", "lowess"
    - kwargs: method-specific arguments (e.g., window=5, span=10, frac=0.1)

    Returns:
    - DataFrame with an added `{y}_smooth` column
    """

    grouped = [
        smooth_group(group, x, y, method=method, **kwargs) for _, group in df.groupby(groupby_col, group_keys=False)
    ]
    return pd.concat(grouped, ignore_index=True)
