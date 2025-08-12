#!/usr/local/bin/python3

"""
https://campus.datacamp.com/courses/extreme-gradient-boosting-with-xgboost/

- speed and performance because algorithm is parallelizable
- consistently outperforms other algorithms
- xgboost uses CART as a base learner in an ensemble algorithm
- carts leafs always contain real values, both for clf and reg problems
- boosting is ensemble meta-algorithm used to convert n weak learners into a strong learner
- convert a df to a DMatrix for optimized performance
- xgb suitable when training samples > 1000 and training sample > n features
- xgb not suitable for images, nlp and training sample < 1000
- loss functions:
    - reg:linear = regression problems
    - reg:logistic = classification problems, decision
    - binary:logistic = classification problems, probability
- regularization is penalizing model for complexity
    - loss function aim at accuracy and model simplicity
- hyperparameters:
    - regularization parameters:
        - gamma = minimum loss reduction for a split to occur
        - alpha = l1-regularization on leaf weights (strong reduction to zero)
        - lambda = l2-regularization on leaf weights (smooth reduction)
    - learning rate = how quickly the model fits the residual error using additional base learners
        - low = more boosting rounds needed
        - high = less round needed + penalizing feature weights more strongly thus stronger regularization.
    - max_depth = how deep trees are allowed to grow
    - subsample = fraction of the total training set that can be used per boosting round
        - low = possible underfitting
        - high = possible overfitting
    - colsample_bytree = fraction of features used per boosting round
        - using a fraction can be seen as regularization
        - all features can lead to overfitting
    - lambda (linear) = l2 reg on weights
    - alpha (linear) = l1 reg on weights
    - alpha_bias = l1 reg term on bias
- gridSearch
- randomSearch


"""

from datetime import datetime

import numpy as np
import pandas as pd
import xgboost as xgb
from pydataset import data
from sklearn.model_selection import train_test_split

print("get data:", datetime.now().strftime("%H:%M:%S"))

# get data
df = data("diamonds")

# set label
df["label"] = np.where(df["clarity"] == "SI2", 1, 0)

# rename and set data types
df["feature_x"] = df["x"]
df["feature_y"] = df["y"]
df["feature_cut"] = df["cut"].astype(str)
df["feature_color"] = df["color"].astype(str)

# create dummies
df = pd.get_dummies(df, drop_first=True)

# set X, y
y = df["label"].values
X = df.filter(like="feature_").values
X_names = df.filter(like="feature_").columns
print(pd.DataFrame(X_names, columns=["features"]))

# split train, test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("models:", datetime.now().strftime("%H:%M:%S"))

# xgboost
xg = xgb.XGBClassifier(objective="binary:logistic", n_estimators=10, seed=123)
xg.fit(X_train, y_train)
preds = xg.predict(X_test)
print(preds[:5,])
print(np.sum(preds == y_test) / y_test.shape[0])  # accuracy


# cv based on error
dmatrix = xgb.DMatrix(data=X_train, label=y_train)

params = {"objective": "reg:logistic", "max_depth": 3}

cv_results = xgb.cv(
    dtrain=dmatrix,
    params=params,
    nfold=3,
    num_boost_round=5,
    metrics="error",
    as_pandas=True,
)

print(cv_results)  # test error mean over folds per boosting round
print(
    ((1 - cv_results["test-error-mean"]).iloc[-1])
)  # accuracy based on final boost round


# cv based on auc
dmatrix = xgb.DMatrix(data=X_train, label=y_train)

params = {"objective": "reg:logistic", "max_depth": 3}

cv_results = xgb.cv(
    dtrain=dmatrix,
    params=params,
    nfold=3,
    num_boost_round=5,
    metrics="auc",
    as_pandas=True,
)

print(cv_results)  # test auc mean over folds per boosting round
print(((cv_results["test-auc-mean"]).iloc[-1]))  # accuracy based on final boost round
