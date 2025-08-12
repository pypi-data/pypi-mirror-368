"""
Functions that model different classifiers with simple settings, and functions regarding model diagnostics.
"""

import matplotlib.pylab as plt
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import accuracy_score, precision_recall_curve
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from xgboost import XGBClassifier


def _change_tbm_columns(df: pd.DataFrame):
    """
    Helper function of train_basic_model() which changes the name of the mean_test variables to avg for better
    visualization in the notebook and returns a list of the actual changed variables.

    Parameters
    ----------
    df : dataframe
        Input data including the dependent and independent variables ready to be modelled.

    Returns
    -------
    df : dataframe
        Dataframe with the renamed variables.
    avg_variables : list
        List with the variable names.
    """
    df.columns = df.columns.str.replace("mean_test", "avg")
    avg_variables = list(df.columns[df.columns.str.contains("avg")])

    return df, avg_variables


def _round_tbm_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function of train_basic_model() which rounds floats to 3 decimals for better visualization in the notebook.

    Parameters
    ----------
    df : dataframe
        Input data including the dependent and independent variables ready to be modelled.

    Returns
    -------
    df : dataframe
        Dataframe with the transformed variables.
    """
    for variable in df.select_dtypes(include=["float64"]).columns:
        df[variable] = df[variable].round(3)

    return df


def _sum_tbm_rank_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function of train_basic_model() which sums the ranking of different models based on scoring criteria
    to pinpoint an overall winner.

    Parameters
    ----------
    df : dataframe
        Input data including the dependent and independent variables ready to be modelled.

    Returns
    -------
    df : dataframe
        Dataframe including the new 'winner' variable.
    """
    rank_variables = list(df.columns[df.columns.str.contains("rank_")])
    df["sum_rank"] = df[rank_variables].sum(axis=1)

    return df


def _add_classifer_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function of train_basic_model() which extracts only the name of the classifier from the 'params_classifier'
    for better visualization in the notebook.

    Parameters
    ----------
    df : dataframe
        Input data including the dependent and independent variables ready to be modelled.

    Returns
    -------
    df : dataframe
        Dataframe with the transformed variables.
    """
    classifiers = []
    for i in range(len(df["param_classifier"])):
        classifiers.append(df["param_classifier"].apply(str)[i].split("(")[0])
    df["classifier"] = classifiers

    return df


def train_basic_models(x: pd.DataFrame, y: pd.DataFrame) -> pd.DataFrame:
    """
    Scikit-learn GridSearchCV wrapper which trains several classifiers with standard settings. The results should
    give direction to the model(s) you want to fully optimize via hyperparameter tuning. Please take fit time and
    complexity into account as well.

    Parameters
    ----------
    x : dataframe
        Dataframe with the independent variables.
    y : dataframe
        Dataframe with the dependent variable.

    Returns
    -------
    pd_results : dataframe with the following diagnostics:
    - param_classifier: name of the classifier
    - mean_fit_time: average time it took to fit the model between the cross validations (default=5)
    - sum_rank: sums the rank based on accuracy, f1 and roc_auc, the lower the better
    - mean_test_accuracy: average accuracy on the validation set between the cross validations (default=5)
    - mean_test_f1: average f1 score on the validation set between the cross validations (default=5)
    - mean_test_roc_auc: average roc auc score on the validation set between the cross validations (default=5)
    """
    pipe = Pipeline(
        [("scaler", StandardScaler()), ("classifier", RandomForestClassifier())]
    )

    param_grid = [
        {
            "classifier": [
                RandomForestClassifier(max_depth=10),
                LogisticRegression(),
                XGBClassifier(),
                SGDClassifier(),
                LGBMClassifier(max_depth=10),
                LinearSVC(),
            ]
        }
    ]

    clf = GridSearchCV(
        estimator=pipe,
        param_grid=param_grid,
        cv=5,
        scoring=["accuracy", "f1", "roc_auc"],
        n_jobs=-1,
        verbose=0,
        refit=False,
    )

    clf_fit = clf.fit(x, y)

    pd_results = pd.DataFrame(clf_fit.cv_results_)

    pd_results, avg_test_variables = _change_tbm_columns(pd_results)
    pd_results = _round_tbm_columns(pd_results)
    pd_results = _sum_tbm_rank_columns(pd_results)
    pd_results = _add_classifer_column(pd_results)

    return pd_results[
        ["classifier", "mean_fit_time", "sum_rank"] + avg_test_variables
    ].sort_values(by="sum_rank")


def plot_recall_precision(model, x_val, y_val):
    """
    Returns a plot with the recall and precision functions per threshold. Based on Hands-On Machine Learning with
    Scikit-Learn & TensorFlow by Aurelien Geron.

    Parameters
    ----------
    model : sklearn Classifier or Pipeline including an estimator
        The model used to create predictions based on the features of the validation set.
    x_val : dataframe
        Dataframe of features of the validation set.
    y_val : dataframe
        Dataframe of the dependent variable of the validation set.

    Returns
    -------
    None : A plot of the tradeoff between recall and precision.
    """
    model_proba = model.predict_proba(x_val)
    precision, recall, threshold = precision_recall_curve(y_val, model_proba[:, 1])

    plt.plot(threshold, precision[:-1], label="precision")
    plt.plot(threshold, recall[:-1], label="recall")
    plt.legend()
    plt.show()


def underfit_overfit(model, x_train, y_train, x_val, y_val, step=1000):
    """
    Trains, predicts and evaluates the model for different sizes of the dataset. High scores on the trainset and low
    scores on the validation set indicates an overfit, low scores on both the train and test set indicates underfit.
    Based on Hands-On Machine Learning with Scikit-Learn & TensorFlow by Aurelien Geron.

    Parameters
    ----------
    model : sklearn Classifier or Pipeline including an estimator
        The model used to create predictions based on the features of the validation set.
    x_train : dataframe
        Dataframe of features of the train set.
    y_train : dataframe
        Dataframe of the dependent variable of the train set.
    x_val : dataframe
        Dataframe of features of the validation set.
    y_val : dataframe
        Dataframe of the dependent variable of the validation set.
    step : integer
        Indicates the increment of training data used to evaluate the prediction error for the train and validation set.

    Returns
    -------
    None : A plot of the prediction error for the train- and test set for different sizes of data.
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
