"""
example file
"""

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=5_000, n_informative=2, weights=[0.95])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

rf = RandomForestClassifier().fit(X_train, y_train)

df_test = pd.DataFrame(X_test).reset_index().drop(columns=["index"])
df_test["label"] = pd.DataFrame(y_test).reset_index().drop(columns=["index"])
df_test["pred_proba"] = pd.DataFrame(rf.predict_proba(X_test)[:, 1])


def get_best_threshold(df: pd.DataFrame, cost: int = 5, gain: int = 25) -> float:
    """
    calculates threshold based on model performance and cost/gain of marketing
    """

    results = pd.DataFrame(
        np.arange(0, df["pred_proba"].max() - 0.01, 0.01), columns=["threshold"]
    )

    for i in range(len(results)):
        t = round(results.loc[i, "threshold"], 2)
        pred_based_on_threshold = np.where(df["pred_proba"] >= t, 1, 0)
        cm = confusion_matrix(df["label"], pred_based_on_threshold)
        results.loc[i, "accuracy"] = (cm[0, 0] + cm[1, 1]) / cm.sum()
        results.loc[i, "n_in_campaign"] = cm[:, 1].sum()
        results.loc[i, "n_conv"] = cm[1, 1]
        results.loc[i, "n_conv_missing"] = cm[1, 0]
        results.loc[i, "profit"] = (cm[1, 1].sum() * gain) - (cm[:, 1].sum() * cost)
        results.loc[i, "p_con_nothreshold"] = df["label"].mean()
        results.loc[i, "p_con"] = round(cm[1, 1] / cm[:, 1].sum(), 2)
        results.loc[i, "cpo"] = (cm[:, 1].sum() * cost) / cm[1, 1]
        results.loc[i, "roi"] = gain / results.loc[i, "cpo"]

    t = pd.DataFrame(results[results["profit"] == results["profit"].max()]["threshold"])
    t = round(t["threshold"].min(), 2)
    print(results[results["threshold"] == t].T)

    return t


print("best threshold: ", get_best_threshold(df_test, 5, 25))
