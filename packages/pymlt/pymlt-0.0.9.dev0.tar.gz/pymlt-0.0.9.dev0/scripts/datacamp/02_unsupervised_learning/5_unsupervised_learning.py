#!/usr/local/bin/python3

import pandas as pd
from sklearn.datasets import make_classification
from sklearn.decomposition import NMF


def load_data(n=1000, f=6):
    """load training data"""
    X, y = make_classification(n_samples=n, n_features=f)
    df = pd.DataFrame(X, y)
    df = df.rename(columns=lambda x: "feature_" + str(x))
    df = df.reset_index().rename(columns={"index": "label"})
    return df


"""
non-negative matrix factorization (NMF)
interpretable dimension reduction technique
only applicable to non-negative sample features

For documents (text, word counts); NMF components represents a topic
For images, NMF components are part of images
- grayscale images of same size can be encoded / flatned as 2D array
- where every sample is a picture and every column a pixel

"""

df = load_data(n=100, f=20).drop(columns=["label"]).to_numpy()
df = abs(df)  # non-negative

nmf = NMF(n_components=2, max_iter=1000)
nmf.fit(df)

df_new = nmf.transform(df).round(4)
print(df_new.shape)
