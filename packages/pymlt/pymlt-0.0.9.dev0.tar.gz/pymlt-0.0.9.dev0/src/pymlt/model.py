"""
this model contains all functions needed to fit a model
"""

# todo: replace ho with scikit-optimize or https://github.com/fmfn/BayesianOptimization
# todo: https://www.kaggle.com/fanvacoolt/tutorial-on-hyperopt
# todo: https://machinelearningmastery.com/scikit-optimize-for-hyperparameter-tuning-in-machine-learning/

# from hyperopt import hp
from sklearn.compose import ColumnTransformer
from sklearn.compose import make_column_selector as selector
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src import utils

_logger = utils.logging.getLogger(__name__)


def get_preprocessor():
    num_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="mean")),
            ("scaler", StandardScaler()),
        ]
    )

    cat_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("ohe", OneHotEncoder()),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                num_transformer,
                selector(dtype_exclude=["category", "object"]),
            ),
            (
                "categorical",
                cat_transformer,
                selector(dtype_include=["category", "object"]),
            ),
        ]
    )

    return preprocessor


def get_estimator(**params):
    estimator = RandomForestClassifier(**params)

    return estimator


def get_pipeline(preprocessor, estimator, verbose=0):
    pipeline = Pipeline(
        steps=[("preprocessor", preprocessor), ("estimator", estimator)]
    )

    if verbose:
        print(list(pipeline.get_params().keys()))

    return pipeline


def get_search_space():
    search_space = {
        "estimator__n_estimators": range(5, 20, 1),
        "estimator__max_depth": range(3, 10, 1),
    }

    # search_space = {
    #     "n_estimators": hp.quniform("num_leaves", 10, 150, 1),
    #     "max_depth": hp.quniform("max_depth", 3, 6, 1),
    # }

    # search_space = {
    #     "n_estimators": hp.choice("n_estimators", range(50, 500, 50)),
    #     "max_depth": hp.choice("max_depth", range(1, 50, 1)),
    #     "criterion": hp.choice("criterion", ["gini", "entropy"]),
    #     "min_samples_split": hp.uniform("min_samples_split", 0.05, 0.25),
    #     "min_samples_leaf": hp.choice("min_samples_leaf", range(1, 10)),
    #     "bootstrap": hp.choice("bootstrap", [True, False]),
    #     "max_features": hp.choice("max_features", ["auto", "sqrt"]),
    # }

    return search_space


def get_best_params_ho():
    """hyperopt"""
    pass


def get_best_params_gs(pipeline, search_space, x_train, y_train):
    """gridsearch"""

    model = GridSearchCV(
        estimator=pipeline,
        param_grid=search_space,
        scoring="roc_auc",
        cv=5,
    ).fit(x_train, y_train)

    print(model.best_params_)

    return model.best_params_
