#!/usr/local/bin/python3

import pandas as pd
from pydataset import data
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import make_scorer, mean_absolute_error, mean_squared_error
from sklearn.model_selection import RandomizedSearchCV, train_test_split

df = data("diamonds")

df = df.rename(
    columns={
        "color": "feature_color",
        "cut": "feature_cut",
        "x": "feature_x",
        "y": "feature_y",
    }
)

df = pd.get_dummies(df, drop_first=True)


y = pd.to_numeric(df["price"], downcast="float")
X = df.filter(like="feature_")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

rfr = RandomForestRegressor().fit(X_train, y_train)

pred = rfr.predict(X_test)
print(mean_absolute_error(y_test, pred))
print(mean_squared_error(y_test, pred))

# random search cv

param_dist = {
    "max_depth": [2, 4, 6, 8],
    "max_features": [2, 4, 6, 8, 10],
    "min_samples_split": [2, 4, 8, 16],
}

rfr = RandomForestRegressor(n_estimators=10, random_state=123)
scorer = make_scorer(mean_squared_error)

rs = RandomizedSearchCV(
    estimator=rfr, param_distributions=param_dist, n_iter=10, cv=5, scoring=scorer
)

rs.fit(X_train, y_train)

print(rs.cv_results_)
print(rs.best_score_)
