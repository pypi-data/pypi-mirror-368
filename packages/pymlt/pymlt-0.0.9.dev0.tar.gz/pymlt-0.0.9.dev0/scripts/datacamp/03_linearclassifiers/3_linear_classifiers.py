#!/usr/local/bin/python3

import pandas as pd
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


def load_data(n=10000, f=12):
    """load training data"""
    X, y = make_classification(n_samples=n, n_features=f)
    df = pd.DataFrame(X, y)
    df = df.rename(columns=lambda x: "feature_" + str(x))
    df = df.reset_index().rename(columns={"index": "label"})
    return df


df = load_data()


X = df.filter(like="feature_")
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

for c in [0.001, 1, 10]:
    lr = LogisticRegression(C=c).fit(X_train, y_train)
    print(c)
    print(lr.score(X_train, y_train))
