#!/usr/local/bin/python3

"""
https://learn.datacamp.com/courses/machine-learning-with-tree-based-models-in-python

- trees standardized or normalized scales
- plot decision regions and boundaries for inspection
- root, internal node, leaf
- leaf is created when no further information gain can be achived
- limitation: only orthogonal decision bounderies
- limitation: sensitive to small variations in data
- limitation: unconstrained CART may overfit training data
- ensemble learning mitigates limitations
- ensemble learning is more robust and less prone to error

- generalization error (generalization to unseen data)
- Bias-Variance Tradeoff in model complexity
- Bias-Variance Tradeoff equal to under- and overfitting
- find best model complexity by inspecting bias and variance in train vs k-fold train scores

Models:
> DecisionTrees
> DecisionTrees w/ GridSearchCV
> LogisticRegression w/ GridSearchCV
> Voting (multiple algorithms)
> Bagging (one algorithm, subset of data w/ replacement)
> AdaBoost (adjust weights)
> GradientBoost (models the errors)
> Stochastic GradientBoost (sample data and features)

classification problems presented below
use print("rmse:", MSE(y_test, y_pred)**(1/2)) to evaluate regression problems

"""

from datetime import datetime

import numpy as np
import pandas as pd
from pydataset import data
from sklearn.ensemble import AdaBoostClassifier  # or regressor
from sklearn.ensemble import BaggingClassifier  # or regressor
from sklearn.ensemble import GradientBoostingClassifier  # or regressor
from sklearn.ensemble import RandomForestClassifier  # or regressor
from sklearn.ensemble import VotingClassifier  # or regressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier  # or regressor

print("get data:", datetime.now().strftime("%H:%M:%S"))

# get data
df = data("diamonds")
df["label"] = np.where(df["price"] > 17000, 1, 0)

# rename and set data types
df["feature_x"] = df["x"]
df["feature_y"] = df["y"]
df["feature_cut"] = df["cut"].astype(str)
df["feature_color"] = df["color"].astype(str)

# create dummies
df = pd.get_dummies(df, drop_first=True)

# set X, y
y = df["label"]  # .values
X = df.filter(like="feature_")  # .values
X_names = df.filter(like="feature_").columns

# split train, test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("models:", datetime.now().strftime("%H:%M:%S"))

# initiate clfs
dt = DecisionTreeClassifier(max_depth=6, criterion="gini", random_state=1)
dt.fit(X_train, y_train)
y_pred = dt.predict(X_test)
print("acc dt:    ", round(accuracy_score(y_test, y_pred), 4))

# dt w/ gridsearchCV
dt_params = {"max_depth": [2, 3, 4], "min_samples_leaf": [0.12, 0.14, 0.16, 0.18]}

dt_cv = GridSearchCV(
    estimator=DecisionTreeClassifier(), param_grid=dt_params, scoring="roc_auc", cv=5
)

dt_cv.fit(X_train, y_train)
y_pred = dt_cv.predict(X_test)
# print(dt_cv.best_estimator_)
print("acc dt_cv: ", round(accuracy_score(y_test, y_pred), 4))

# create list
lr = LogisticRegression(max_iter=200)
knn = KNeighborsClassifier(n_neighbors=40)
dt = DecisionTreeClassifier(max_depth=5, min_samples_leaf=0.1)
clfs = [("logreg", lr), ("knn", knn), ("tree", dt)]

# initiate clf (voting)
vc = VotingClassifier(estimators=clfs).fit(X_train, y_train)
y_pred = vc.predict(X_test)
print("acc vc:    ", round(accuracy_score(y_test, y_pred), 4))

# initiate clf (bagging)
dt = DecisionTreeClassifier(max_depth=5, min_samples_leaf=0.1)
bc = BaggingClassifier(base_estimator=dt, n_estimators=50, oob_score=True, n_jobs=-1)
bc.fit(X_train, y_train)
y_pred = bc.predict(X_test)
print("acc bc:    ", round(accuracy_score(y_test, y_pred), 4))
print("acc bc oob:", round(bc.oob_score_, 4))  # out of bag accuracy

# Define the dictionary 'params_rf'
rf_params = {
    "n_estimators": [100, 350, 500],
    "max_features": ["log2", "auto", "sqrt"],
    "min_samples_leaf": [2, 10, 30],
}

rf_cv = GridSearchCV(
    estimator=RandomForestClassifier(), param_grid=rf_params, scoring="roc_auc", cv=2
)

# rf_cv.fit(X_train, y_train) # expensive!
# y_pred = rf_cv.predict(X_test)
# print(dt_cv.best_estimator_)
# print("acc rf_cv test:", round(accuracy_score(y_test, y_pred), 6))

# initiate clf (rf)
rf = RandomForestClassifier(n_estimators=25)
# rf.get_params()  # inspect hyperparameters
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
print("acc rf:    ", round(accuracy_score(y_test, y_pred), 4))
# print(pd.Series(data=rf.feature_importances_, index=X_names).sort_values(ascending=False).head(5))

# initiate clf (ada)
dt = DecisionTreeClassifier(max_depth=1)
ada = AdaBoostClassifier(base_estimator=dt, n_estimators=180)
ada.fit(X_train, y_train)
y_pred = ada.predict(X_test)
print("acc ada:   ", round(accuracy_score(y_test, y_pred), 4))
y_pred_proba = ada.predict_proba(X_test)[:, 1]
print("auc ada:   ", round(roc_auc_score(y_test, y_pred_proba), 4))

# initiate clf (gbt)
gb = GradientBoostingClassifier(n_estimators=180, max_depth=1)
gb.fit(X_train, y_train)
y_pred = gb.predict(X_test)
print("acc gb:    ", round(accuracy_score(y_test, y_pred), 4))
y_pred_proba = gb.predict_proba(X_test)[:, 1]
print("auc gb:    ", round(roc_auc_score(y_test, y_pred_proba), 4))

# initiate clf (stochastic gbt)
sgb = GradientBoostingClassifier(
    n_estimators=180,
    max_depth=1,
    subsample=0.9,  # sample data
    max_features=0.50,
)  # sample features
sgb.fit(X_train, y_train)
y_pred = sgb.predict(X_test)
print("acc sgb:   ", round(accuracy_score(y_test, y_pred), 4))
y_pred_proba = gb.predict_proba(X_test)[:, 1]
print("auc sgb:   ", round(roc_auc_score(y_test, y_pred_proba), 4))
