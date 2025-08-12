"""
This module contains a collection of functions to transform data.

Functions included:
- redefine_missing_values
- impute_data
- drop_missings
- percentile_outlier_replacement
- add_interactions
- drop_near_zero_variance_features
- scale_features
- fit_trend_model
- correct_trends
- duplicate_rows
- over_under_sampling
"""

import logging
from typing import Tuple, Union

import numpy as np
import pandas as pd
import statsmodels.api as sm
from imblearn.over_sampling import ADASYN, SMOTE, RandomOverSampler
from imblearn.under_sampling import NearMiss, RandomUnderSampler
from sklearn.base import BaseEstimator
from sklearn.feature_selection import VarianceThreshold
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

_logger = logging.getLogger(__name__)


def redefine_missing_values(
    df: pd.DataFrame, replace_values: Union[int, str], cols: pd.Series = None
) -> pd.DataFrame:
    """This function can be used to identify values as being missing and transform them to NaN

    :param df: DataFrame with missing values of different formats
    :type df: pd.DataFrame
    :param replace_values: values indicating missing values to be replaced, null, 'null', -1, 0, 'empty', ...
    :type replace_values: Union[int, str]
    :param cols: names of the columns that the transformation should be applied to, optional, defaults to None
    :type cols: pd.Series, optional
    :return: DataFrame with redefined missing values
    :rtype: pd.DataFrame
    """

    if cols is None:
        df = df.replace(to_replace=replace_values, value=np.nan)
    else:
        df[cols] = df[cols].replace(to_replace=replace_values, value=np.nan)
    return df


def impute_data(
    df: pd.DataFrame, col_list: list, type: Union[int, str]
) -> pd.DataFrame:
    """This function imputes missing values in the specified columns.
    The function can be used for float, numeric or categorical values.
    Note: not every imputation is suitable for all dtypes

    :param df: dataframe containing missing values
    :type df: pd.DataFrame
    :param col_list: names of the columns the imputation of missings should be done for
    :type col_list: list
    :param type: 'median', 'mean', 'most_frequent', -1, 0
    :type type: Union[int, str]
    :return: imputed df
    :rtype: pd.DataFrame
    """

    for column in col_list:
        if type in ("median", "mean", "most_frequent"):
            df[column] = SimpleImputer(
                missing_values=np.nan, strategy=type
            ).fit_transform(df[column].to_numpy().reshape(-1, 1))

        if type in (-1, 0):
            df[column] = SimpleImputer(
                missing_values=np.nan, strategy="constant", fill_value=type
            ).fit_transform(df[column].to_numpy().reshape(-1, 1))

    return df


# TODO rewrite: make it use exploration function
def drop_missings(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """Drops variables with a percentage missing above the threshold. Imputation of these missing values should
    be considered before dropping the full variables.

    :param df: input data
    :type df: pd.DataFrame
    :param threshold: value between 0 and 1 corresponding to the percentage of missing values per variable
    :type threshold: float
    :raises ValueError: in case the threshold is not between 0 and 1.
    :return: the dataframe without the dropped variables based on the threshold
    :rtype: pd.DataFrame
    """

    if (threshold > 1) | (threshold < 0):
        raise ValueError("Choose a threshold between 0 and 1")
    else:
        try:
            missings = df.isna().mean().reset_index()
            missings.columns = ["column", "perc_missings"]
            drop_list = missings[missings["perc_missings"] >= threshold][
                "column"
            ].tolist()
            return df.drop(columns=drop_list, axis=1)
        except AttributeError:
            print("You must use a Pandas DataFrame as input")


def percentile_outlier_replacement(
    df: pd.DataFrame,
    col: str,
    replacement: str = "percentile",
    top_percentile: int = 90,
    bot_percentile: int = 10,
) -> pd.DataFrame:
    """This function identifies and replace the values in the top and bottom percentiles of the requested colum

    :param df: dataframe containing all features
    :type df: pd.DataFrame
    :param col: column
    :type col: str
    :param replacement: {'nan', 'percentile', 'mean'}, default 'percentile'. Choice of replacement value, defaults to "percentile"
    :type replacement: str, optional
    :param top_percentile: the top percentile to use as percentile replacement and from which it is defined an outlier, defaults to 90
    :type top_percentile: int, optional
    :param bot_percentile:  the bottom percentile to use as percentile replacement and from which it is defined an, defaults to 10
    :type bot_percentile: int, optional
    :return: DataFrame with top and bottom percentiles replaced with nans, percentiles or means
    :rtype: pd.DataFrame
    """

    percentile_bot = np.percentile(df[col], bot_percentile)
    percentile_top = np.percentile(df[col], top_percentile)
    if replacement == "nan":
        replacement_top = np.nan
        replacement_bot = np.nan
    if replacement == "percentile":
        replacement_top = percentile_top
        replacement_bot = percentile_bot
    if replacement == "mean":
        replacement_top = df[col].mean(skipna=True)
        replacement_bot = df[col].mean(skipna=True)
    df[col] = np.where(df[col] < percentile_bot, replacement_bot, df[col])
    df[col] = np.where(df[col] > percentile_top, replacement_top, df[col])
    return df


def add_interactions(df: pd.DataFrame, col1: str, col2: str) -> pd.DataFrame:
    """This function adds a new feature that consists of the product of two existing features.

    :param df: dataframe containing the variables to be multiplied
    :type df: pd.DataFrame
    :param col1: column containing the first feature of the interaction
    :type col1: str
    :param col2: column containing the second feature of the interaction
    :type col2: str
    :return: df with added interaction terms
    :rtype: pd.DataFrame
    """

    df[f"{col1}_{col2}_interaction"] = df[col1] * df[col2]

    return df


# TODO add threshold as parameter
def drop_near_zero_variance_features(df: pd.DataFrame) -> pd.DataFrame:
    """Function that Uses sklearns VarianceThreshold method to drop features that have less variance than the threshold

    :param df: Input data with numeric variables although there is a check on numeric variables in the function.
    :type df: pd.DataFrame
    :return: the dataframe without the zero-variance variables
    :rtype: pd.DataFrame
    """

    df_include = df.select_dtypes(include=["int64", "float64"])
    df_exclude = df.select_dtypes(exclude=["int64", "float64"])

    selector = VarianceThreshold()
    selector.fit(df_include)

    nzv_return = df_include[df_include.columns[selector.get_support(indices=True)]]
    df_return = pd.concat([nzv_return, df_exclude], axis=1, sort=False)

    return df_return


def scale_features(x_train: pd.DataFrame) -> pd.DataFrame:
    """Transforms the features so it expresses the amount of standard deviations the value is removed from the mean

    :param x_train: dataframe with all the independent variables (features) of the train set
    :type x_train: pd.DataFrame
    :return: dataframe with all the scaled independent variables (features) of the train set
    :rtype: pd.DataFrame
    """

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_train_scaled = pd.DataFrame(x_train_scaled, columns=x_train.columns)

    return x_train_scaled


def fit_trend_model(
    df: pd.DataFrame, target_col: str, train_size: float
) -> BaseEstimator:
    """This function fits a trend model that can later be used for correction.

    :param df: dataFrame including the target of the trend model
    :type df: pd.DataFrame
    :param target_col: the name of the column the trend model should be fitted for
    :type target_col: str
    :param train_size: float between 0 and 1 that determines the percentage of records used for training the trend model
    :type train_size: float
    :return: a fitted model with an estimate of the sales trend
    :rtype: BaseEstimator
    """
    sorted_df = df.sort_values(target_col)
    n_train = round(df.shape[0] * train_size)
    # Select the training samples from the target.
    trend_target = sorted_df[target_col].iloc[: int(n_train)].reset_index(drop=True)
    # Set the trend parameter equal to a list from 1 to number of rows of the df.
    trend_features = pd.DataFrame(list(range(1, n_train + 1)), columns=["trend"])
    # Add a constant to the features.
    trend_features = sm.add_constant(trend_features)
    # Return the fit.
    model = sm.OLS(trend_target, trend_features)
    return model.fit()


def correct_trends(
    df: pd.DataFrame,
    timestamp_col: str,
    target: str,
    fit_trend_model: object,
) -> pd.DataFrame:
    """This function uses the fitted trend model to correct the target variable for this trend.

    :param df: a dataframe that contains at least a timestamp column and a target variable
    :type df: pd.DataFrame
    :param timestamp_col: column name that represents the datetime
    :type timestamp_col: str
    :param target: the target variable of the trend model
    :type target: str
    :param fit_trend_model: a function that fits the trend model
    :type fit_trend_model: object
    :return: the df with the trend corrected
    :rtype: pd.DataFrame
    """
    # Fit the regression
    fit = fit_trend_model
    # Only apply the correction if the trend is significant
    if abs(fit.tvalues["trend"]) > 2:
        # Calculate the trend growth.
        trend_growth = round(fit.params["trend"] / df[target].mean(), 6) * 100
        # Apply trend correction
        df.reset_index(inplace=True)
        df[target + "_corrected"] = df[target] - (
            fit.params["const"] + (df.index + 1) * fit.params["trend"]
        )
        df.set_index("index", inplace=True)
        _logger.info(
            "The {target} has a significant trend with relative growth of {trend}.".format(
                target=target, trend=trend_growth
            )
        )
        df.sort_values(timestamp_col, inplace=True, ascending=False)
    else:
        # Apply no correction if there is no trend.
        df[target + "_corrected"] = df[target]
        _logger.info("The {target} has no significant trend.".format(target=target))
    return df


def duplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    """This function duplicates each row in a dataframe

    :param df: dataframe
    :type df: pd.DataFrame
    :return: a dataframe with duplicated rows
    :rtype: pd.DataFrame
    """
    cols = df.columns
    df = pd.DataFrame(np.repeat(df.values, 2, axis=0), columns=cols)
    return df


def over_under_sampling(
    X_train: np.ndarray, y_train: np.ndarray, method: str = "ros"
) -> Tuple[np.ndarray, np.ndarray]:
    """To find out which method best suits your model use the function "sampling_roc" in explore_functions.py in the explore folder.

    - RandomOverSampler: picking samples at random with replacement.
    - SMOTE: takes each minority sample and introduces synthetic data points connecting the minority sample and its nearest neighbors.
        Neighbors from the k nearest neighbors are chosen randomly.
    - ADASYN: similar to SMOTE, but it generates different number of samples depending on
        an estimate of the local distribution of the class to be oversampled.
    - RandomUnderSampler: randomly picks data points from the majority class.
    - nearmiss_1: selects the positive samples for which the average distance to
        the N closest samples of the negative class is the smallest.
    - nearmiss_2: selects the positive samples for which the average distance to
        the N farthest samples of the negative class is the smallest.
    - nearmiss_3: a 2-steps algorithm. First, for each negative sample, their M nearest-neighbors will be kept.
        Then, the positive samples selected are the one for which the average distance to the N nearest-neighbors is the largest.

    :param X_train: features to predict the target variable
    :type X_train: np.ndarray
    :param y_train: type of over or under sampling to use
    :type y_train: np.ndarray
    :param method: oversampling method, defaults to "ros"
    :type method: str, optional
    :return: resampled version of X_train and y_train
    :rtype: Tuple[np.ndarray, np.ndarray]
    """

    if method == "ros":
        sample_method = RandomOverSampler(random_state=42)
    if method == "smote":
        sample_method = SMOTE(random_state=42)
    if method == "adasyn":
        sample_method = ADASYN(random_state=42)
    if method == "rus":
        sample_method = RandomUnderSampler(random_state=42)
    if method == "nearmiss_1":
        sample_method = NearMiss(version=1)
    if method == "nearmiss_2":
        sample_method = NearMiss(version=2)
    if method == "nearmiss_3":
        sample_method = NearMiss(version=3)
    X_train, y_train = sample_method.fit_resample(X_train, y_train)
    return X_train, y_train
