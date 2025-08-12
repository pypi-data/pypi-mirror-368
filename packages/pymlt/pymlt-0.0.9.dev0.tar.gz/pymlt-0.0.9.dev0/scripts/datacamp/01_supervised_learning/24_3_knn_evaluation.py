#!/usr/local/bin/python3

# https://campus.datacamp.com/courses/supervised-learning-with-scikit-learn/

import numpy as np
from pydataset import data
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

df = data("diamonds")
df["price_cat"] = np.where(df["price"] > 17000, 1, 0)

X = df[["x", "y", "z"]].values
y = df["price_cat"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

knn = KNeighborsClassifier(n_neighbors=6)  # create class
knn.fit(X_train, y_train)  # fit/train model
y_pred = knn.predict(X_test)  # returns predictions
print(knn.score(X_test, y_test))  # check accuracy of clf

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))
