#!/usr/local/bin/python3

# https://campus.datacamp.com/courses/supervised-learning-with-scikit-learn/

import numpy as np
from pydataset import data
from sklearn.neighbors import KNeighborsClassifier

df = data("diamonds")
df["high"] = np.where(df["price"] > 17000, 1, 0)

# construct clf
# sk models are classes
# sk takes a numpy array or pd dataframe
# all features must be numerical, not categorical
# features cannot have na's
# tagets needs to be a single column

X = df[["x", "y", "z"]]
y = df["high"]

knn = KNeighborsClassifier(n_neighbors=6)  # create class
print(knn.fit(X, y))  # fit/train model
print(knn.predict(X))  # returns predictions
print(knn.score(X, y))  # check accuracy of clf
