#!/usr/local/bin/python3

import matplotlib.pyplot as plt
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from sklearn.datasets import make_classification
from sklearn.preprocessing import normalize


def load_data(n=1000, f=6):
    """load training data"""
    X, y = make_classification(n_samples=n, n_features=f)
    df = pd.DataFrame(X, y)
    df = df.rename(columns=lambda x: "feature_" + str(x))
    df = df.reset_index().rename(columns={"index": "label"})
    return df


df = load_data(100, 10)
df_n = normalize(df)

mergings = linkage(df, method="complete")  # distance between furthest samples

labels = df["label"].values
labels_cluster = fcluster(mergings, 6, criterion="distance")


df = pd.DataFrame({"labels": labels, "labels_cluster": labels_cluster})
ct = pd.crosstab(df["labels"], df["labels_cluster"])
print(ct)

dendrogram(mergings, labels=labels_cluster, leaf_rotation=0, leaf_font_size=5)

plt.show()
