#!/usr/local/bin/python3

from datetime import datetime

import numpy as np
import xgboost as xgb
from pydataset import data
from sklearn.feature_extraction import DictVectorizer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import RandomizedSearchCV
from sklearn.pipeline import Pipeline

print("get data:", datetime.now().strftime("%H:%M:%S"))

# get data
df = data("diamonds")

# create missings
df["y"] = np.where(df["y"] == 3.98, np.nan, df["y"])

df["label"] = np.where(df["clarity"] == "SI2", 1, 0)
# df['label'] = np.where(df['price'] > 17000, 1, 0)

# rename and set data types
df["feature_x"] = df["x"]
df["feature_y"] = df["y"]
df["feature_cut"] = df["cut"].astype("category")
df["feature_color"] = df["color"].astype("category")

# set X,y
y = df["label"]
X = df.filter(like="feature_")
print(X.head())

print("grid:", datetime.now().strftime("%H:%M:%S"))

grid = {
    "clf__learning_rate": np.arange(0.05, 1, 0.05),
    "clf__max_depth": np.arange(3, 10, 1),
    "clf__n_estimators": np.arange(50, 200, 50),
}

xgb_pipeline = Pipeline(
    [
        ("ohe_onestep", DictVectorizer(sparse=False)),
        ("imp", SimpleImputer(strategy="median")),
        ("clf", xgb.XGBClassifier(max_depth=2, objective="binary:logistic")),
    ]
)

rgcv = RandomizedSearchCV(
    estimator=xgb_pipeline,
    param_distributions=grid,
    n_iter=20,
    scoring="accuracy",
    cv=5,
    verbose=1,
)

# when using the DictVectorizer, make sure X are dicts
rgcv.fit(X.to_dict("records"), y)

print(rgcv.best_score_)
print(rgcv.best_estimator_)

print("finish:", datetime.now().strftime("%H:%M:%S"))
