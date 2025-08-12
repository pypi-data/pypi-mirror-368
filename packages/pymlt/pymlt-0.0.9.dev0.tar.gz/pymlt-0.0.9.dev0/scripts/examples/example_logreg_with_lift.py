"""
example file
"""

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


def get_model_lift(y: np.ndarray, y_proba: np.ndarray, p=0.1) -> float:
    """
    takes y and y_proba and returns lift at p%
    """
    df = pd.DataFrame({"y": y, "y_proba": y_proba})
    df = df.sort_values(by="y_proba", ascending=False)
    n_true = df.y.sum()
    n_true_p = df.head(round(p * len(df))).y.sum()
    gain = n_true_p / n_true
    lift = gain / p
    return lift


def get_model_lift_table(y: np.ndarray, y_proba: np.ndarray) -> pd.DataFrame:
    """
    takes y and y_proba and returns df with model lift
    """
    df = pd.DataFrame({"y": y, "y_proba": y_proba})
    df = df.sort_values(by="y_proba", ascending=False)
    n_true = df.y.sum()
    table_p, table_g, table_l = [], [], []
    for i in range(1, 11, 1):
        i = i / 10
        n_true_p = df.head(round(i * len(df))).y.sum()
        gain = n_true_p / n_true
        lift = gain / i
        table_p.append(i)
        table_g.append(gain)
        table_l.append(lift)
    table = pd.DataFrame({"p": table_p, "gain": table_g, "lift": table_l})
    return table


X, y = make_classification(n_samples=5_000, n_informative=2, weights=[0.95])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

clf = LogisticRegression(max_iter=3_000).fit(X_train, y_train)

print(clf.predict_proba(X_test)[:, 1])

print(get_model_lift_table(y_test, clf.predict_proba(X_test)[:, 1]))
