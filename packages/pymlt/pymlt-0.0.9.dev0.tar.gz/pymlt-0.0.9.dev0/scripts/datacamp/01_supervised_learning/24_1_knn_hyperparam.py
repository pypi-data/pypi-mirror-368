#!/usr/local/bin/python3

# https://campus.datacamp.com/courses/supervised-learning-with-scikit-learn/

import numpy as np
from pydataset import data
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV

df = data("diamonds")
df["price_cat"] = np.where(df["price"] > 17000, 1, 0)

X = df[["depth"]].values
y = df["price_cat"].values


logreg = LogisticRegression()
logreg.fit(X, y)
print(logreg.score(X, y))


# hyperparameters cannot be learned by modelling -- gridsearch + cv needed

# C controls the inverse of the regularization strength
param_grid = {"C": np.logspace(-5, 8, 15)}
logreg = LogisticRegression()
logreg_cv = GridSearchCV(logreg, param_grid, cv=5)
logreg_cv.fit(X, y)

print(logreg_cv.best_params_)
print(logreg_cv.best_score_)
