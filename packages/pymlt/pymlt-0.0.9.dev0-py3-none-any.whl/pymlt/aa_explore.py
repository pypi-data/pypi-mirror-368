"""
This module contains functionalities to explore your data (structure).

Functions included:
- check_one_val_feature
- check_sparse_features
- initial_acc_estimate
- pandas_profiling
- correlation_matrix
- proportion_calculation
- proportion_visualization
- mean_fpr_tpr
- sampling_roc
"""

import logging
import math
import os
from datetime import date
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_profiling as pf
import plotly.express as px
import seaborn as sns
from imblearn import FunctionSampler
from imblearn.over_sampling import ADASYN, SMOTE, RandomOverSampler
from imblearn.pipeline import make_pipeline
from imblearn.under_sampling import NearMiss, RandomUnderSampler
from lightgbm import LGBMClassifier
from sklearn.metrics import RocCurveDisplay, accuracy_score, auc, roc_curve
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline

_logger = logging.getLogger(__name__)


def check_one_val_feature(df: pd.DataFrame, drop_cols=False) -> pd.DataFrame:
    """Checks whether there are columns containing 1 unique value and drops them if
    drop_cols is True

    :param df: data
    :type df: pd.DataFrame
    :param drop_cols: whether to drop columns from the DataFrame, defaults to False
    :type drop_cols: bool, optional
    :return: the DataFrame with columns removed when drop_cols is True, else it
    will return the full DataFrame
    :rtype: pd.DataFrame
    """
    _logger.debug("Start checking whether features contain one unique value")
    cols = df.columns[(df.agg("nunique") == 1).values]
    if drop_cols:
        df = df.drop(labels=cols, axis=1)
        _logger.info(f"columns {list(cols)} have 1 unique value and will be dropped")
    if not drop_cols:
        _logger.info(f"columns {list(cols)} have 1 unique value")

    return df


def check_sparse_features(df: pd.DataFrame, threshold: float) -> list:
    """Calculates the percentage of missing values for each column and returns them when the
    percentage is above the given threshold

    :param df: data
    :type df: pd.DataFrame
    :param threshold: float between 0 and 1 that determines the percentage of missing allowed
    :type threshold: float
    :raises ValueError: if treshold is larger than 1 or smaller than 0
    :return: list of the column names that have fewer than 'threshold' values
    :rtype: list
    """
    _logger.debug(
        f"checking whether columns hold more than {threshold * 100} % empty values"
    )
    if (threshold > 1) | (threshold < 0):
        raise ValueError("Choose a threshold between 0 and 1")

    upper_limit = math.floor(threshold * df.shape[0])
    cols = df.columns[(df.isna().sum() > upper_limit).values]
    _logger.info(
        f"Warning: columns {list(cols)} have more than "
        f"{threshold * 100}% missing values"
    )

    return cols


def initial_acc_estimate(y_train: list) -> float:
    """calculates the initial accuracy estimate based on the mode of y

    :param y_train: y values to be predicted
    :type y_train: list
    :return: accuracy estimate
    :rtype: float
    """
    _logger.debug("Calculating initial accuracy estimate based on the mode of y")
    majority_class = pd.Series(y_train).mode()
    prediction = np.full(shape=y_train.shape, fill_value=majority_class)
    _logger.info(
        "accuracy is {} if model only predicted the majority class".format(
            accuracy_score(y_train, prediction)
        )
    )

    return accuracy_score(y_train, prediction)


def pandas_profiling(df: pd.DataFrame, config_file="") -> None:
    """Generates a pandas profile report in an html file.
    If the function execution appears slow, you should customize the config file.
    You can start by setting html.minify_html to True and, under correlations, set all calculate to false.

    For more information on the contents and usage of the profile report,
        see https://pandas-profiling.github.io/pandas-profiling/docs/master/rtd/pages/getting_started.html

    **This function will create a new folder in /out and writes files to your local directory.**
    :param df: Dataframe to profile
    :type df: pd.DataFrame
    :param config_file: File containing the custom configurations for the profile, defaults to ''
    :type config_file: str, optional
    :return: None
    """

    if os.path.isfile(config_file):
        _logger.info(f"Generating profile report using config file{config_file}")
        profile = pf.ProfileReport(df, config_file=config_file)
    else:
        _logger.info("Generating profile report with default config settings")
        profile = pf.ProfileReport(df)

    folder_to_log = os.path.dirname(__file__) + "/../../out/pandas_profiling/"
    Path(folder_to_log).mkdir(parents=True, exist_ok=True)
    profile.to_file(
        f"{folder_to_log}pandas_profiling_{date.today().strftime('%b-%d-%Y')}.html"
    )


def correlation_matrix(df: pd.DataFrame, threshold=0.0):
    """Compute and display the pairwise correlation of the numerical columns within a dataframe. NA/null values are excluded.
    The default includes all numerical columns (no active threshold).
    Adjusting the threshold might be convenient for limiting the number of numerical columns.
    **This function will create a new folder in /out and writes files to your local directory.**

    :param df: data to compute correlations
    :type df: pd.DataFrame
    :param threshold: only columns where there is at least one correlation greater than the absolute threshold are included, defaults to 0.0
    :type threshold: float, optional
    """
    plt.figure(figsize=(20, 17))

    corr = df.corr()
    passed = set()
    for r, c in combinations(corr.columns, 2):
        if abs(corr.loc[r, c]) >= threshold:
            passed.add(r)
            passed.add(c)
    passed = sorted(passed)
    corr = corr.loc[passed, passed]

    sns.heatmap(
        corr,
        cmap="RdBu",
        vmin=-1,
        vmax=1,
        linewidth=1,
        linecolor="black",
        annot_kws={"fontsize": 14},
        annot=True,
        fmt=".3f",
    )
    plt.title("Correlation Matrix", fontsize=18)
    plt.xticks(fontsize=14, rotation=45)
    plt.yticks(fontsize=14, rotation=45)

    folder_to_log = os.path.dirname(__file__) + "/../../out/correlation_matrix/"
    Path(folder_to_log).mkdir(parents=True, exist_ok=True)
    plt.savefig(
        folder_to_log + f"correlation_matrix_{date.today().strftime('%b-%d-%Y')}.jpeg"
    )
    plt.show()


def proportion_calculation(
    df: pd.DataFrame,
    features: list = None,
    target: str = "y_var",
    max_unique_values: int = 12,
):
    """Generates proportion calculation for features with a maximum of unique values, given by the variable max_unique_values.
    The calculation contains per feature a overview with the proportion of the 0/1 from the target variable.
    This applies to both the absolute and relative distribution.
    If there is no x_variables list given, all columns (except for the target) will be processed.

    :param df: Dataframe with all the x variable and y variable
    :type df: pd.DataFrame
    :param features: List with all the relevant features, defaults to None
    :type features: list, optional
    :param target: The name of the target variable. It has to be a part of the given df.
        The values of this variable has to be 0/1. , defaults to 'y_var'
    :type target: str, optional
    :param max_unique_values: The number of the maximum unique values from the given features.
        If a feature has more unique values, it will be skipped. , defaults to 12
    :type max_unique_values: int, optional
    :return df_prop_calculation: A dataset that contains the proportion calculation per relevant feature
    :rtype df_prop_calculation: pd.DataFrame
    """
    df_prop_calculations = (
        pd.DataFrame()
    )  # create a empty dataframe where all the proportion calculations can be stored in

    if features is None:
        features = list(df.columns.values)

    features = [x.lower() for x in features]
    target = target.lower()
    if target in features:
        features.remove(target)

    # Counts the unique values within the features. If they has more unique values than X, they will be skipped
    df_unique = df[features].nunique()
    # Listing columns with more/less than X (default 12) unique values
    list_unique_over_X = df_unique[df_unique > max_unique_values].index.tolist()
    list_unique_under_X = df_unique[df_unique <= max_unique_values].index.tolist()

    # Logs the features that will be skipped
    if len(list_unique_over_X) > 1:
        _logger.info(
            f"""The following features has over  {max_unique_values} unique values. They will be skipped in calculate the proportion:
        {list_unique_over_X}"""
        )

    # Looping over all the features
    for feature in list_unique_under_X:
        df_prop = pd.DataFrame(df.groupby([feature, target]).size())
        df_prop = df_prop.reset_index()
        df_prop.columns = ["feature_value", "target", "count"]

        # Create 2 dummy records per unique value (y=0 and y=1), so there is a record for each possibility.
        # This is needed to create equal lists for creating the graphs.
        unique_x_var = df_prop["feature_value"].unique().tolist()
        df_dummy = pd.DataFrame(columns=["feature_value", "target"])

        # Change the dummy datatypes to the actual datatypes so they can be merged later
        for x in df_dummy.columns:
            df_dummy[x] = df_dummy[x].astype(df_prop[x].dtypes.name)

        for i in unique_x_var:
            dummy_y0 = pd.DataFrame([[i, 0]], columns=["feature_value", "target"])
            dummy_y1 = pd.DataFrame([[i, 1]], columns=["feature_value", "target"])
            df_dummy = df_dummy.append(dummy_y0)
            df_dummy = df_dummy.append(dummy_y1)

        # Join the dummy data with the actual data (with a left join where right is null)
        # This ensures that the dummy records of which there is no real data will be merged
        df_dummy = (
            df_dummy.merge(
                df_prop[["feature_value", "target"]],
                left_on=["feature_value", "target"],
                right_on=["feature_value", "target"],
                indicator="i",
                how="outer",
            )
            .query('i == "left_only"')
            .drop("i", 1)
        )
        df_dummy["count"] = 0

        df_prop = df_prop.append(df_dummy)  # Add the dummy data to the actual dataset
        # end of creating dummy records

        df_prop = df_prop.set_index("feature_value")
        df_prop["total"] = (
            df_prop["count"].groupby(level="feature_value").sum()
        )  # count the total occurrences per feature_value for calculation the relative distribution
        df_prop["percentage"] = (
            df_prop["count"] / df_prop["total"] * 100
        )  # calculate the percentage of the 0/1 values related to the total occurrences
        df_prop = df_prop.reset_index()

        df_prop = df_prop.sort_values(
            by=["feature_value", "target"], ascending=[True, False]
        )

        df_prop["target"] = (
            df_prop["target"].astype(int).astype(str)
        )  # convert float to int (so,without de decimals) and then to string.
        # This is because the plot color wouldn't show a continuous color
        df_prop.insert(
            0, "feature_name", feature
        )  # add a column with the "feature name" as the first column of the dataframe

        df_prop_calculations = df_prop_calculations.append(df_prop)

    return df_prop_calculations


def proportion_visualization(df: pd.DataFrame):
    """Generates proportion visualizations for each feature in the dataframe
    The visualization shows per feature a graph with the proportion of the 0/1 from the target variable.
    The absolute and relative distribution is visible.

    :param df: Dataframe with a proportion calculation, based on the output of the proportion_calculation function with columns:
        feature_name, feature_value, y_var, count, total, percentage
    :type df: pd.DataFrame
    """

    for feature in df["feature_name"].unique():  # iterate over all the features
        df_prop = df[df["feature_name"] == feature]

        # Create the figures with the percentages on the y axis. The absolute counts are the bar values.
        fig = px.bar(
            df_prop,
            x="feature_value",
            y="percentage",
            color="target",
            color_discrete_map={"1": "rgb(153, 230, 153)", "0": "rgb(255, 102, 102)"},
            barmode="stack",
            text=df_prop["count"],
        )

        fig.update_layout(
            title=f"Distribution 0/1 variable: {feature}",
            xaxis_title=feature,
            yaxis_title="count",
            width=1600,
            height=600,
        )

        fig.show()


def mean_fpr_tpr(
    X_train: np.ndarray, y_train: np.ndarray, model: Pipeline, n_splits=3
) -> list:
    """Generates the mean false positive rate and the true positive rate.

    :param X_train: features to predict the target variable
    :type X_train: numpy.ndarray
    :param y_train: target variable
    :type y_train: numpy.ndarray
    :param model: pipline including an over or under sampling technique and a classifier
    :type model: Pipeline
    :param n_splits: number of splits in the cross-validation, defaults to 3
    :type n_splits: int, optional
    :return: mean true positive rate, mean false positive rate, mean area under the curve
    :rtype: list
    """
    cv = StratifiedKFold(n_splits=n_splits)
    class_distribution = pd.Series(y_train).value_counts(normalize=True)
    pos_label = class_distribution.idxmin()

    # Compute the mean fpr/tpr to get the mean ROC curve
    mean_tpr, mean_fpr = 0.0, np.linspace(0, 1, 100)
    for train, test in cv.split(X_train, y_train):
        model.fit(X_train[train], y_train[train])
        y_proba = model.predict_proba(X_train[test])

        pos_label_idx = np.flatnonzero(model.classes_ == pos_label)[0]
        fpr, tpr, _ = roc_curve(
            y_train[test], y_proba[:, pos_label_idx], pos_label=pos_label
        )
        mean_tpr += np.interp(mean_fpr, fpr, tpr)
        mean_tpr[0] = 0.0

    mean_tpr /= cv.get_n_splits(X_train, y_train)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    return mean_fpr, mean_tpr, mean_auc


def sampling_roc(
    X_train: np.ndarray,
    y_train: np.ndarray,
    plot_path: str,
    classifier=LGBMClassifier(),
):
    """Generates a plot with the ROC curve for different over or under sampling methods used on the dataset.
    The plot will be saved in the "out" folder of your repository. the different sampling methods used are:
    - FunctionSampler https://imbalanced-learn.org/dev/references/generated/imblearn.FunctionSampler.html
    - RandomOverSampler https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.RandomOverSampler.html
    - ADASYN https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.ADASYN.html
    - SMOTE https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.SMOTE.html
    - RandomUnderSampler https://imbalanced-learn.org/stable/references/generated/imblearn.under_sampling.RandomUnderSampler.html
    - NearMiss (version 3) https://imbalanced-learn.org/dev/references/generated/imblearn.under_sampling.NearMiss.html

    :param X_train: features to predict the target variable
    :type X_train: np.ndarray
    :param y_train: target variable
    :type y_train: np.ndarray
    :param plot_path: file path to save the plot
    :type plot_path: str
    :param classifier: type of classifier the model uses, defaults to LGBMClassifier()
    :type classifier: _type_, optional
    """
    # Create different pipelines to compare
    pipeline = [
        make_pipeline(FunctionSampler(), classifier),
        make_pipeline(RandomOverSampler(random_state=42), classifier),
        make_pipeline(ADASYN(random_state=42), classifier),
        make_pipeline(SMOTE(random_state=42), classifier),
        make_pipeline(RandomUnderSampler(random_state=42), classifier),
        make_pipeline(NearMiss(version=3), classifier),
    ]

    # Calculate the fpr/tpr to get the mean ROC curve
    disp = []
    for model in pipeline:
        mean_fpr, mean_tpr, mean_auc = mean_fpr_tpr(X_train, y_train, model)

        # Create a display that we will reuse to make the aggregated plots for all methods
        disp.append(
            RocCurveDisplay(
                fpr=mean_fpr,
                tpr=mean_tpr,
                roc_auc=mean_auc,
                estimator_name=f"{model[0].__class__.__name__}",
            )
        )

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 10))
    for d in disp:
        d.plot(ax=ax, linestyle="--")
    ax.plot([0, 1], [0, 1], linestyle="--", color="k")
    ax.axis("square")
    fig.suptitle("Comparison of over and under-sampling methods")
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    sns.despine(offset=10, ax=ax)

    # Log to plot
    folder_to_log = os.path.dirname(__file__) + plot_path
    Path(folder_to_log).mkdir(parents=True, exist_ok=True)
    plt.savefig(
        folder_to_log + f"sampling_methods_{date.today().strftime('%Y%m%d')}.png"
    )
    plt.show()
