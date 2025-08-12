"""
This module contains a collection of functions to evaluate a fitted model in grafana.

Functions included:
- get_grafana_metrics_config
- get_grafana_metrics_df_shape
- get_grafana_metrics_model_performance
"""

import numpy as np
import pandas as pd


def get_grafana_metrics_config(grafana_metrics, config):
    grafana_metrics.update({"model type": config.training.estimator})
    grafana_metrics.update({"run name": config.my_run.name})
    grafana_metrics.update({"test set percentage": config.data.test_set.percentage})
    grafana_metrics.update({"nr_of_cv_folds": config.training.nr_of_cv_folds})
    grafana_metrics.update(
        {"hyperopt nr of trials": config.training.hyperopt.max_nr_of_trials}
    )
    grafana_metrics.update({"optimization metric": config.metrics.optimization_metric})
    return grafana_metrics


def get_grafana_metrics_df_shape(grafana_metrics, y, df):
    grafana_metrics.update({"number of true y": sum(y)})
    grafana_metrics.update({"percentage of true y": (sum(y) / len(y)) * 100})
    grafana_metrics.update({"length full df": len(y)})
    grafana_metrics.update({"number of features": len(df.columns) - 1})
    return grafana_metrics


def get_grafana_metrics_model_performance(
    grafana_metrics, model_dict, X_test_unprepped, y_test
):
    def _calculate_aggregations(y, y_prob, n_bins=100):
        """
        Calculated various model performance metrics to be stored
        :param y: target variable (1/0) for the trained model
        :param y_prob: model evaluation of target variable on the test set
        :param n_bins: Number of bins into which the probabilities are divided. Default = 100
        """
        df = pd.DataFrame({"y": y, "y_prob": y_prob})
        df = df.sort_values("y_prob", ascending=False)
        df["group"] = (np.arange(0, len(df), 1) / len(df) * n_bins).astype(int) + 1
        df["count"] = 1
        aggs = df.groupby("group").agg({"y": [np.mean, sum], "count": [sum]})
        aggs.columns = ["pos_rate", "n_pos", "count"]
        aggs["avg_pos_rate"] = df["y"].mean()
        aggs["pos_tot"] = df["y"].sum()
        aggs["non_cum_lift"] = aggs["pos_rate"] / aggs["avg_pos_rate"]
        aggs["cum_n_pos"] = aggs["n_pos"].cumsum()
        aggs["cum_count"] = aggs["count"].cumsum()
        aggs["cum_lift"] = aggs["cum_n_pos"] / aggs["cum_count"] / aggs["avg_pos_rate"]
        aggs["non_cum_gains"] = aggs["n_pos"] / aggs["pos_tot"]
        aggs["cum_gains"] = aggs["cum_n_pos"] / aggs["pos_tot"]
        aggs["cum_pos_rate"] = aggs["cum_n_pos"] / aggs["cum_count"]
        aggs = aggs.reset_index()
        aggs = aggs[["avg_pos_rate", "pos_tot", "cum_lift", "cum_pos_rate"]]
        return aggs

    grafana_metrics.update({"accuracy CV": model_dict["metrics"]["accuracy_cv"]})
    grafana_metrics.update({"precision CV": model_dict["metrics"]["precision_cv"]})
    grafana_metrics.update({"F1 CV": model_dict["metrics"]["f1_cv"]})
    grafana_metrics.update({"recall CV": model_dict["metrics"]["recall_cv"]})
    grafana_metrics.update({"roc auc CV": model_dict["metrics"]["roc_auc_cv"]})

    grafana_metrics.update({"accuracy train": model_dict["metrics"]["accuracy_train"]})
    grafana_metrics.update(
        {"precision train": model_dict["metrics"]["precision_train"]}
    )
    grafana_metrics.update({"F1 train": model_dict["metrics"]["f1_train"]})
    grafana_metrics.update({"recall train": model_dict["metrics"]["recall_train"]})
    grafana_metrics.update({"roc auc train": model_dict["metrics"]["roc_auc_train"]})

    grafana_metrics.update({"accuracy test": model_dict["metrics"]["accuracy_test"]})
    grafana_metrics.update({"precision test": model_dict["metrics"]["precision_test"]})
    grafana_metrics.update({"F1 test": model_dict["metrics"]["f1_test"]})
    grafana_metrics.update({"recall test": model_dict["metrics"]["recall_test"]})
    grafana_metrics.update({"roc auc test": model_dict["metrics"]["roc_auc_test"]})

    y_prob_test = pd.Series(
        model_dict["model"].predict_proba(X_test_unprepped)[:, 1],
        index=X_test_unprepped.index,
    )
    aggs = _calculate_aggregations(y_test, y_prob_test)
    grafana_metrics.update({"average positive rate": aggs["avg_pos_rate"].mean() * 100})
    grafana_metrics.update({"total positive rate": aggs["pos_tot"].mean()})
    grafana_metrics.update({"cumulative lift top 10": aggs["cum_lift"].head(10).mean()})
    grafana_metrics.update({"cumulative lift top 20": aggs["cum_lift"].head(20).mean()})
    grafana_metrics.update({"cumulative lift top 30": aggs["cum_lift"].head(30).mean()})
    grafana_metrics.update({"cumulative lift top 40": aggs["cum_lift"].head(40).mean()})
    grafana_metrics.update({"cumulative lift top 50": aggs["cum_lift"].head(50).mean()})
    grafana_metrics.update({"cumulative lift top 60": aggs["cum_lift"].head(60).mean()})
    grafana_metrics.update({"cumulative lift top 70": aggs["cum_lift"].head(70).mean()})
    grafana_metrics.update({"cumulative lift top 80": aggs["cum_lift"].head(80).mean()})
    grafana_metrics.update({"cumulative lift top 90": aggs["cum_lift"].head(90).mean()})
    grafana_metrics.update(
        {"cumulative lift top 100": aggs["cum_lift"].head(100).mean()}
    )

    grafana_metrics.update(
        {"cumulative positive rate top 10": aggs["cum_pos_rate"].head(10).mean() * 100}
    )
    grafana_metrics.update(
        {"cumulative positive rate top 20": aggs["cum_pos_rate"].head(20).mean() * 100}
    )
    grafana_metrics.update(
        {"cumulative positive rate top 30": aggs["cum_pos_rate"].head(30).mean() * 100}
    )
    grafana_metrics.update(
        {"cumulative positive rate top 40": aggs["cum_pos_rate"].head(40).mean() * 100}
    )
    grafana_metrics.update(
        {"cumulative positive rate top 50": aggs["cum_pos_rate"].head(50).mean() * 100}
    )
    grafana_metrics.update(
        {"cumulative positive rate top 60": aggs["cum_pos_rate"].head(60).mean() * 100}
    )
    grafana_metrics.update(
        {"cumulative positive rate top 70": aggs["cum_pos_rate"].head(70).mean() * 100}
    )
    grafana_metrics.update(
        {"cumulative positive rate top 80": aggs["cum_pos_rate"].head(80).mean() * 100}
    )
    grafana_metrics.update(
        {"cumulative positive rate top 90": aggs["cum_pos_rate"].head(90).mean() * 100}
    )
    grafana_metrics.update(
        {
            "cumulative positive rate top 100": aggs["cum_pos_rate"].head(100).mean()
            * 100
        }
    )

    return grafana_metrics


def get_grafana_metrics_predict(
    grafana_metrics: dict, df: pd.DataFrame, target: str, features: list
):
    """
    adds descriptive statistics of features to grafana_metrics dict
    """

    grafana_metrics.update({"len_df": len(df)})

    for f in features:
        grafana_metrics.update(
            {f"perc_missing_{f.replace(' ', '_')}": df[f].isna().mean()}
        )

        if df[f].dtypes == "float":
            grafana_metrics.update({f"mean_{f.replace(' ', '_')}": np.mean(df[f])})
            grafana_metrics.update({f"std_{f.replace(' ', '_')}": np.std(df[f])})
            grafana_metrics.update({f"var_{f.replace(' ', '_')}": np.var(df[f])})
        else:
            grafana_metrics.update({f"nunique_{f.replace(' ', '_')}": df[f].nunique()})

    # order predictions
    df = df.sort_values(target).reset_index(drop=True)

    # add overall mean to grafana_metrics
    grafana_metrics.update(
        {f"mean_{target.replace(' ', '_')}": np.mean(df[target]).round(4)}
    )

    # add group mean to grafana_metrics
    df["group"] = (np.arange(0, len(df), 1) / len(df) * 10).astype(int) + 1
    groups = list(df.group.unique())

    for g in groups:
        grafana_metrics.update(
            {f"predict_mean_target_group_{g}": df.query(f"group == {g}")[target].mean()}
        )

    # add frac size of bins to grafana_metrics
    bins = [
        (0, 0.1),
        (0.1, 0.2),
        (0.2, 0.3),
        (0.3, 0.4),
        (0.4, 0.5),
        (0.5, 0.6),
        (0.6, 0.7),
        (0.7, 0.8),
        (0.8, 0.9),
        (0.9, 1.0),
    ]
    for b in bins:
        frac = len(df.query(f"{target} > {b[0]} and {target} <= {b[1]}")) / len(df)
        grafana_metrics.update({f"predict_target_size_bin_{int(b[0] * 10)}": frac})

    # round values in dict
    grafana_metrics = {key: round(grafana_metrics[key], 4) for key in grafana_metrics}

    return grafana_metrics
