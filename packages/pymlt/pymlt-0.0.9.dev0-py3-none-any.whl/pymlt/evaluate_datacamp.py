import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix


def get_model_lift(y: np.ndarray, y_proba: np.ndarray, p=0.1) -> float:
    """takes y and y_proba and returns lift at p%"""
    df = pd.DataFrame({"y": y, "y_proba": y_proba})
    df = df.sort_values(by="y_proba", ascending=False)
    n_true = df.y.sum()
    n_true_p = df.head(round(p * len(df))).y.sum()
    gain = n_true_p / n_true
    lift = gain / p
    return lift


def get_model_lift_table(y: np.ndarray, y_proba: np.ndarray) -> pd.DataFrame:
    """takes y and y_proba and returns df with model lift"""
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


def get_best_threshold(
    y: np.ndarray, y_proba: np.ndarray, cost=5, gain=50
) -> pd.DataFrame:
    """
    takes y, y_proba, cost (e.g. the cost calling a customer) and gain (i.e.
    the monetary gains of a conversion) and returns evaluation metrics per threshold
    and indicating the max profit threshold; function is used in create_model to
    evaluate model performance on test set as a proxy for final campaign
    """
    df = pd.DataFrame({"y": y, "y_proba": y_proba})
    # if with highest y_proba no y=True is captured, cpo cannot be calculated
    y_proba_max = df.query("y==True").y_proba.max() - 0.01
    df_results = pd.DataFrame(np.arange(0, y_proba_max, 0.01), columns=["threshold"])
    for i in range(len(df_results)):
        t = df_results.loc[i, "threshold"].round(2)
        y_pred = (y_proba > t).astype("int")
        cm = confusion_matrix(y, y_pred)
        df_results.loc[i, "accuracy"] = (cm[0, 0] + cm[1, 1]) / cm.sum()
        df_results.loc[i, "precision"] = cm[1, 1] / (cm[1, 1] + cm[0, 1])
        df_results.loc[i, "recall"] = cm[1, 1] / (cm[1, 1] + cm[1, 0])
        df_results.loc[i, "n_in_campaign"] = cm[:, 1].sum()
        df_results.loc[i, "n_in_campaign_perc"] = round(
            df_results.loc[i, "n_in_campaign"] / len(df), 2
        )
        df_results.loc[i, "n_conv"] = cm[1, 1]
        df_results.loc[i, "n_conv_missing"] = cm[1, 0]
        df_results.loc[i, "profit"] = (cm[1, 1].sum() * gain) - (cm[:, 1].sum() * cost)
        df_results.loc[i, "p_con_nothreshold"] = y.mean()
        df_results.loc[i, "p_con"] = (cm[1, 1] / cm[:, 1].sum()).round(2)
        df_results.loc[i, "cpo"] = (cm[:, 1].sum() * cost) / cm[1, 1]
        df_results.loc[i, "roi"] = gain / df_results.loc[i, "cpo"]
    df_results["pr_rel"] = (df_results["profit"] / df_results["profit"].max()).astype(
        "float"
    )
    df_results["pr_max"] = (
        (df_results["profit"] == df_results["profit"].max())
        .astype("int")
        .replace(1, "<<<")
    )
    # profit below 0 is not relevant, usually t = 0.00 will result in negative profit
    df_results = df_results.query("profit > 0")
    df_results = df_results.round(3).head(30)
    return df_results
