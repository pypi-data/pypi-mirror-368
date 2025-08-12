"""
This module contains a collection of functions to evaluate a fitted model.

Functions included:
- feature_importance
- confusion_matrix
- contributing_features
- create_feature_lists
- underfit_overfit
- plot_recall_precision
- plot_roc_curve
- plot_score_vs_actuals
"""

import logging
import math
import os
from collections import Counter
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFECV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    plot_confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

_logger = logging.getLogger(__name__)


def _create_bins(
    num: float, df: pd.DataFrame, top_perc: float, buckets: int
) -> pd.DataFrame:
    """This is a helper function for function 'plot_score_vs_actuals'

    :param num: number of probabilities to include in the bins
    :type num: float
    :param df: data to include
    :type df: pd.DataFrame
    :param top_perc: percentage of data that is included
    :type top_perc: float
    :param buckets: number of buckets
    :type buckets: int
    :return: data to be plotted
    :rtype: pd.DataFrame
    """
    df = df.iloc[0 : int(math.ceil(num)), :].copy()
    df["bins"] = pd.qcut(df["pred"], q=buckets, labels=False, duplicates="drop")
    plot_df = df.groupby("bins").agg({"bins": "count", "pred": "min", "labels": "mean"})
    plot_df = plot_df.rename({"bins": "count"}, axis=1).reset_index(drop=False)
    plot_df["labels"] *= 100

    # create categories based on model score buckets
    add = 100 - (100 * top_perc)
    step = (100 - add) / len(set(df["bins"]))

    plot_df["score_cat"] = [
        str(round(add + (x * step))) + "% - " + str(round(add + ((x + 1) * step))) + "%"
        for x in plot_df.index
    ]

    return plot_df


def _plot_bins(plot_df: pd.DataFrame, baseline: float) -> None:
    """This is a helper function for function 'plot_score_vs_actuals'

    :param plot_df: the data to plot
    :type plot_df: pd.DataFrame
    :param baseline: baseline value at which a vertical line is plotted
    :type baseline: float
    """

    order = plot_df.sort_values(by="bins")["score_cat"].tolist()[::-1]
    sns.set(rc={"figure.figsize": (15, 10)})
    sns.set(style="whitegrid")
    ax = sns.barplot(
        data=plot_df,
        x="labels",
        y="score_cat",
        order=order,
        alpha=0.6,
        palette="Spectral_r",
    )
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set(xlabel="Actual Y", ylabel="Model scores")
    plt.axvline(x=baseline * 100, color="black", alpha=0.6)
    trans = ax.get_xaxis_transform()
    plt.text(
        (baseline * 100) - 1.5,
        0.01,
        "baseline",
        transform=trans,
        rotation=90,
        size="medium",
    )

    folder_to_log = os.path.dirname(__file__) + "/../../out/score_vs_actuals/"
    Path(folder_to_log).mkdir(parents=True, exist_ok=True)
    plt.savefig(
        folder_to_log + f"score_vs_actuals_{date.today().strftime('%Y%m%d')}.png"
    )

    plt.show()
    ax.clear()


def plot_score_vs_actuals(
    y_pred_proba: list, y: list, buckets: int = 10, top_perc: float = 1
) -> pd.DataFrame:
    """Orders the predicted y and compares the actual y percentage per bucket

    :param y_pred_proba: predicted probabilities
    :type y_pred_proba: list
    :param y: actual target values
    :type y: list
    :param buckets: number of buckets, defaults to 10
    :type buckets: int, optional
    :param top_perc: select a certain percentage of the highest scoring probabilities, defaults to 1
    :type top_perc: float, optional
    :return: the buckets and y percentage
    :rtype: pd.DataFrame
    """
    num = len(y_pred_proba) * top_perc
    df = pd.DataFrame({"labels": y, "pred": y_pred_proba})
    df = df.sort_values(by=["pred"], ascending=False)

    # Calculating baseline for class 1 occurrence
    baseline = df["labels"].mean()

    # create aggregated result per bin
    plot_df = _create_bins(num, df, top_perc, buckets)

    # plot percentages
    _plot_bins(plot_df, baseline)

    return plot_df


def feature_importance(fitted_model: Pipeline, feature_columns: list) -> pd.Series:
    """Takes the fitted model and displays a horizontal bar plot of the relative features importance

    :param fitted_model: the fitted model
    :type fitted_model: Pipeline
    :param feature_columns: the names of the feature columns
    :type feature_columns: list
    :return: the features importance
    :rtype: pd.Series
    """
    importances = fitted_model.feature_importances_
    importances_as_series = pd.Series(importances, index=feature_columns)
    (importances_as_series.nlargest(20).plot(kind="barh"))
    plt.show()
    plt.close()

    _logger.info(f"Feature importance: {importances_as_series}")

    return importances_as_series


def confusion_matrix(
    fitted_model: Pipeline,
    x_test: pd.DataFrame,
    y_test: pd.DataFrame,
    print_result: bool = True,
) -> list:
    """Plots and prints the non-normalized and normalized confusion matrices
    **This function will create a new folder in /out and writes files to your local directory.**

    :param fitted_model: fitted model
    :type fitted_model: Pipeline
    :param x_test: feature columns of the test set
    :type x_test: pd.DataFrame
    :param y_test: target column of the test set
    :type y_test: pd.DataFrame
    :param print_result: boolean denoting whether to print the confusion matrices, defaults to True
    :type print_result: bool, optional
    :return: non-normalized and the normalized confusion matrices
    :rtype: list
    """
    confusion_matrices = []
    np.set_printoptions(precision=2)

    # Plot confusion matrices
    titles_options = [
        ("Confusion matrix, without normalization", None, "non-normalized"),
        ("Normalized confusion matrix", "true", "normalized"),
    ]
    for title, normalize, type in titles_options:
        disp = plot_confusion_matrix(
            fitted_model, x_test, y_test, cmap=plt.cm.Blues, normalize=normalize
        )
        disp.ax_.set_title(title)
        if print_result:
            print(title)
            print(disp.confusion_matrix)
        confusion_matrices.append(disp.confusion_matrix)

        df = pd.DataFrame(
            {
                "Column1": disp.confusion_matrix[:, 0],
                "Column2": disp.confusion_matrix[:, 1],
            }
        )

        folder_to_log = os.path.dirname(__file__) + "/../../out/confusion_matrices/"
        Path(folder_to_log).mkdir(parents=True, exist_ok=True)

        df.to_csv(
            folder_to_log
            + "{}_confusion_matrix_{}.csv".format(
                type, date.today().strftime("%b-%d-%Y")
            )
        )
        plt.savefig(
            folder_to_log
            + "{}_confusion_matrix_{}.jpeg".format(
                type, date.today().strftime("%b-%d-%Y")
            ),
            bbox_inches="tight",
        )
        plt.show()
        plt.close()
    return confusion_matrices


def contributing_features(
    model_type: str,
    X_train: pd.DataFrame,
    y_train: pd.DataFrame,
    cpus: int = 3,
    step_size: int = 5,
) -> list:
    """Performs recursive feature elimination and cross-validation (RFECV) with a specified model in order to generate a list of
    features that contribute to the overall scoring metric. Scaling is performed separately since the RFECV cannot easily handle Pipelines

    :param model_type: The model to perform RFECV with.
    :type model_type: str
    :param X_train: dataFrame with all the features of the train set
    :type X_train: pd.DataFrame
    :param y_train: dataFrame with the dependent variable of the train set
    :type y_train: pd.DataFrame
    :param cpus: number of core processing unit's used to run the cross validation, defaults to 3
    :type cpus: int, optional
    :param step_size: number of features to remove each RFECV cycle, defaults to 5
    :type step_size: int, optional
    :return: a list with the most important features
    :rtype: list
    """

    _logger.debug(f"Generating a list of contributing features using a {model_type}")

    if model_type == "RandomForestClassifier":
        model = RandomForestClassifier(n_estimators=100, max_depth=10)
    elif model_type == "XGBClassifier":
        model = XGBClassifier(
            n_estimators=20, use_label_encoder=False, eval_metric="mlogloss"
        )
    elif model_type == "LogisticRegression":
        model = LogisticRegression(max_iter=500)
    else:
        _logger.warning(f"The model type '{model_type}' is not (yet) implemented.")
        return

    selector = RFECV(model, step=step_size, cv=3, scoring="accuracy", n_jobs=cpus)
    selector = selector.fit(X_train, y_train)
    feature_list = list(X_train.columns[selector.support_])

    print(
        f"{model_type}: The optimal number of features is {selector.n_features_}. \
        Please keep in mind that the stepsize is {step_size}."
    )

    return feature_list


def create_feature_lists(dependent_variable: str, *args: list) -> list:
    """Creates a feature list based on the input of the feature selection algorithms or business sense input.
    It counts the occurrences of features in the input lists and sorts them by relevance. This results in
    a faster process compared to re-running multiple feature selection algorithms since it saves the output
    of the feature selection algorithms and it creates a benchmark for the different sets of features.
    **This function will create a new folder in /out and writes files to your local directory.**

    :param dependent_variable: column name of the dependent variable which will be inserted the return list
    :type dependent_variable: str
    :param *args: arbitrary number of lists with features
    :type *args: list
    :raises TypeError: if *args is not a list
    :return: a list with the features that can be used to export the relevant subset of the dataframe for the modeling phase
    :rtype: list
    """
    if not isinstance(dependent_variable, str):
        raise TypeError(
            f"dependent_variable must be a string, received {type(dependent_variable)}"
        )

    folder_to_log = os.path.dirname(__file__) + "/../../out/feature_lists/"
    Path(folder_to_log).mkdir(parents=True, exist_ok=True)

    joined_list = []
    len_args = len(args)

    for sublist in args:
        if not isinstance(sublist, list):
            raise TypeError(f"*args must be a list, received {type(sublist)}")
        joined_list = joined_list + sublist

    combined = pd.Series(
        dict(Counter(joined_list))
    )  # count the number of votes per variable to create separate lists

    array = np.arange(1, len_args + 1)
    reversed_array = array[
        ::-1
    ]  # reversed to end with the most extensive set of features which is used for export

    temp_list = []
    for i in reversed_array:
        temp_list = list(combined.index[combined >= i])
        file = f"combined_list_{i}_votes"
        path = os.path.join(folder_to_log, file)

        pd.DataFrame(data={"features": temp_list}).to_csv(
            path, sep=";", encoding="utf-8", index=False
        )

        print(
            f"The list with {i} vote(s) contains {len(temp_list)} variables and can be found in {path}"
        )

    temp_list.insert(0, dependent_variable)

    return temp_list


def underfit_overfit(
    model: Pipeline,
    x_train: pd.DataFrame,
    y_train: pd.DataFrame,
    x_val: pd.DataFrame,
    y_val: pd.DataFrame,
    step=1000,
):
    """Trains, predicts and evaluates the model for different sizes of the dataset. High scores on the trainset and low
    scores on the validation set indicates an overfit, low scores on both the train and test set indicates underfit.
    Based on Hands-On Machine Learning with Scikit-Learn & TensorFlow by Aurelien Geron.
    Can be used to give an indication of the necessary minimum sample size.

    :param model: The model used to create predictions based on the features of the validation set
    :type model: Pipeline
    :param x_train: features of the train set
    :type x_train: pd.DataFrame
    :param y_train: the dependent variable of the train set
    :type y_train: pd.DataFrame
    :param x_val: features of the validation set
    :type x_val: pd.DataFrame
    :param y_val: the dependent variable of the validation set
    :type y_val: pd.DataFrame
    :param step: the increment of training data used to evaluate the prediction error for the train and validation set., defaults to 1000
    :type step: int, optional
    """
    train_errors, val_errors = [], []

    for m in range(100, len(x_train), step):
        model.fit(x_train[:m], y_train[:m])

        y_train_predict = model.predict(x_train[:m])
        y_val_predict = model.predict(x_val)

        train_errors.append(accuracy_score(y_train[:m], y_train_predict))
        val_errors.append(accuracy_score(y_val, y_val_predict))

        if m % 5000 == 100:
            print(f"Currently at iteration {m} of {int(len(x_train) / step) * step}")

    plt.plot(train_errors, label="train")
    plt.plot(val_errors, label="validation")
    plt.legend()
    plt.show()
    plt.close()


def plot_recall_precision(
    model: Pipeline, x_val: pd.DataFrame, y_val: pd.DataFrame, save_result: bool = False
):
    """Shows a plot with the recall and precision functions per threshold.
    Based on Hands-On Machine Learning with Scikit-Learn & TensorFlow by Aurelien Geron.
    **If save_result is set to True, this function will create a new folder in /out and writes files to your local directory.**

    :param model: model used to create predictions based on the features of the validation set.
    :type model: Pipeline
    :param x_val: features of the validation set.
    :type x_val: pd.DataFrame
    :param y_val: the dependent variable of the validation set.
    :type y_val: pd.DataFrame
    :param save_result: boolean denoting whether to print the confusion matrices, defaults to False
    :type save_result: bool, optional
    """
    model_proba = model.predict_proba(x_val)
    precision, recall, threshold = precision_recall_curve(y_val, model_proba[:, 1])

    plt.plot(threshold, precision[:-1], label="precision")
    plt.plot(threshold, recall[:-1], label="recall")
    plt.legend()

    if save_result:
        folder_to_log = os.path.dirname(__file__) + "/../../out/recall_precision_plots/"
        Path(folder_to_log).mkdir(parents=True, exist_ok=True)
        plt.savefig(
            f"{folder_to_log}/recall_precision_{date.today().strftime('%b-%d-%Y')}.jpeg"
        )

    plt.show()
    plt.close()


def plot_roc_curve(
    model: Pipeline, x_val: pd.DataFrame, y_val: pd.DataFrame, save_result: bool = False
) -> float:
    """
    Shows a plot with the Receiver Operating Characteristic (ROC) Curve
    **If save_result is set to True, this function will create a new folder in /out and writes files to your local directory.**

    :param model: model used to create predictions based on the features of the validation set.
    :type model: Pipeline
    :param x_val: features of the validation set.
    :type x_val: pd.DataFrame
    :param y_val: the dependent variable of the validation set.
    :type y_val: pd.DataFrame
    :param save_result: boolean denoting whether to print the confusion matrices, defaults to False
    :type save_result: bool, optional
    :return: area under the curve (AUC) score
    :rtype: float
    """
    model_proba = model.predict_proba(x_val)
    fpr, tpr, _ = roc_curve(y_val, model_proba[:, 1])
    auc_score = roc_auc_score(y_val, model_proba[:, 1])

    lw = 2
    plt.plot(
        fpr,
        tpr,
        color="darkorange",
        lw=lw,
        label="ROC curve (area = %0.2f)" % auc_score,
    )
    plt.plot([0, 1], [0, 1], color="navy", lw=lw, linestyle="--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Receiver operating characteristic example")
    plt.legend(loc="lower right")

    if save_result:
        folder_to_log = os.path.dirname(__file__) + "/../../out/roc_curves/"
        Path(folder_to_log).mkdir(parents=True, exist_ok=True)
        plt.savefig(
            f"{folder_to_log}/roc_curve_{date.today().strftime('%b-%d-%Y')}.jpeg"
        )

    plt.show()
    plt.close()
    return auc_score
