"""
train classification model
"""

from datetime import datetime

from dotenv import find_dotenv, load_dotenv
from sklearn.model_selection import train_test_split

from src import config, evaluate, explore, load, model, utils

# set logger
_logger = utils.logging.getLogger(__name__)

# load env vars
load_dotenv(find_dotenv())

# set run id for experiment tracking
run_id = datetime.now().strftime("%Y%m%d_%H%M")


def main():
    # instantiate grafana logger
    grafana = evaluate.GrafanaLog()

    # load data
    df = load.penguins(config.N_SAMPLES)

    # set data exploration class
    data = explore.Understand(df)

    # set X and y
    X = data.get_x()
    y = data.get_y()

    # set train, test
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2)

    # get preprocessor
    preprocessor = model.get_preprocessor()

    # get estimator
    estimator = model.get_estimator()

    # get pipeline
    pipeline = model.get_pipeline(preprocessor, estimator, verbose=0)

    # get search_space
    search_space = model.get_search_space()

    # get best hyperparams
    params = model.get_best_params_gs(pipeline, search_space, X_train, y_train)

    # fit pipeline
    pipeline.set_params(**params).fit(X_train, y_train)

    # model evaluation
    evaluation = evaluate.ModelEvaluation(pipeline, X_test, y_test)
    metrics = evaluation.get_metrics()
    print(metrics)
    lift = evaluation.get_model_lift_table()
    print(lift)

    # shap analysis
    # evaluation_shap = evaluate.ShapAnalysis(config, pipeline, X_test, y_test)  # todo: add shap

    # create model_dict
    model_dict = {
        "params": params,
        "metrics": metrics,
        "model": pipeline,
        "artifacts": "./out",
        "tags": {"estimator_class": "lgbm_clf", "hyperopt": True},
    }

    # add logging
    grafana.add_df(df)
    grafana.add_feature_descriptives()

    # log model and model info to mlflow
    if config.mlflow_log:
        utils.save_results_mlflow(config_dict, model_dict)


if __name__ == "__main__":
    main()
    _logger.info("done!")
