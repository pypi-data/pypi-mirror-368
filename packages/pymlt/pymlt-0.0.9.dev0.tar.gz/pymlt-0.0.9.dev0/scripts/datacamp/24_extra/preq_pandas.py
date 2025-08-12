#!/usr/local/bin/python3


import pandas as pd
from pydataset import data

df = data("diamonds")


def df_sample(df, n=200):
    """take a sample of n from df"""
    return df.sample(n, replace=False)


df = (
    df.drop_duplicates()
    .fillna(0)
    .replace({"color": {"D": "A", "E": "B"}})
    .loc[:40000,]
    .loc[lambda df: df["price"] > 500]
    .query('price > 4000 & cut == "Ideal"')
    .pipe(df_sample, n=4000)
    .sample(frac=0.25)
    .sort_values("x", ascending=False)
    .head(500)
    .tail(500)
    .rename(columns={"color": "colour"})
    .assign(price_per_x=df["price"] / df["x"])
    .groupby("colour")
    .price_per_x.agg(["count", "mean", "std", "min", "max", "var"])
    .round()
    .astype("int")
    .reset_index()
    .rename(columns={"index": "colour"})
    .assign(mean_plus_2std=lambda df: df["mean"] + (2 * df["std"]))
    .assign(
        type=lambda df: pd.cut(
            df["mean_plus_2std"], bins=[0, 2300, 4000], labels=["a", "b"]
        )
    )
    .add_prefix("results_")
    .rename(columns={"results_colour": "colour"})
    .select_dtypes(include=["number", "object", "category", "datetime"])
)

print(df)
