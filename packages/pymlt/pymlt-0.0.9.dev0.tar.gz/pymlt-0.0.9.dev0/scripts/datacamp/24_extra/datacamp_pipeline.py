from sklearn.cluster import KMeans
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

X_train, y_train = load_iris(return_X_y=True)
X_test, y_test = load_iris(return_X_y=True)

pipeline = Pipeline(
    [
        ("kmeans", KMeans(n_clusters=5)),
        ("log_reg", LogisticRegression()),
    ]
)
pipeline.fit(X_train, y_train)
score = pipeline.score(X_test, y_test)
print(score)
