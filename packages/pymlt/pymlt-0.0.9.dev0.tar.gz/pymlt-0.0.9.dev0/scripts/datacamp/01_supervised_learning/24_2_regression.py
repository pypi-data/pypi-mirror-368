#!/usr/local/bin/python3

# https://campus.datacamp.com/courses/supervised-learning-with-scikit-learn/

import numpy as np
from pydataset import data
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import cross_val_score, train_test_split

df = data("diamonds")

y = df["price"].values
y = y.reshape(-1, 1)
X = df["carat"].values
X = X.reshape(-1, 1)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

reg = LinearRegression()
cv_scores = cross_val_score(reg, X, y, cv=5)
print(cv_scores)
print(np.mean(cv_scores))

reg.fit(X_train, y_train)
y_pred = reg.predict(X_test)
print("R2:", round(reg.score(X_test, y_test), 3))
print("RMSE:", round(np.sqrt(mean_squared_error(y_test, y_pred)), 2))

# lenear regression minimizes a loss function
# large coefficients lead to overfitting
# regularisation = alter loss function to penalize large coefficients

# Ridge Regression
# Alpha = parameter
