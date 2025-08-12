#!/usr/local/bin/python3

import numpy as np
import pandas as pd
from pydataset import data
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    make_scorer,
    precision_score,
    recall_score,
)
from sklearn.model_selection import cross_val_score, train_test_split

df = data("diamonds")

df = df.rename(
    columns={
        "carat": "feature_carat",
        "cut": "feature_cut",
        "color": "feature_color",
        "clarity": "feature_clarity",
        "depth": "feature_depth",
        "x": "feature_x",
        "y": "feature_y",
    }
)

df = pd.get_dummies(df, drop_first=True)


y = df["label"] = np.where(df["price"] > 16000, 1, 0)
X = df.filter(like="feature_")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y)

rf = RandomForestClassifier(
    n_estimators=20,
    max_depth=5,
    max_features=4,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=123,
)

rf.fit(X_train, y_train)
print(rf.get_params())
print(rf.max_depth)

imp = pd.DataFrame(rf.feature_importances_, index=X_train.columns).rename(
    columns={0: "imp"}
)
print(imp.sort_values("imp", ascending=False).head(5))

print(rf.predict_proba(X_test)[:5, 1])
print(rf.predict(X_test))
print(pd.Series(rf.predict(X_test)).value_counts())
print(rf.score(X_test, y_test))

# accuracy = ability to correctly classify
# precision = finding only real 1's - when a FP is expensive
# recall = finding all 1's - when a FN is expensive

preds = rf.predict(X_test)
cm = confusion_matrix(y_test, preds)
print(cm)

print(accuracy_score(y_test, preds))
print(precision_score(y_test, preds))
print(recall_score(y_test, preds))

# bias-variance trade off
# high variance = overfitting = low training error, high test error
# high bias = underfitting =  high training error, high test error

preds_train = rf.predict(X_train)
acc_train = accuracy_score(y_train, preds_train)
acc_test = accuracy_score(y_test, preds)
print(acc_train, acc_test, acc_train / acc_test)

# cv
cv = cross_val_score(
    estimator=rf, X=X_train, y=y_train, cv=10, scoring=make_scorer(recall_score)
)

# Print the mean error
print("cv: ", cv.mean())

# loocv, leave one out
# note: leave one observation (!) out, computational expensive
cv = cross_val_score(
    estimator=rf,
    X=X_train,
    y=y_train,
    cv=X_train.shape[0],  # de facto loocv
    scoring=make_scorer(recall_score),
)
