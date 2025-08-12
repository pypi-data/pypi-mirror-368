"""
load data
"""

import random

import pandas as pd
from sklearn.datasets import make_classification


def make_data(n_samples=10000, n_features=12):
    """
    :param n_samples: number of samples
    :param n_features: number of features
    :return: dataframe with training data
    """
    X, y = make_classification(n_samples=n_samples, n_features=n_features)
    df = pd.DataFrame(X, y)
    df = df.rename(columns=lambda x: "feature_" + str(x))
    df = df.reset_index().rename(columns={"index": "label"})
    return df


def make_data_extended(n_samples=10_000, n_features=10, missing_data=False, bins=False):
    """create training data"""
    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=int(n_features / 2),
        n_classes=2,
        weights=([0.9, 0.1]),
    )
    df = pd.DataFrame(X, y)
    df = df.rename(columns=lambda x: "feature_" + str(x))
    df = df.reset_index().rename(columns={"index": "label"})
    if bins:
        columns = list(df.columns)
        columns.remove("label")
        cols_to_process = random.sample(columns, round(n_features / 3))
        for i in cols_to_process:
            df[i] = pd.qcut(df[i], q=3, labels=["a", "b", "c"], duplicates="drop")
    if missing_data:
        for i in df.columns[1:]:
            # reassign w/ sample results in nan's due to auto-alignment
            df[i] = df[i].sample(frac=random.uniform(0.9, 1))
    return df
