#!/usr/local/bin/python3

import pandas as pd
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split


def load_data(n=10000, f=10):
    """load training data"""
    X, y = make_classification(n_samples=n, n_features=f)
    df = pd.DataFrame(X, y)
    df = df.rename(columns=lambda x: "feature_" + str(x))
    df = df.reset_index().rename(columns={"index": "label"})
    df.loc[: (n * 0.2), "label"] = 0
    print(df.label.value_counts())
    return df


df = load_data()
y = df["label"]
X = df.filter(like="feature_")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=30,
    max_features=10,
    min_samples_split=2,
    min_samples_leaf=2,
).fit(X_train, y_train)

# create predictions
preds = rf.predict(X_test)

# confusion_matrix
print(confusion_matrix(y_test, preds))

# accuracy = ability to correctly classify
a = accuracy_score(y_test, preds).round(3)

# precision = finding only real 1's - when a FP is expensive
p = precision_score(y_test, preds).round(3)

# recall = finding all 1's - when a FN is expensive
r = recall_score(y_test, preds).round(3)

print("a: {}, p: {}, r: {}".format(a, p, r))
# f1 = harmonic mean of precision and recall
# it punishes low values
# good measure if you want both recall and precision to be high
print(classification_report(y_test, preds))

# check for overfitting
acc_train = accuracy_score(y_train, rf.predict(X_train))
acc_test = accuracy_score(y_test, rf.predict(X_test))
print(acc_train, acc_test, acc_train / acc_test)
