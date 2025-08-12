#!/usr/local/bin/python3

"""
notes at clfs file

"""

from datetime import datetime

import numpy as np
import pandas as pd
import xgboost as xgb
from pydataset import data
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, train_test_split

print("get data:", datetime.now().strftime("%H:%M:%S"))

# get data
df = data("diamonds")

# set label
df["label"] = df["price"]

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
# print(pd.DataFrame(X_names, columns=['features']))

# split train, test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("models:", datetime.now().strftime("%H:%M:%S"))

# xgb w/ tree as base learner (default booster)
xg_reg = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=10, seed=123)
xg_reg.fit(X_train, y_train)
preds = xg_reg.predict(X_test)
print(np.sqrt(mean_squared_error(y_test, preds)))


# xgb w/ linear model as base learner
dm_train = xgb.DMatrix(data=X_train, label=y_train)
dm_test = xgb.DMatrix(data=X_test, label=y_test)
params = {"booster": "gblinear", "objective": "reg:squarederror"}
# uncommon to use gblinear, thus use sklearns api (.train)
xg_reg = xgb.train(params=params, dtrain=dm_train, num_boost_round=5)
preds = xg_reg.predict(dm_test)
print(np.sqrt(mean_squared_error(y_test, preds)))

# cv
params = {"objective": "reg:squarederror", "max_depth": 4}
cv = xgb.cv(
    dtrain=dm_train,
    params=params,
    nfold=4,
    num_boost_round=5,
    metrics="rmse",
    as_pandas=True,
)
print(cv)
print((cv["test-rmse-mean"]).tail(1))

print("regularization:", datetime.now().strftime("%H:%M:%S"))
# regularization
reg_params = [1, 10, 100]
params = {"objective": "reg:squarederror", "max_depth": 3}
rmses_l2 = []

for reg in reg_params:
    params["lambda"] = reg  # add to params dict

    cv_results_rmse = xgb.cv(
        dtrain=dm_train,
        params=params,
        nfold=2,
        num_boost_round=5,
        metrics="rmse",
        as_pandas=True,
    )

    # append to list
    rmses_l2.append(cv_results_rmse["test-rmse-mean"].tail(1).values[0])

# create df by zipping two lists + print
print(pd.DataFrame(list(zip(reg_params, rmses_l2)), columns=["l2", "rmse"]))


print("=== parameter tuning:", datetime.now().strftime("%H:%M:%S"))
# parameter tuning w/ for loop
params = {"objective": "reg:squarederror", "max_depth": 3}
num_rounds = [5, 10, 150, 200]
rmse = []

for r in num_rounds:
    cv = xgb.cv(
        dtrain=dm_train,
        params=params,
        nfold=3,
        num_boost_round=r,
        early_stopping_rounds=10,  # if rmse does not improve for 10 rounds
        metrics="rmse",
        as_pandas=True,
    )

    rmse.append(cv["test-rmse-mean"].tail().values[-1])

output = list(zip(num_rounds, rmse))
print(pd.DataFrame(output, columns=["num_boosting_rounds", "final_rmse_per_round"]))

print("=== gridsearch:", datetime.now().strftime("%H:%M:%S"))
# parameter tuning w/ gridsearch
gbm_param_grid = {
    "colsample_bytree": [0.3, 0.7],
    "n_estimators": [50],
    "max_depth": [2, 5],
}

gbm = xgb.XGBRegressor()
grid_mse = GridSearchCV(
    estimator=gbm,
    param_grid=gbm_param_grid,
    scoring="neg_mean_squared_error",
    cv=4,
    verbose=1,
)

grid_mse.fit(X_train, y_train)
print(np.sqrt(np.abs(grid_mse.best_score_)))


print("=== randomizedsearch:", datetime.now().strftime("%H:%M:%S"))
# parameter tuning w/ randomizedsearch

gbm_param_grid = {"n_estimators": [25], "max_depth": range(2, 12)}

gbm = xgb.XGBRegressor(n_estimators=10)
randomized_mse = RandomizedSearchCV(
    estimator=gbm,
    param_distributions=gbm_param_grid,
    n_iter=5,
    scoring="neg_mean_squared_error",
    cv=4,
    verbose=1,
)
randomized_mse.fit(X_train, y_train)
print(np.sqrt(np.abs(randomized_mse.best_score_)))
