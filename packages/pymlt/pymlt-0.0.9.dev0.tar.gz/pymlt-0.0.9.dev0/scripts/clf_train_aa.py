"""
Script to train a classification model for {{ cookiecutter.project_name }}
"""

import logging
import os
import sys
from pathlib import Path

import mlflow
import numpy as np
from box import Box
from dotenv import find_dotenv, load_dotenv
from envyaml import EnvYAML
from sklearn.datasets import load_breast_cancer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time

from src.evaluate import (
    evaluate_grafana_functions,
    evaluate_model_functions,
    evaluate_shap_functions,
)
from src.explore import explore_functions
from src.model import model_functions
from src.transform import transform_functions

from src import utils

# set working directory
# os.chdir("{{cookiecutter.project_slug}}")

# set logger
_logger = logging.getLogger(__name__)

# load env vars
load_dotenv(find_dotenv())

# construct box object with both env vars and config.yml vars
config = Box(
    EnvYAML(os.getenv("CONFIG_PATH_CLASSIFICATION"), include_environment=True).export()
)


def main():
    start_time = time.perf_counter() / 60
    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    grafana_metrics = {}
    grafana_metrics = evaluate_grafana_functions.get_grafana_metrics_config(
        grafana_metrics, config
    )

    # Load data
    df = load_breast_cancer(as_frame=True)["frame"]

    # Explore
    df = explore_functions.check_one_val_feature(df)

    sparse_features = explore_functions.check_sparse_features(df, threshold=0.75)

    # Transform
    df = transform_functions.redefine_missing_values(
        df, replace_values=[None], cols=df.columns
    )

    df = transform_functions.drop_missings(
        df, threshold=config.data.drop.missing_percentage
    )

    # Model
    # set X, y, split data
    X = df.drop(config.data.target, axis=1)
    y = df[config.data.target]

    X_train, X_test, y_train, y_test = model_functions.split_data(
        X, y, config=config.data.test_set
    )
    grafana_metrics = evaluate_grafana_functions.get_grafana_metrics_df_shape(
        grafana_metrics, y, df
    )

    # Use the preprocessor to impute the missing data and to encode the features
    preprocessor = model_functions.get_preprocessor(config=config.data)

    preprocessor.fit(X_train, y_train)

    X_train_unprepped = X_train.copy()
    X_test_unprepped = X_test.copy()
    X_train = preprocessor.transform(X_train)
    X_test = preprocessor.transform(X_test)

    # get estimator tags and search space
    _, estimator_tags = model_functions.get_estimator(
        estimator_type=config.training.estimator,
        calibrate_model=config.calibration.calibrate,
    )
    search_space = model_functions.get_params(estimator_type=config.training.estimator)

    # construct (and fit) the model
    # if the search space of the estimator is provided, hyperparameter optimization is included
    model_dict = model_functions.construct_model(
        preprocessor=preprocessor,
        estimator_tags=estimator_tags,
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        config=config,
        search_space=search_space,
    )

    # extract the fitted estimator for evaluation
    estimator = model_dict["model"]["estimator"]

    # Evaluate
    # get evaluation metrics for the trained model
    _logger.info(f"{model_dict['metrics']=}")
    evaluate_model_functions.feature_importance(estimator, X.columns)
    evaluate_model_functions.confusion_matrix(
        estimator, X_test, y_test, print_result=True
    )

    if config.explainability.shap_analysis:
        shap_tags, shap_artifacts = evaluate_shap_functions.shap_analysis(
            model=model_dict["model"],
            x=X_train_unprepped,
            temp_dir=Path("out") / "shap",
        )
        model_dict["tags"].update(shap_tags)
        model_dict["artifacts"].update(shap_artifacts)
    else:
        _logger.info("Shap analysis skipped")

    # add the feature columns as a tag
    model_dict["tags"].update({"feature_columns": list(X.columns)})

    # save the results in mlflow
    # utils.save_results_mlflow(config, model_dict)

    # save model metrics to grafana metrics
    grafana_metrics = evaluate_grafana_functions.get_grafana_metrics_model_performance(
        grafana_metrics, model_dict, X_test_unprepped, y_test
    )
    # save duration to grafana metrics
    end_time = time.perf_counter() / 60
    grafana_metrics.update({"duration_minutes": round(end_time - start_time)})
    grafana_metrics.update({"features": list(X.columns)})

    # store metrics to st_monitoring.metrics in PostGres DB
    utils.store_grafana_metrics(
        grafana_metrics, name=config.model.name, label="train_classification"
    )


if __name__ == "__main__":
    np.random.seed(1)
    main()
    _logger.info("Done")
