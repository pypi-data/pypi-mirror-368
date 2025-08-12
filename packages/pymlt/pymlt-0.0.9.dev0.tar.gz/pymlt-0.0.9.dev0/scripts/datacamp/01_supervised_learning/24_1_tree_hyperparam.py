#!/usr/local/bin/python3

# https://campus.datacamp.com/courses/supervised-learning-with-scikit-learn/

import numpy as np
from pydataset import data
from scipy.stats import randint
from sklearn.model_selection import RandomizedSearchCV
from sklearn.tree import DecisionTreeClassifier

df = data("diamonds")
df["price_cat"] = np.where(df["price"] > 17000, 1, 0)

X = df[["depth", "x", "y", "z"]].values
y = df["price_cat"].values

param_dist = {
    "max_depth": [3, None],
    "max_features": randint(1, 4),
    "min_samples_leaf": randint(1, 9),
    "criterion": ["gini", "entropy"],
}

tree = DecisionTreeClassifier()

tree_cv = RandomizedSearchCV(tree, param_dist, cv=5)

tree_cv.fit(X, y)

print("Tuned parameters:", tree_cv.best_params_)
print("Best score:", tree_cv.best_score_)
