"""
This module contains functionalities specific for setting up your model.

Functions included:
- get_preprocessor
- get_estimator
- get_params
- split_data
- construct_model
"""

import copy
import logging
import os
from functools import partial
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from box import Box
from hyperopt import STATUS_OK, Trials, fmin, hp, tpe
from lightgbm import LGBMClassifier, LGBMRegressor
from myautoml.evaluation.binary_classifier import get_plots
from myautoml.utils.hyperopt import flatten_params, prep_params
from myautoml.utils.model import make_pipeline
from sklearn.base import BaseEstimator, is_classifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.compose import make_column_selector as selector
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import IterativeImputer, KNNImputer, SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    explained_variance_score,
    f1_score,
    log_loss,
    mean_squared_error,
    median_absolute_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from typing_extensions import Literal

_logger = logging.getLogger(__name__)


def get_preprocessor(config: Box) -> ColumnTransformer:
    """Define the transformations made for numerical and categorical features.
    For numeric columns (i.e. not "category" or "object") the imputation method is
    defined using the sklearn.impute.SimpleImputer using the 'numeric_strategy' which
    can be one of 'mean', 'median', 'most_frequent' or 'constant'. If 'constant' is
    used, make sure the numeric_fill_value is defined. The scaling method is defined
    using the sklearn.preprocessing.StandardScaler which standardizes features by
    removing the mean and scaling to unit variance.

    For categorical columns (i.e. 'category') the imputation method is defined using
    the sklearn.impute.SimpleImputer using the 'categorical_strategy' which
    can be one of 'most_frequent' or 'constant'. If 'constant' is
    used, make sure the categorical_fill_value is defined. The encoding method can be
    defined as a combination of sklearn.preprocessing.OrdinalEncoder which converts the features
    to ordinal integers, resulting in a single column of integers per feature
    or the sklearn.preprocessing.OneHotEncoder which creates a binary column for each
    category.
    Example:
    preprocessor = get_preprocessor()
    preprocessor.fit(x_train, y_train)

    :param config: configuration file that includes properties for the imputation and encoding strategy
    :type config: Box
    :return: Column transformer that imputes missing data
    :rtype: ColumnTransformer
    """

    _logger.info("Constructing the preprocessor")

    if config.impute.numeric_strategy == "KNN":
        _logger.warning(
            "Imputing missing numeric data using KNNImputer. This might take a long time dependent on the size of your dataset"
        )
        numeric_transformer = Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("imputer", KNNImputer(n_neighbors=config.impute.knn_neighbors)),
            ]
        )
        # todo: kunnen we een subsample meegeven?
    elif config.impute.numeric_strategy == "iterative":
        _logger.warning(
            "Imputing missing numeric data using IterativeImputer. This might take a long time dependent on the size of your dataset"
        )
        numeric_transformer = Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("imputer", IterativeImputer(random_state=42)),
            ]
        )
    else:
        numeric_transformer = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(
                        strategy=config.impute.numeric_strategy,
                        fill_value=config.impute.numeric_fill_value,
                    ),
                ),
                ("scaler", StandardScaler()),
            ]
        )

    # Unless explicitly indicated otherwise in the config, ordinal encoder is used for all categorical features,
    categorical_transformer_ordinal = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy=config.impute.categorical_strategy,
                    fill_value=config.impute.categorical_fill_value,
                ),
            ),
            ("ord_enc", OrdinalEncoder()),
        ]
    )

    categorical_transformer_one_hot = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy=config.impute.categorical_strategy,
                    fill_value=config.impute.categorical_fill_value,
                ),
            ),
            ("ord_enc", OneHotEncoder()),
        ]
    )

    numeric_features = selector(dtype_exclude=["category", "object"])
    transformers = [
        ("num", numeric_transformer, numeric_features),
    ]

    categorical_features = selector(dtype_include=["category", "object"])

    if config.encode.default_strategy == "ordinal":
        # All categorical features are ordinally encoded. This includes features that should be one hot encoded.
        categorical_features_ordinal = categorical_features
        transformers.append(
            ("cat1", categorical_transformer_ordinal, categorical_features_ordinal)
        )

        # Features that should be one hot encoded are also one hot encoded.
        # Note that ordinal encoding and one hot encoding simultaneously is equivalent to only one hot encoding.
        categorical_features_one_hot = config.encode.features_one_hot
        if len(categorical_features_one_hot) > 0:
            _logger.info(
                f"The following features will be one-hot encoded: {categorical_features_one_hot}"
            )
            transformers.append(
                ("cat2", categorical_transformer_one_hot, categorical_features_one_hot)
            )

    elif config.encode.default_strategy == "one_hot":
        # All categorical features are one hot encoded.
        # We currently do not support an option to exclude features that should be ordinally encoded.
        categorical_features_one_hot = categorical_features
        transformers.append(
            ("cat1", categorical_transformer_one_hot, categorical_features_one_hot)
        )

    else:
        _logger.warning(
            "A correct default encoding strategy should be defined. Currently supported strategies are 'ordinal' and 'one_hot'"
        )

    preprocessor = ColumnTransformer(transformers=transformers, remainder="passthrough")

    return preprocessor


def get_estimator(
    estimator_type: Literal[
        "LGBMClassifier",
        "RandomForestClassifier",
        "KNeighborsClassifier",
        "RandomForestRegressor",
        "KNeighborsRegressor",
        "LGBMRegressor",
    ],
    calibrate_model: bool = False,
    **params,
) -> Tuple[BaseEstimator, dict]:
    """Constructs an estimator of the requested type with corresponding hyperparameters.
    If no hyperparameters are specified, an estimator with default values is constructed.

    :param estimator_type: one of "LGBMClassifier", "RandomForestClassifier", "KNeighborsClassifier", "RandomForestRegressor",
        "KNeighborsRegressor" or "LGBMRegressor"
    :type estimator_type: Literal
    :param calibrate_model: indicate if classifier should be calibrated, defaults to False
    :type calibrate_model: bool, optional
    :return: a (possibly calibrated) model with the hyperparameters as specified in **params and corresponding tags
    :rtype: Tuple[BaseEstimator, dict]
    """

    if estimator_type == "LGBMClassifier":
        estimator = LGBMClassifier(**params)
        estimator_tags = {"module": "lightgbm", "class": "LGBMClassifier"}
    elif estimator_type == "RandomForestClassifier":
        estimator = RandomForestClassifier(**params)
        estimator_tags = {"module": "ensemble", "class": "RandomForestClassifier"}
    elif estimator_type == "KNeighborsClassifier":
        estimator = KNeighborsClassifier(**params)
        estimator_tags = {"module": "neighbors", "class": "KNeighborsClassifier"}
    elif estimator_type == "LGBMRegressor":
        estimator = LGBMRegressor(**params)
        estimator_tags = {"module": "lightgbm", "class": "LGBMRegressor"}
    elif estimator_type == "RandomForestRegressor":
        estimator = RandomForestRegressor(**params)
        estimator_tags = {"module": "ensemble", "class": "RandomForestRegressor"}
    elif estimator_type == "KNeighborsRegressor":
        estimator = KNeighborsRegressor(**params)
        estimator_tags = {"module": "neighbors", "class": "KNeighborsRegressor"}
    else:
        _logger.warning("a correct estimator should be defined")
        estimator = {}
        estimator_tags = {}

    if is_classifier and calibrate_model:
        estimator = CalibratedClassifierCV(base_estimator=estimator, cv=5)

    return estimator, estimator_tags


def get_params(
    estimator_type: Literal[
        "LGBMClassifier",
        "RandomForestClassifier",
        "KNeighborsClassifier",
        "RandomForestRegressor",
        "KNeighborsRegressor",
        "LGBMRegressor",
    ],
) -> dict:
    """Defines the parameter search space for the requesting estimator.
    The search space consists of, for every hyperparameter:
    a lower bound, an upper bound, a prior distribution and possibly a step size.

    :param estimator_type: one of "LGBMClassifier", "RandomForestClassifier", "KNeighborsClassifier", "RandomForestRegressor",
        "KNeighborsRegressor" or "LGBMRegressor"
    :type estimator_type: Literal
    :return: The search space of the estimator
    :rtype: dict
    """

    if estimator_type == "LGBMClassifier" or estimator_type == "LGBMRegressor":
        search_space = {
            "boosting_type_choice": hp.choice(
                "boosting_type_choice",
                [
                    {
                        "boosting_type": "gbdt",
                        "subsample": hp.uniform("gdbt_subsample", 0.5, 1),
                    },
                    {
                        "boosting_type": "dart",
                        "subsample": hp.uniform("dart_subsample", 0.5, 1),
                    },
                    {"boosting_type": "goss", "subsample": 1.0},
                ],
            ),
            "num_leaves": hp.qloguniform("num_leaves", np.log(3), np.log(100), 1),
            # hp.quniform('num_leaves', 4, 64, 1)
            "learning_rate": hp.loguniform("learning_rate", np.log(0.005), np.log(0.5)),
            "subsample_for_bin": hp.qloguniform(
                "subsample_for_bin", np.log(20000), np.log(300000), 20000
            ),
            "min_child_samples": hp.qloguniform(
                "min_child_samples", np.log(20), np.log(500), 5
            ),
            # default min is 20, max set to 500
            "reg_alpha": hp.uniform("reg_alpha", 0.0, 1.0),
            "reg_lambda": hp.uniform("reg_lambda", 0.0, 1.0),
            "colsample_bytree": hp.uniform("colsample_by_tree", 0.6, 1.0),
            "is_unbalance": hp.choice("is_unbalance", [True, False]),
            # 'scale_pos_weight': 20,
            "max_depth": hp.qloguniform("max_depth", np.log(2), np.log(500), 1),
        }
    elif estimator_type == "RandomForestClassifier":
        search_space = {
            "n_estimators": hp.quniform("n_estimators", 50, 200, 1),
            # The number of trees in the forest
            "criterion": hp.choice("criterion", ["gini", "entropy"]),
            "max_depth": hp.qloguniform("max_depth", np.log(2), np.log(500), 1),
            # The maximum depth of the tree
            "min_samples_split": hp.qloguniform(
                "min_samples_split", np.log(2), np.log(500), 1
            ),
            # The minimum number of samples required
            # to split an internal node
            "min_samples_leaf": hp.quniform("min_samples_leaf", 1, 10, 1),
            # The minimum number of samples required to
            # be at a leaf node
            "bootstrap": hp.choice("bootstrap", [True, False]),
            # Whether bootstrap samples are used when
            # building trees
            "max_features": hp.choice("max_features", ["auto", "sqrt"]),
            # The number of features to consider when
            # looking for the best split
        }
    elif estimator_type == "RandomForestRegressor":
        search_space = {
            "n_estimators": hp.quniform("n_estimators", 50, 200, 1),
            # The number of trees in the forest
            "criterion": hp.choice(
                "criterion", ["squared_error", "absolute_error", "poisson"]
            ),
            "max_depth": hp.qloguniform("max_depth", np.log(2), np.log(500), 1),
            # The maximum depth of the tree
            "min_samples_split": hp.qloguniform(
                "min_samples_split", np.log(2), np.log(500), 1
            ),
            # The minimum number of samples required
            # to split an internal node
            "min_samples_leaf": hp.quniform("min_samples_leaf", 1, 10, 1),
            # The minimum number of samples required to
            # be at a leaf node
            "bootstrap": hp.choice("bootstrap", [True, False]),
            # Whether bootstrap samples are used when
            # building trees
            "max_features": hp.choice("max_features", ["auto", "sqrt"]),
            # The number of features to consider when looking for the best split
        }

    elif (
        estimator_type == "KNeighborsClassifier"
        or estimator_type == "KNeighborsRegressor"
    ):
        search_space = {
            "n_neighbors": hp.quniform("n_neighbors", 2, 20, 1),
            "weights": hp.choice("weights", ["uniform", "distance"]),
            "algorithm": hp.choice(
                "algorithm", ["auto", "ball_tree", "kd_tree", "brute"]
            ),
            "leaf_size": hp.qloguniform("leaf_size", np.log(5), np.log(100), 1),
            "metric": hp.choice("metric", ["minkowski", "manhattan", "euclidean"]),
        }

    else:
        _logger.warning("a correct estimator should be defined")
        search_space = {}
        pass

    return search_space


# TODO make n_dates (optionally) proportional
def split_data(
    x: pd.DataFrame,
    y: pd.Series,
    config: Box,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, pd.Series]:
    """Splits x and y into a train and test set. Uses normal (random) train-test split by
    default. When out_of_time_testing in config is set to true, the latest date(s) from
    config.time_column_name is used as the test set and all the others as the train set.

    :param x: features
    :type x: pd.DataFrame
    :param y: dependent variable
    :type y: pd.Series
    :param config: configuration file
    :type config: Box
    :return: train-test split of inputs.
    :rtype: Tuple[np.ndarray, np.ndarray, np.ndarray, pd.Series]
    """
    # Size of the test dataset, defaults to 0.2
    test_size = config.percentage if hasattr(config, "percentage") else 0.2
    # Whether to use out-of-time testing, defaults to False
    test_oot = (
        config.out_of_time_testing if hasattr(config, "out_of_time_testing") else False
    )
    # Name of the column that contains the time dimension, defaults to None
    time_column_name = (
        config.time_column_name if hasattr(config, "time_column_name") else None
    )
    # Number of dates to assign to the test set, defaults to 1
    n_dates = config.n_dates if hasattr(config, "n_dates") else 1

    if not test_oot:
        _logger.info("Performing normal train test split (not OOT)")

        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=test_size, random_state=234
        )
    else:
        x_tmp = x  # .reset_index()
        y_tmp = y  # .reset_index()
        x_tmp[time_column_name] = pd.to_datetime(
            x_tmp[time_column_name], format="%Y%m%d"
        )
        _logger.info(
            f"Performing train test split for OOT testing. OOT snapshot date: "
            f"{time_column_name}"
        )
        test_dates = list(
            pd.to_datetime(
                x_tmp.sort_values([time_column_name], ascending=True)
                .tail(n_dates)["dates"]
                .values,
                format="%Y%m%d",
            )
        )
        test_set = x_tmp[time_column_name].isin(test_dates)

        x_test = x_tmp[test_set]
        y_test = y_tmp[test_set]
        x_train = x_tmp[~test_set]
        y_train = y_tmp[~test_set]

    return x_train, x_test, y_train, y_test


def get_regression_metrics(
    model: BaseEstimator, data: dict, evaluation_metrics: list, prefix: str = None
) -> dict:
    """ "This function is called in function 'evaluate_regressor'".
    Calculates a set of metrics for a regression model

    :param model: trained regression model
    :type model: BaseEstimator
    :param data: data separated over the features (X) and the target (y) and over a train and test set
    :type data: dict
    :param config: set of metrics
    :type config: list
    :param prefix: prefix for the metric name, defaults to None
    :type prefix: str, optional
    :return: calculated metrics
    :rtype: dict
    """

    _logger.debug("Starting computing the metrics")
    if prefix is None:
        prefix = ""
    elif len(prefix) > 0 and (not prefix[-1:] == "_"):
        prefix = prefix + "_"

    metrics = {}
    for label in data.keys():
        x = data[label]["x"]
        y_true = data[label]["y"]
        y_pred = data[label]["y_pred"] = model.predict(x)

        if "r2" in evaluation_metrics:
            metrics[f"{prefix}r2_score_{label}"] = r2_score(y_true, y_pred)

        if "explained_variance" in evaluation_metrics:
            metrics[f"{prefix}explained_variance_score_{label}"] = (
                explained_variance_score(y_true, y_pred)
            )

        if "neg_mean_squared_error" in evaluation_metrics:
            metrics[f"{prefix}neg_mean_squared_error_{label}"] = mean_squared_error(
                y_true, y_pred
            )

        if "neg_median_absolute_error" in evaluation_metrics:
            metrics[f"{prefix}neg_median_absolute_error_{label}"] = (
                median_absolute_error(y_true, y_pred)
            )

    return metrics


def get_classification_metrics(
    model: BaseEstimator, data: dict, evaluation_metrics: list, prefix: str = None
) -> dict:
    """ "This function is called in function 'evaluate_binary_classifier'".
    Calculates a set of metrics for a classification model

    :param model: trained classification model
    :type model: BaseEstimator
    :param data: data separated over the features (X) and the target (y) and over a train and test set
    :type data: dict
    :param config: set of metrics
    :type config: list
    :param prefix: prefix for the metric name, defaults to None
    :type prefix: str, optional
    :return: calculated metrics
    :rtype: dict
    """

    _logger.debug("Starting computing the metrics")
    if prefix is None:
        prefix = ""
    elif len(prefix) > 0 and (not prefix[-1:] == "_"):
        prefix = prefix + "_"

    metrics = {}
    for label in data.keys():
        x = data[label]["x"]
        y_true = data[label]["y"]
        y_pred = data[label]["y_pred"] = model.predict(x)
        y_pred_proba = data[label]["y_pred_proba"] = model.predict_proba(x)[:, 1]

        if "accuracy" in evaluation_metrics:
            metrics[f"{prefix}accuracy_{label}"] = accuracy_score(y_true, y_pred)

        if "roc_auc" in evaluation_metrics:
            metrics[f"{prefix}roc_auc_{label}"] = roc_auc_score(y_true, y_pred_proba)

        if "average_precision" in evaluation_metrics:
            metrics[f"{prefix}average_precision_{label}"] = average_precision_score(
                y_true, y_pred_proba
            )

        if "f1" in evaluation_metrics:
            metrics[f"{prefix}f1_{label}"] = f1_score(y_true, y_pred)

        if "precision" in evaluation_metrics:
            metrics[f"{prefix}precision_{label}"] = precision_score(y_true, y_pred)

        if "recall" in evaluation_metrics:
            metrics[f"{prefix}recall_{label}"] = recall_score(y_true, y_pred)

        if "neg_brier_score" in evaluation_metrics:
            metrics[f"{prefix}neg_brier_score_{label}"] = brier_score_loss(
                y_true, y_pred
            )

        if "neg_log_loss" in evaluation_metrics:
            metrics[f"{prefix}neg_log_loss_{label}"] = log_loss(y_true, y_pred)

        if "confusion_matrix" in evaluation_metrics:
            tn, fp, fn, tp = confusion_matrix(y_true=y_true, y_pred=y_pred).ravel()
            metrics[f"{prefix}confusion_matrix_true_negatives_{label}"] = tn
            metrics[f"{prefix}confusion_matrix_true_positives_{label}"] = tp
            metrics[f"{prefix}confusion_matrix_false_negatives_{label}"] = fn
            metrics[f"{prefix}confusion_matrix_false_positives_{label}"] = fp

    return metrics


def evaluate_binary_classifier(
    model: BaseEstimator, data: dict, temp_dir: Path, config: Box, plots: bool = False
) -> dict:
    """Calculates metrics and generates plots for the evaluation of a binary classification model

    :param model: trained binary classification model
    :type model: BaseEstimator
    :param data: data separated over the features (X) and the target (y) and over a train and test set
    :type data: dict
    :param temp_dir: local directory to save the plots
    :type temp_dir: Path
    :param config: configuration file
    :type config: Box
    :param plots: denoting whether any plots are saved in the local directory, defaults to False
    :type plots: bool, optional
    :return: two dictionaries containing the calculated metrics and the generated artifacts
    :rtype: dict
    """

    _logger.debug("Starting evaluation for binary classifier")

    metrics = get_classification_metrics(model, data, config.metrics.evaluation_metrics)

    _logger.debug("Starting cross-validation for binary classifier")

    cv_metrics = config.metrics.evaluation_metrics
    # confusion matrix is not a metric for cross-validation
    if "confusion_matrix" in cv_metrics:
        cv_metrics.remove("confusion_matrix")

    cv_results = cross_validate(
        estimator=model,
        X=data["train"]["x"],
        y=data["train"]["y"],
        scoring=cv_metrics,
        cv=config.training.nr_of_cv_folds,
    )

    for scorer in config.metrics.evaluation_metrics:
        metrics[f"{scorer}_cv"] = cv_results[f"test_{scorer}"].mean()

    if plots:
        plot_types = ["roc", "pr", "lift_deciles", "cum_precision", "distribution"]
        artifacts = get_plots(temp_dir, data, plots=plot_types, plot_path="evaluation")
    else:
        artifacts = {}

    print(f"{metrics=}")

    return metrics, artifacts


def evaluate_regressor(
    model: BaseEstimator, data: dict, temp_dir: Path, config: Box, plots: bool = False
) -> dict:
    """Calculates metrics and generates plots for the evaluation of a regression model

    :param model: trained regression model
    :type model: BaseEstimator
    :param data: data separated over the features (X) and the target (y) and over a train and test set
    :type data: dict
    :param temp_dir: local directory to save the plots
    :type temp_dir: Path
    :param config: configuration file
    :type config: Box
    :param plots: denoting whether any plots are saved in the local directory, defaults to False
    :type plots: bool, optional
    :return: two dictionaries containing the calculated metrics and the generated artifacts
    :rtype: dict
    """

    _logger.debug("Starting evaluation for regressor")

    metrics = get_regression_metrics(model, data, config.metrics.evaluation_metrics)

    _logger.debug("Starting cross-validation for regressor")
    cv_results = cross_validate(
        estimator=model,
        X=data["train"]["x"],
        y=data["train"]["y"],
        scoring=config.metrics.evaluation_metrics,
        cv=config.training.nr_of_cv_folds,
    )
    for scorer in config.metrics.evaluation_metrics:
        metrics[f"{scorer}_cv"] = cv_results[f"test_{scorer}"].mean()

    artifacts = {}
    if plots:
        # rename y_pred to y_pred_proba so it can be used by myautoml.get_plots
        # make a deep copy to not affect the naming of 'data'
        data_dummy = copy.deepcopy(data)
        a = data_dummy["train"]["y_pred"]
        b = data_dummy["test"]["y_pred"]
        del data_dummy["train"]["y_pred"]
        del data_dummy["test"]["y_pred"]
        data_dummy["train"]["y_pred_proba"] = a
        data_dummy["test"]["y_pred_proba"] = b

        plot_types = ["distribution"]
        artifacts = get_plots(
            temp_dir, data_dummy, plots=plot_types, plot_path="evaluation"
        )

    return metrics, artifacts


def train_run(
    estimator_params: dict,
    estimator_tags: dict,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: pd.Series,
    temp_dir: Path,
    config: Box,
) -> dict:
    """This function is called in function 'construct_model', either directly or with the use of the function 'hyperopt_objective'.
    A model is constructed given the provided hyperparameters of the estimator and evaluated based on a set of metrics.

    :param estimator_params: configuration of hyperparameters to construct an estimator
    :type estimator_params: dict
    :param estimator_tags: tags of the estimator, including the class, to construct an estimator
    :type estimator_tags: dict
    :param X_train: 2D array all the features of the train set
    :type X_train: np.ndarray
    :param y_train: 1D array with all the dependent variable of the train set
    :type y_train: np.ndarray
    :param X_test: 2D array with all the features of the test set
    :type X_test: np.ndarray
    :param y_test: series with all the dependent variable of the test set
    :type y_test: pd.Series
    :param temp_dir: local directory to save plots
    :type temp_dir: Path
    :param config: configuration file
    :type config: Box
    :return: dictionary containing the estimator and its corresponding tags, evaluated metrics and artifacts
    :rtype: dict
    """

    temp_dir.mkdir(parents=True, exist_ok=True)
    _logger.debug("Fitting the estimator")

    # construct an estimator with specified hyperpameters
    estimator, estimator_tags = get_estimator(
        estimator_tags["class"], config.calibration.calibrate, **estimator_params
    )
    estimator.fit(X_train, y_train)

    # evaluate the estimator
    if is_classifier(estimator):
        estimator_metrics, estimator_artifacts = evaluate_binary_classifier(
            model=estimator,
            data={
                "train": {"x": X_train, "y": y_train},
                "test": {"x": X_test, "y": y_test},
            },
            temp_dir=temp_dir,
            config=config,
            plots=config.explainability.evaluation_plots,
        )
    else:
        estimator_metrics, estimator_artifacts = evaluate_regressor(
            model=estimator,
            data={
                "train": {"x": X_train, "y": y_train},
                "test": {"x": X_test, "y": y_test},
            },
            temp_dir=temp_dir,
            config=config,
            plots=config.explainability.evaluation_plots,
        )

    return {
        "estimator": estimator,
        "estimator_tags": estimator_tags,
        "estimator_metrics": estimator_metrics,
        "estimator_artifacts": estimator_artifacts,
    }


def hyperopt_objective(
    search_params: dict,
    trials: Trials,
    preprocessor: ColumnTransformer,
    estimator_tags: dict,
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: pd.Series,
    config: Box,
) -> dict:
    """This function is called in function 'construct_model' when a search space is defined.
    It measures the objective value of a configuration of hyperparameters being tested by HyperOpt by training and evaluating
    a model and measuring the primary metric as defined in the config file.

    :param search_params: the configuration of hyperparameters to evaluate
    :type search_params: dict
    :param trials: Class that represents all of the completed, in-progress, and scheduled evaluation points from the fmin call
    :type trials: Trials
    :param preprocessor: preprocessor for the model
    :type preprocessor: ColumnTransformer
    :param estimator_tags: tags of the estimator, including the class, to construct an estimator
    :type estimator_tags: dict
    :param X_train: 2D array with all the features of the train set
    :type X_train: np.ndarray
    :param X_test: 2D array with all the features of the test set
    :type X_test: np.ndarray
    :param y_train: 1D array with all the dependent variable of the train set
    :type y_train: np.ndarray
    :param y_test: series with all the dependent variable of the test set
    :type y_test: pd.Series
    :param config: configuration file
    :type config: Box
    :return: dictionary that is saved for every function call in class Trials containing
        the objective value of the configuration and model specifications
    :rtype: dict
    """

    run_name = str(
        len(trials) - 1
    )  # the run_name is used to create subdirectories in the out/hyperopt folder
    _logger.debug("Evaluating the objective value of the hyperparameter configuration")
    estimator_params = {}
    temp_dir = os.path.dirname(__file__) + "/../../out/hyperopt/"

    ho_params = {}
    ho_tags = {}
    ho_metrics = {}
    ho_artifacts = {}

    search_params = flatten_params(search_params)
    search_params = prep_params(search_params)
    ho_estimator_params = estimator_params.copy()
    ho_estimator_params.update(search_params)

    ho_estimator = train_run(
        estimator_params=ho_estimator_params,
        estimator_tags=estimator_tags,
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        temp_dir=Path(temp_dir + "/" + str(run_name)),
        config=config,
    )

    ho_model = make_pipeline(preprocessor, ho_estimator["estimator"])
    ho_params.update({f"estimator_{k}": v for k, v in ho_estimator_params.items()})
    ho_tags.update(
        {f"estimator_{k}": v for k, v in ho_estimator["estimator_tags"].items()}
    )
    ho_metrics.update(ho_estimator["estimator_metrics"])
    ho_artifacts.update(ho_estimator["estimator_artifacts"])
    ho_tags["hyperopt"] = True

    # the objective value to optimize is the primary metric as defined in the config.
    # This metric must be included in the list of metrics generated in 'train_run'.
    if config.metrics.optimization_metric not in ho_metrics:
        _logger.warning(
            f"The primary metric '{config.metrics.optimization_metric}' as specified \
                        in the config file is not present in the list of metrics. \
                        Available metrics are: {ho_metrics.keys()}"
        )

    # todo: loss functie aanpassen zodat ook metrics niet in interval [0,1] werken (vb: mse voor regressie)
    loss = 1 - ho_metrics[config.metrics.optimization_metric]

    return {
        "loss": loss,
        "status": STATUS_OK,
        "model": ho_model,
        "params": ho_params,
        "tags": ho_tags,
        "metrics": ho_metrics,
        "artifacts": ho_artifacts,
    }


def construct_model(
    preprocessor: ColumnTransformer,
    estimator_tags: dict,
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: pd.Series,
    config: Box,
    search_space: dict = None,
) -> dict:
    """Fits an estimator and constructs a model based on the preprocessor and the fitted estimator.
    If a search space is defined, hyperparameter optimization is applied and the estimator with
    the hyperparameters that yielded the best performance is returned.

    :param preprocessor: preprocessor for the model
    :type preprocessor: ColumnTransformer
    :param estimator_tags: tags of the estimator, including the class, to construct an estimator
    :type estimator_tags: dict
    :param X_train: 2D array with all the features of the train set
    :type X_train: np.ndarray
    :param X_test: 2D array with all the features of the test set
    :type X_test: np.ndarray
    :param y_train: 1D array with all the dependent variable of the train set
    :type y_train: np.ndarray
    :param y_test: series with all the dependent variable of the test set
    :type y_test: pd.Series
    :param config: configuration file
    :type config: Box
    :param search_space: hyperparameter search space, defaults to None
    :type search_space: dict, optional
    :return: dictionary containing the model and its corresponding hyperparameters, tags, metrics and artifacts
    :rtype: dict
    """

    _logger.info(f"Constructing a {estimator_tags['class']} using default values")

    if search_space is None:
        _logger.debug("Constructing estimator with default hyperparameter values")
        estimator_params = {}
        estimator_dict = train_run(
            estimator_params=estimator_params,
            estimator_tags=estimator_tags,
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            temp_dir=Path(os.path.dirname(__file__) + "/../../out/hyperopt/"),
            config=config,
        )

        model = make_pipeline(preprocessor, estimator_dict["estimator"])
        params = {f"estimator_{k}": v for k, v in estimator_params.items()}
        tags = {
            f"estimator_{k}": v for k, v in estimator_dict["estimator_tags"].items()
        }
        metrics = estimator_dict["estimator_metrics"]
        artifacts = estimator_dict["estimator_artifacts"]

    else:
        trials = Trials()
        _logger.debug(
            f"Finding the best hyperparameter configuration over {config.training.hyperopt.max_nr_of_trials} iterations"
        )

        # The 'partial' function allows passing of additional variables to hyperopt_objective that are not part of the search space
        test_hyperopt_objective = partial(
            hyperopt_objective,
            trials=trials,
            preprocessor=preprocessor,
            estimator_tags=estimator_tags,
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test,
            config=config,
        )

        try:
            fmin(
                fn=test_hyperopt_objective,
                space=search_space,
                algo=tpe.suggest,
                trials=trials,
                max_evals=config.training.hyperopt.max_nr_of_trials,
                timeout=config.training.hyperopt.search_timeout_in_seconds,
                verbose=config.training.hyperopt.verbose,
                # rstate=np.random.RandomState(1), # todo: gebruik hiervan geeft error. moet wel een rstate hebben voor reproducibility.
                show_progressbar=False,
            )
        except KeyboardInterrupt:
            _logger.warning("User interrupted hyperopt optimisation")

        # the model that is returned is the model from trials that attained the largest objective value
        model = trials.best_trial["result"]["model"]
        params = trials.best_trial["result"]["params"]
        tags = trials.best_trial["result"]["tags"]
        metrics = trials.best_trial["result"]["metrics"]
        artifacts = trials.best_trial["result"]["artifacts"]

    return {
        "model": model,
        "params": params,
        "tags": tags,
        "metrics": metrics,
        "artifacts": artifacts,
    }
