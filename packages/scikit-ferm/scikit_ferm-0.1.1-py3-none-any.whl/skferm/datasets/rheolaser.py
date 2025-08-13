from importlib.resources import files
from typing import Optional

import pandas as pd


def clean_rheolaser(df: pd.DataFrame, cutoff: Optional[int] = None) -> pd.DataFrame:
    """
    Function which transforms the raw rheolaser format to a nice long format.
    """
    df = df.dropna(axis=1, how="all")

    # grab unique ids
    ids = [s.replace(" - Elasticity Index", "") for s in df.columns.tolist()[0::2]]

    # transform to long format
    seperate_frames = []
    n_samples = len(ids)

    for i in range(0, n_samples):
        sub_df = df.iloc[:, i * 2 : i * 2 + 2].copy()
        sub_df.columns = ["time", "elasticity_index"]
        sub_df = sub_df.assign(sample_id=ids[i]).dropna()
        seperate_frames.append(sub_df)

    result_df = (
        pd.concat(seperate_frames, axis=0)
        .reset_index(drop=True)
        .assign(time=lambda d: d["time"] / 60)
        .assign(elasticity_index=lambda d: d["elasticity_index"] * 1000)
        .loc[:, ["sample_id", "time", "elasticity_index"]]
        .sort_values(["sample_id", "time"])
        .reset_index(drop=True)
    )

    if cutoff:
        result_df = result_df.loc[lambda d: d["time"] <= cutoff]

    return result_df


def load_rheolaser_data(clean: bool = True, cutoff: Optional[int] = None) -> pd.DataFrame:
    """
    Load the Rheolaser dataset from the package resources. This is the exact
    format you get from a Rheolaser machine. Use `clean_rheolaser` to transform it
    into a long format DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing the Rheolaser dataset.
    """
    rheolaser_path = files("skferm.data").joinpath("rheolaser_export.csv.gz")
    with rheolaser_path.open("rb") as f:
        df = pd.read_csv(f, compression="gzip")

    if clean:
        df = clean_rheolaser(df, cutoff=cutoff)

    return df
