#!/usr/local/bin/python3

# https://campus.datacamp.com/courses/supervised-learning-with-scikit-learn/

import numpy as np
from pydataset import data
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

df = data("diamonds")

X = df[["x", "y", "z"]].values
y = df["price"].values

reg = LinearRegression()
reg.fit(X, y)

y_pred = reg.predict(X)
print("R2:", round(reg.score(X, y), 3))
print("RMSE:", round(np.sqrt(mean_squared_error(y, y_pred)), 2))

# lenear regression minimizes a loss function
# large coefficients lead to overfitting
# regularisation = alter loss function to penalize large coefficients

# Ridge Regression
# Alpha = parameter
