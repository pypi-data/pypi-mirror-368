#!/usr/local/bin/python3

from sklearn.cluster import KMeans
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

X_train, y_train = load_iris(return_X_y=True)
X_test, y_test = load_iris(return_X_y=True)


km = KMeans(n_clusters=10).fit(X_train)
print(km.predict(X_test))
print(km.score(X_test, y_test))


pipeline = Pipeline(
    [
        # ("kmeans", KMeans(n_clusters=3)),
        ("log_reg", LogisticRegression(max_iter=200))
    ]
)

pipeline.fit(X_train, y_train)


print(pipeline.predict(X_test))
print(pipeline.score(X_test, y_test))
