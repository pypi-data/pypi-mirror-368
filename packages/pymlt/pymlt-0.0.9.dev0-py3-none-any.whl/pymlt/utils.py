"""This module contains utility functions

functions included: cached, log_training_experiment"""

import importlib
import logging
import pickle
import shutil
from pathlib import Path
from typing import Callable

import mlflow
import requests
import yaml
from eneco.dsp_clients.monitoring.client import MonitoringClient
from myautoml.utils.mlflow.tracking import log_sk_model
from myautoml.utils.pickle import load_pickle, save_pickle
from yaml import safe_load

_logger = logging.getLogger(__name__)


def cached(func: Callable, cache_path: str):
    """
    This function uses 'func' to load a Dataframe and store it as a pickled file.
    If the 'cache_path' already exists, it loads the data from this path
    :param func: a function that loads a DataFrame
    :param cache_path: the file path to save / load the pickled file to/from
    :return: a DataFrame
    """
    if Path(cache_path).exists():
        return load_pickle(cache_path)
    else:
        result = func()
        save_pickle(result, cache_path)
        return result


# TODO: add pickle load and write
# TODO: read_csv


def save_training_result(
    config,
    save_root,
    model_to_save,
    hyperopt_trial_results,
    mlflow_params,
    mlflow_tags,
    mlflow_metrics,
    mlflow_artifacts,
):
    if config.save_results.mlflow:
        save_results_mlflow(
            config,
            model_to_save,
            hyperopt_trial_results,
            mlflow_params,
            mlflow_tags,
            mlflow_metrics,
            mlflow_artifacts,
        )

    if config.save_results.local:
        save_trial_results_locally(
            save_dir=save_root / "trial_results",
            formatted_trial_results=hyperopt_trial_results,
        )

        save_evaluation_metrics_locally(
            save_dir=save_root / "evaluation_metrics", formatted_metrics=mlflow_metrics
        )

        model_dir = save_root / "model"
        model_dir.mkdir(parents=True, exist_ok=True)
        save_model_artifact_locally(
            save_path=model_dir / "best_model.pkl", model_to_save=model_to_save
        )

        _logger.info("Trial results are saved locally at %s", save_root)
    else:
        _logger.info("Delete temporary folder %s.", save_root)
        shutil.rmtree(save_root)


def save_results_mlflow(config, model_dict):
    """Log training result in MLFlow to experiment"""

    _logger.info(
        "Log training result in MLFlow to experiment %s", config.experiment.name
    )
    mlflow.set_experiment(config.experiment.name)
    with mlflow.start_run():
        log_sk_model(
            sk_model=model_dict["model"],
            registered_model_name=config.model.name,
            params=model_dict["params"],
            tags=model_dict["tags"],
            metrics=model_dict["metrics"],
            artifacts=model_dict["artifacts"],
        )

        _logger.info(
            "Log training result in MLFlow to experiment %s", config.experiment.name
        )

        # mlflow.log_text(yaml.dump(hyperopt_trial_results), "trial_results.yaml")


def save_trial_results_locally(save_dir, formatted_trial_results):
    """Log training results locally"""
    _logger.info("Save training results to path %s", save_dir)

    save_dir.mkdir(parents=True, exist_ok=True)

    with open(save_dir / "hyperopt_trial_results.yaml", "w+") as result_file:
        yaml.dump(formatted_trial_results, result_file, allow_unicode=True)


def save_evaluation_metrics_locally(save_dir, formatted_metrics):
    """Log evaluation metrics locally"""
    _logger.info("Save evaluation metrics to path %s", save_dir)

    save_dir.mkdir(parents=True, exist_ok=True)

    with open(save_dir / "best_model_metrics.yaml", "w+") as result_file:
        yaml.dump(formatted_metrics, result_file, allow_unicode=True)


def save_model_artifact_locally(save_path, model_to_save):
    """Save best model and (optional) calibrated best model locally as .pkl file"""
    save_dir = save_path.parent
    save_dir.mkdir(parents=True, exist_ok=True)

    _logger.info("Save model artefact locally to path %s", save_path)

    with open(save_path, "wb") as file:
        pickle.dump(obj=model_to_save, file=file)


def get_model(run_id: str, model_path: str = "model"):
    # Determine how to load the model
    ml_model_url = f"{mlflow.get_tracking_uri()}/get-artifact?path={model_path}%2FMLmodel&run_id={run_id}"
    ml_model = safe_load(requests.get(ml_model_url).content)
    loader_module = ml_model["flavors"]["python_function"]["loader_module"]
    _logger.debug(f"Loader module for the model: {loader_module}")

    # Import the 'load_model' function
    load_model = getattr(importlib.import_module(loader_module), "load_model")

    # Load the model
    model = load_model(f"runs:/{run_id}/{model_path}")
    return model


def get_registered_model(model_name: str, model_stage: str):
    _logger.debug("Finding trained model on MLflow Server")
    _logger.debug(f"Model name: {model_name}")
    _logger.debug(f"Model stage: {model_stage}")

    client = mlflow.tracking.MlflowClient()
    registered_models = client.search_model_versions(f"name='{model_name}'")

    registered_models_in_stage = [
        rm for rm in registered_models if rm.current_stage == model_stage
    ]

    if len(registered_models_in_stage) == 0:
        raise LookupError(f"{model_stage} version of model {model_name} not found")
    if len(registered_models_in_stage) > 1:
        _logger.warning(
            f"{len(registered_models_in_stage)} {model_stage} versions of model {model_name} found"
        )

    rm = registered_models_in_stage[-1]
    _logger.info(f"Loading model '{model_name}' version {rm.version}")

    model_path = None
    for p in Path(rm.source).parents:
        if p.stem == "artifacts":
            model_path = Path(rm.source).relative_to(p)

    if model_path is None:
        raise ValueError("Path of model in artifact store not found")

    return get_model(rm.run_id, str(model_path)), rm.version


def store_grafana_metrics(metrics, name, label):
    """
    metrics: all metrics to be stored to grafana
    name: string
    label: string
    return: stores metrics to PostGres DB
    """
    _logger.warning("Storing Grafana metrics to PostGres DB")
    # connect the client
    monitoring_client = MonitoringClient(namespace=name)
    # use the .store() method to submit a dictionary of key: value pairs!
    monitoring_client.store(
        metrics=metrics, label=label
    )  # see docstring for optional addition of labels, the use of run_id, etc.
