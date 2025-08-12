#!/usr/local/bin/python3

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def load_data(n=1000, f=6):
    """load training data"""
    X, y = make_classification(n_samples=n, n_features=f)
    df = pd.DataFrame(X, y)
    df = df.rename(columns=lambda x: "feature_" + str(x))
    df = df.reset_index().rename(columns={"index": "label"})
    return df


"""
PCA
- part of sklearn
- has both fit and transform

Step 1:
 - 1.) rotate features along axis w/ mean = 0, so variance can be compared
 - 2.) principal components =  directions along which the the data varies
 - 3.) intrinsic dimensions = components (PCA features) with high variance
 - n intrinsic dimensions = n features needed to approximate dataset
 - note that no info is lost in step 1; df has same dimensions
Step 2:
 - reduce dimensions
 - remove noise ...

"""

df = load_data(n=100, f=20).drop(columns=["label"]).to_numpy()

scaler = StandardScaler()
pca = PCA(n_components=5)  # reduce to 5 components
# pca = PCA(n_components=.95) # reduce to n components to get 95% explained variance
pipeline = make_pipeline(scaler, pca)
pipeline.fit(df)

features = range(pca.n_components_)
variance = pca.explained_variance_
plt.bar(features, variance)
plt.show()

df_new = pipeline.transform(df)
print(df.shape)
print(df_new.shape)
