#!/usr/local/bin/python3

# https://campus.datacamp.com/courses/supervised-learning-with-scikit-learn/

import matplotlib.pyplot as plt
import pandas as pd
from pydataset import data
from sklearn.linear_model import Lasso

df = data("diamonds")

X = df[["x", "y", "z"]].values
y = df["price"].values

df_columns = pd.DataFrame(df[["x", "y", "z"]].columns.values)

lasso = Lasso(alpha=0.4, normalize=True)
lasso.fit(X, y)
lasso_coef = lasso.coef_
print(lasso_coef)

plt.plot(range(len(df_columns)), lasso_coef)
plt.xticks(range(len(df_columns)), df_columns.values, rotation=60)
plt.margins(0.02)
plt.show()
