#!/usr/local/bin/python3

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.manifold import TSNE


def load_data(n=1000, f=6):
    """load training data"""
    X, y = make_classification(n_samples=n, n_features=f)
    df = pd.DataFrame(X, y)
    df = df.rename(columns=lambda x: "feature_" + str(x))
    df = df.reset_index().rename(columns={"index": "label"})
    return df


"""
t-SNE
gain insights from high dimensional data
t-SNE transforms dimensions into 2d visualisation
part of sklearn
only has fit_transform, thus always start over with new samples
learning rate, use between 50 and 200
"""

df = load_data()
model = TSNE(learning_rate=200)
tsne_features = model.fit_transform(df)
print(tsne_features)

xs = tsne_features[:, 0]
ys = tsne_features[:, 1]

plt.scatter(xs, ys, c=df["label"].values, alpha=0.75)
plt.show()
