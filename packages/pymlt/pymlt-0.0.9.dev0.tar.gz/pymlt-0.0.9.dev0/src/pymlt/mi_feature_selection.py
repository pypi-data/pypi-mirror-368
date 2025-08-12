"""
Functions that uses modeling to perform feature selection.
"""

import os
from collections import Counter

import numpy as np
import pandas as pd
from boruta import BorutaPy
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFECV
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier


def scale_features(x_train: pd.DataFrame) -> pd.DataFrame:
    """
    Scaling of variables, i.e. (value - mean)/sd. Or in other words: the variable is expressed as the amount
    of standard deviations the value is removed from the mean.

    Parameters
    ----------
    x_train : dataframe
        Dataframe with all the independent variables (features) of the train set.

    Returns
    -------
    x_train_scaled : dataframe
        Dataframe with all the scaled independent variables (features) of the train set.
    """

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_train_scaled = pd.DataFrame(x_train_scaled, columns=x_train.columns)

    return x_train_scaled


def n_features_rf(
    x_train: pd.DataFrame, y_train: pd.DataFrame, cpus: int = 3, step_size: int = 5
) -> list:
    """
    RandomForestClassifier with recursive feature elimination and cross-validation (RFECV) in order to generate a list
    of features that contribute to the overall scoring metric.

    Scaling is performed separately since the RFECV cannot easily handle Pipelines.

    Parameters
    ----------
    x_train : dataframe
        Dataframe with all the independent variables (features) of the train set.
    y_train : dataframe
        Dataframe with the dependent variable of the train set.
    cpus : integer, default = 3
        Number of core processing unit's used to run the cross validation.
    step_size : int
        Determines the number of features to remove each RFECV cycle.

    Returns
    -------
    feature_list : list
        A list with the most important features.
    """

    rf_model = RandomForestClassifier(n_estimators=100, max_depth=10)
    selector = RFECV(rf_model, step=step_size, cv=3, scoring="accuracy", n_jobs=cpus)
    selector = selector.fit(x_train, y_train)
    feature_list = list(x_train.columns[selector.support_])

    print(
        f"RandomForest: The optimal number of features is {selector.n_features_} with a maximum accuracy\n"
        f"of {max(selector.grid_scores_):.1%}. Please keep in mind that the stepsize is {step_size}."
    )

    return feature_list


def n_features_xgb(
    x_train: pd.DataFrame, y_train: pd.DataFrame, cpus: int = 3, step_size: int = 5
) -> list:
    """
    XGBClassifier with recursive feature elimination and cross-validation (RFECV) in order to generate a list of
    features that contribute to the overall scoring metric.

    Scaling is performed separately since the RFECV cannot easily handle Pipelines.

    Parameters
    ----------
    x_train : dataframe
        Dataframe with all the independent variables (features) of the train set.
    y_train : dataframe
        Dataframe with the dependent variable of the train set.
    cpus : integer, default = 3
        Number of core processing unit's used to run the cross validation.
    step_size : int
        Determines the number of features to remove each RFECV cycle.

    Returns
    -------
    feature_list : list
        A list with the most important features.
    """

    xgboost_classifier = XGBClassifier(n_estimators=20)
    selector = RFECV(
        xgboost_classifier, step=step_size, cv=3, scoring="accuracy", n_jobs=cpus
    )
    selector = selector.fit(x_train, y_train)
    feature_list = list(x_train.columns[selector.support_])

    print(
        f"XGboost: The optimal number of features is {selector.n_features_} with a maximum accuracy\n"
        f"of {max(selector.grid_scores_):.1%}. Please keep in mind that the stepsize is {step_size}."
    )

    return feature_list


def n_features_logreg(
    x_train: pd.DataFrame, y_train: pd.DataFrame, cpus: int = 3, step_size: int = 5
) -> list:
    """
    LogisticRegression with recursive feature elimination and cross-validation (RFECV) in order to generate a list of
    features that contribute to the overall scoring metric.

    Scaling is performed separately since the RFECV cannot easily handle Pipelines.

    Parameters
    ----------
    x_train : dataframe
        Dataframe with all the independent variables (features) of the train set.
    y_train : dataframe
        Dataframe with the dependent variable of the train set.
    cpus : integer, default = 3
        Number of core processing unit's used to run the cross validation.
    step_size : int
        Determines the number of features to remove each RFECV cycle.

    Returns
    -------
    feature_list : list
        A list with the most important features.
    """

    logreg_model = LogisticRegression(max_iter=500)
    selector = RFECV(
        logreg_model, step=step_size, cv=3, scoring="accuracy", n_jobs=cpus
    )
    selector = selector.fit(x_train, y_train)
    feature_list = list(x_train.columns[selector.support_])

    print(
        f"Log. regression: The optimal number of features is {selector.n_features_} with a maximum accuracy\n"
        f"of {max(selector.grid_scores_):.1%}. Please keep in mind that the stepsize is 5."
    )

    return feature_list


def n_features_boruta(
    x_train: pd.DataFrame, y_train: pd.DataFrame, cpus: int = 3
) -> list:
    """
    Runs selected features based on the boruta algorithm, in this case a wrapper around a RandomForestClassifier.
    More info on Boruta can be found at https://pypi.org/project/Boruta/.

    Parameters
    ----------
    x_train : dataframe
        Pandas dataframe with all the independent variables (features) of the train set.
    y_train : dataframe
        Pandas dataframe with the dependent variable of the train set.
    cpus : integer, default = 3
        Number of core processing unit's used to run the cross validation.

    Returns
    -------
    feature_list : list
        A list with the most important features.
    """
    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)

    rf = RandomForestClassifier(n_jobs=cpus, class_weight="balanced", max_depth=5)
    feat_selector = BorutaPy(
        rf, n_estimators="auto", verbose=0, random_state=1, alpha=0.01
    )
    feat_selector.fit(x_train_scaled, y_train)
    feature_list = list(x_train.columns[feat_selector.support_])
    print(f"Boruta: The optimal number of features is {feat_selector.n_features_}")

    return feature_list


def create_feature_lists(dependent_variable: str, *args: list) -> list:
    """
    Creates feature lists based on the input of the feature selection algorithms or business sense input. Results in
    a faster process since it saves the output of the feature selection algorithms and it creates a benchmark for the
    different sets of features.

    Attention: this function assumes you are using the MI modeling template and that you currently are in your
    /notebook folder. You can check this with the os module via os.getcwd().

    **This function will create a new folder and writes files to your local directory.**

    Parameters
    ----------
    dependent_variable : str
        Column name of the dependent variable which will be inserted the return list.
    *args : list
        Arbitrary number of lists with features.

    Returns
    -------
    temp_list : list
        A list with the most extensive set of features which can be used to export the relevant subset of the dataframe
        for the modeling phase.
    """
    if not isinstance(dependent_variable, str):
        raise TypeError(
            f"dependent_variable must be a string, received {type(dependent_variable)}"
        )

    dir_list = []
    with os.scandir("../../") as entries:
        for entry in entries:
            if entry.is_dir():
                dir_list.append(entry.name.lower())

    if "feature_lists" not in dir_list:
        os.mkdir("../feature_lists")

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
        path = os.path.join("../..", "feature_lists", file)

        pd.DataFrame(data={"features": temp_list}).to_csv(
            path, sep=";", encoding="utf-8", index=False
        )

        print(
            f"The list with {i} vote(s) contains {len(temp_list)} variables and can be found in {path}"
        )

    temp_list.insert(0, dependent_variable)

    return temp_list
