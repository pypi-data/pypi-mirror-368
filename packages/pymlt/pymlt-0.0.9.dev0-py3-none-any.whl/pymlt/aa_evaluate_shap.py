"""
This module contains a collection of functions to estimate SHAP values of the features used in a fitted tree model.

Functions included:
- shap_analysis
- _save_shap_summary (helper function)
- _save_shap_summary_bar (helper function)
- _save_shap_dependence_plots (helper function)
"""

import logging
from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from myautoml.utils.sklearn import get_ct_feature_names
from sklearn.pipeline import Pipeline

_logger = logging.getLogger(__name__)


def shap_analysis(
    model: Pipeline, x: pd.DataFrame, temp_dir: Path, return_shap_details=False
) -> Tuple[dict, dict]:
    """Estimates the SHAP values of the features used in tree models and constructs summary
    plots. Makes use of three helper functions: _save_shap_summary, _save_shap_summary_bar,
    plots.

    :param model: trained ensemble tree model to analyse
    :type model: Pipeline
    :param x: dataframe consisting of the feature columns
    :type x: pd.DataFrame
    :param temp_dir: location to the directory to save the summary diagrams and
    :type temp_dir: Path
    :param return_shap_details: boolean whether to return additional detailed information, defaults to False
    :type return_shap_details: bool, optional
    :return: tags, artifacts. Returns additional information if 'return_shap_details' is
    set to true
    :rtype: Tuple[dict, dict]
    """
    temp_dir.mkdir(parents=True, exist_ok=True)
    _logger.info("Performing Shap analysis")
    shap_feature_names = get_ct_feature_names(model.steps[0][1])

    shap_estimator = model.steps[1][1]
    shap_data = model.steps[0][1].transform(x)

    shap_explainer = shap.TreeExplainer(shap_estimator)
    shap_values = shap_explainer.shap_values(shap_data)[1]

    # Computes the baseline value, i.e. expected average shape value for all customers
    tags = {"shap_expected_value": shap_explainer.expected_value[1]}

    shap_summary_path = _save_shap_summary(
        temp_dir, shap_values, shap_data, shap_feature_names
    )
    shap_summary_bar_path = _save_shap_summary_bar(
        temp_dir, shap_values, shap_data, shap_feature_names
    )
    shap_dependence_paths = _save_shap_dependence_plots(
        temp_dir, shap_values, shap_data, shap_feature_names
    )

    paths = [shap_summary_path, shap_summary_bar_path, *shap_dependence_paths]
    artifacts = {path: "shap" for path in paths}

    if return_shap_details:
        return (
            tags,
            artifacts,
            shap_explainer,
            shap_data,
            shap_values,
            shap_feature_names,
        )

    return tags, artifacts


def _save_shap_summary(
    save_dir: Path, shap_values: list, shap_data: np.array, shap_feature_names: list
) -> Path:
    """Plots a SHAP summary diagram

    :param save_dir: location to save the diagram
    :type save_dir: Path
    :param shap_values: a matrix (# samples x # features) of SHAP values
    :type shap_values: list
    :param shap_data: a matrix of samples (# samples x # features) on which to explain the model's output
    :type shap_data: np.array
    :param shap_feature_names: names of the features
    :type shap_feature_names: list
    :return: path to the location of the summary diagram
    :rtype: Path
    """
    _logger.debug("Plotting Shap summary diagram")
    save_path = Path(save_dir) / "shap_summary.png"
    shap.summary_plot(
        shap_values, shap_data, show=False, feature_names=shap_feature_names
    )
    fig = plt.gcf()
    fig.set_figwidth(10)
    fig.set_figheight(5)
    fig.savefig(save_path, bbox_inches="tight")
    plt.close(fig)
    return save_path


def _save_shap_summary_bar(
    save_dir: Path, shap_values: list, shap_data: np.array, shap_feature_names: list
) -> Path:
    """Plots a SHAP summary bar diagram

    :param save_dir: location to save the diagram
    :type save_dir: Path
    :param shap_values: a matrix (# samples x # features) of SHAP values
    :type shap_values: list
    :param shap_data: a matrix of samples (# samples x # features) on which to explain the model's output
    :type shap_data: np.array
    :param shap_feature_names: names of the features
    :type shap_feature_names: list
    :return: path to the location of the summary diagram
    :rtype: Path
    """
    _logger.debug("Plotting Shap summary bar diagram")
    save_path = Path(save_dir) / "shap_summary_bar.png"
    shap.summary_plot(
        shap_values,
        shap_data,
        plot_type="bar",
        show=False,
        feature_names=shap_feature_names,
    )
    fig = plt.gcf()
    fig.set_figwidth(10)
    fig.set_figheight(5)
    fig.savefig(save_path, bbox_inches="tight")
    plt.close(fig)
    return save_path


def _save_shap_dependence_plots(
    save_dir: Path, shap_values: list, shap_data: np.array, shap_feature_names: list
) -> list:
    """Plots dependence plots for each variable in the model

    :param save_dir: location to save the diagram
    :type save_dir: Path
    :param shap_values: a matrix (# samples x # features) of SHAP values
    :type shap_values: list
    :param shap_data: a matrix of samples (# samples x # features) on which to explain the model's output
    :type shap_data: np.array
    :param shap_feature_names: names of the features
    :type shap_feature_names: list
    :return: a list of paths to the locations of the dependence plots
    :rtype: list
    """
    save_paths = []
    for col in shap_feature_names:
        _logger.debug(f"Plotting dependence plot for {col}")
        save_path = Path(save_dir) / f"shap_dependence_{col}.png"
        shap.dependence_plot(
            ind=col,
            shap_values=shap_values,
            features=shap_data,
            interaction_index=None,
            show=False,
            feature_names=shap_feature_names,
        )
        fig = plt.gcf()
        fig.set_figwidth(10)
        fig.set_figheight(5)
        plt.axhline(y=0, color="black", linestyle="--", alpha=0.4)
        fig.savefig(save_path, bbox_inches="tight")
        plt.close(fig)
        save_paths.append(save_path)
    return save_paths
