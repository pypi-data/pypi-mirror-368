#!/usr/local/bin/python3

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pydataset import data
from sklearn.cluster import KMeans
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer, StandardScaler

df = data("iris")
X = df.iloc[:, 0:4]

n_cl, inertia = [], []
for i in range(2, 8):
    km = KMeans(n_clusters=i).fit(X)
    n_cl.append(i)
    inertia.append(round(km.inertia_, 5))

results = pd.DataFrame({"n_clusters": n_cl, "inertia": inertia})

# trade off between n_clusers and inertia
sns.lineplot(
    data=results, x="n_clusters", y="inertia", linewidth=1, markersize=5, marker="o"
)
plt.show()


# difference between standard scaler and normalizer?
scaler = StandardScaler()
normalizer = Normalizer()

kmeans = KMeans(n_clusters=3)
pipeline = make_pipeline(scaler, kmeans)
pipeline.fit(X)
df["preds"] = pipeline.predict(X)
print(pd.crosstab(df["preds"], df["Species"]))

kmeans = KMeans(n_clusters=3)
pipeline = make_pipeline(normalizer, kmeans)
pipeline.fit(X)
df["preds"] = pipeline.predict(X)
print(pd.crosstab(df["preds"], df["Species"]))
