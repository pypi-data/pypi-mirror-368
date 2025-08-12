"""
example on how to organize data checks in your project
"""

import time

import numpy as np
import pandas as pd


def generate_data(n: int = 10) -> pd.DataFrame:
    """
    generates test data for checks and pytests
    """
    return pd.DataFrame(
        {
            "column1": np.random.randint(1, 12, n),
            "column2": np.random.uniform(500, 3500, n),
            "column3": np.random.choice(["value_1", "value_2"], n),
        }
    )


def check_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    data checks on dataframe provided
    """

    assert type(df) == pd.DataFrame, "df is not a dataframe"
    assert len(df), "df is empty"
    assert df.column1.dtype == "int64"
    assert df.column2.dtype == "float64"
    assert df.column3.dtype == "object"
    assert df.column1.between(0, 12).all(), "column1 outside boundaries"
    assert df.column1.notnull().all(), "column1 contains nulls"
    assert df.column1.gt(0).all(), "column1 not greater than 0"
    assert df.column2.mean() >= 500, "column2 mean below threshold"
    assert df.column3.notnull().all(), "column3 contains nulls"
    assert df.column3.isin(["value_1", "value_2"]).all(), "invalid category"

    print("all checks passed")

    return df


def cta(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(cta=50.5)


def main():
    df = generate_data(5)
    df = df.pipe(check_data).pipe(cta)
    print(df)


if __name__ == "__main__":
    # check input data
    check = False
    while not check:
        print("input not updated yet")
        time.sleep(3)
        check = False  # check again
        if time.perf_counter() > 30:  # check if time out
            raise RuntimeError("time out")

    main()
