#!/usr/local/bin/python3

import os
from datetime import datetime

import numpy as np
import pandas as pd
from pydataset import data
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

print("start: ", datetime.now().strftime("%H:%M:%S"))
print(os.chdir("/Users/benvanvliet/Desktop"))
# get data
df = data("diamonds")
df["label"] = np.where(df["price"] > 14000, 1, 0)

# df.to_csv(r'diamonds.csv', index=False)

# print label ratio
print(df["label"].value_counts())
print(df["label"].mean().round(4))

# create missing
df["table"] = np.where(df["table"] == 58.1, np.nan, df["table"])

# set data types
df["cut"] = df["cut"].astype(str)
df["color"] = df["color"].astype(str)

# drop all rows with missing
# print(df.isnull().sum())
# df = df.dropna()

# create dummy vars, don't need first
df = pd.get_dummies(df, drop_first=True)

# set X, y
y = df["label"].values
X = df[["x", "y", "z", "table"]].values
# X = df.filter(like='feature_').values # test
# X = df.drop('price', axis=1).values

# split train, test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# create classifier, svm
clf = SVC()

# create imputer
imp = SimpleImputer(missing_values=np.nan, strategy="mean")

parameters = {
    "svm__C": [1, 10, 100],  # regularization strength
    "svm__gamma": [0.1, 0.01],
}  # the kernel coefficient

# create pipeline
pipeline = Pipeline([("imputer", imp), ("scaler", StandardScaler()), ("svm", clf)])

# fit
print("fit: ", datetime.now().strftime("%H:%M:%S"))
cv = GridSearchCV(pipeline, parameters, cv=2)
cv.fit(X_train, y_train)

# predict
print("predict: ", datetime.now().strftime("%H:%M:%S"))
y_pred = cv.predict(X_test)

# best parameters
print("best params: ", cv.best_params_)

# best score
print("Best score:", cv.best_score_)

# confusion matrix
print(confusion_matrix(y_test, y_pred))

# report
print(classification_report(y_test, y_pred, zero_division=0))  # check zero_division

# roc
# plot_roc_curve(cv, X_test, y_test)
# print(plt.show())

print("finish: ", datetime.now().strftime("%H:%M:%S"))
