"""
example on how to process dates
"""

from datetime import date

import numpy as np
import pandas as pd


def generate_data(n: int = 10) -> pd.DataFrame:
    """
    generates dataframe with dates
    """
    return pd.DataFrame(
        {
            "start_date": np.random.choice(["2022-04-01", "2023-03-01"], n),
            "contract_duration": np.random.randint(1, 12, n),
        }
    )


def get_date_features(df: pd.DataFrame, col: str, fmt: str = "%Y-%m-%d"):
    """
    generates date features
    """

    # convert to date
    df[col] = pd.to_datetime(df[col], format=fmt)

    # generate date features -- https://strftime.org/
    df[f"{col}_day"] = df[col].dt.strftime("%d")
    df[f"{col}_month"] = df[col].dt.strftime("%m")
    df[f"{col}_year"] = df[col].dt.strftime("%Y")
    df[f"{col}_weekday"] = df[col].dt.strftime("%a")

    # set ref
    df["ref"] = pd.to_datetime(date.today(), format=fmt)
    df["ref"] = pd.to_datetime("2022-12-01", format=fmt)

    # diff with reference
    df[f"{col}_after_ref"] = df[col] > df["ref"]
    df["diff_days"] = (df[col] - df["ref"]) / np.timedelta64(1, "D")
    df["diff_weeks"] = (df[col] - df["ref"]) / np.timedelta64(1, "W")
    df["diff_months"] = (df[col] - df["ref"]) / np.timedelta64(1, "M")
    df["diff_years"] = (df[col] - df["ref"]) / np.timedelta64(1, "Y")

    # add days or weeks
    df[f"{col}_plus_n_day"] = df[col] + pd.DateOffset(1)
    df[f"{col}_plus_n_week"] = df[col] + pd.DateOffset(7)
    df[f"{col}_plus_n_month"] = df[col] + pd.DateOffset(months=1)

    # add days or weeks from another column in df
    df[f"{col}_plus_n_month"] = (
        (df["start_date"].dt.to_period("M")) + df["contract_duration"]
    ).dt.strftime("%Y-%m")

    return df.round(2)


df = generate_data(10)
df = get_date_features(df, col="start_date")
print(df.transpose())
