#!/usr/local/bin/python3

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC, LinearSVC


def load_data(n=100, f=6):
    """load training data"""
    X, y = make_classification(n_samples=n, n_features=f)
    df = pd.DataFrame(X, y)
    df = df.rename(columns=lambda x: "feature_" + str(x))
    df = df.reset_index().rename(columns={"index": "label"})
    return df


df = load_data(100, 10)

X = df.filter(like="feature_")
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

classifiers = [LogisticRegression(), LinearSVC(), SVC(), KNeighborsClassifier()]

for c in classifiers:
    c.fit(X_train, y_train)
    print(c.score(X_train, y_train).round(5))


# dot product, @
print(np.arange(3) @ np.arange(3, 6))

# LogisticRegression uses the dot product to make predictions
# raw model output = coefficients @ features + intercept
lr = LogisticRegression().fit(X_train, y_train)
print(lr.coef_ @ X_train.iloc[3] + lr.intercept_)

# svc and logreg have different fit methods (based on loss function), but same fit (using dot product)
