#!/usr/local/bin/python3

import re

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler

df = pd.DataFrame(
    {
        "X1": [1.0, 2.4, 3.3, 2.0, 3.6, 3.0, 1.4, 3.3, 2.8, 3.1],
        "X2": [1.0, 2.4, 3.3, 30.1, 1.8, 3.0, 1.4, 3.3, 2.8, 3.1],
        "X3": ["a", "b", "b", "a", "b", "a", "b", "b", "a", "b"],
        "X4": ["i", "i", "j", "j", np.nan, "i", "i", "k", "k", "i"],
        "y": [1, 0, 1, 0, 0, 0, 1, 1, 1, 0],
        "dt": [
            "2020-01-01",
            "2020-02-02",
            "2020-03-13",
            "2020-01-22",
            "2020-03-21",
            "2020-01-11",
            "2020-03-01",
            "2020-04-01",
            "2020-04-11",
            "2020-01-07",
        ],
        "tx": [
            "0.8 miles",
            "2.8 miles",
            "1.8 miles",
            "0.8 miles",
            "0.8 miles",
            "0.8 miles",
            "0.8 miles",
            "0.8 miles",
            "0.8 miles",
            "0.8 miles",
        ],
    }
)

# pd data types: object, int64, float64, datatime64
print(df.dtypes)

df = df.dropna().reset_index()  # note reset index!!
# df = df.drop("X4", axis=1)
print(df.isnull().sum())
df["X1_check"] = df["X1"].notnull()
print(df)

print(df["X1"].var())
print(df["X2"].var())
# df['X2'] = np.log(df['X2'])  # apply log normalization
# print(df['X1'].var())
# print(df['X2'].var())
print(df)

# StandardScaler scales all numeric vars to same variance
ss = StandardScaler()
df_subset = df[["X1", "X2"]]
df_subset = pd.DataFrame(ss.fit_transform(df_subset), columns=["X1", "X2"])
df["X1"] = df_subset[["X1"]]
df["X2"] = df_subset[["X2"]]
print(df["X1"].var())
print(df["X2"].var())

X = df[["X1", "X2"]]
y = df["y"]

# stratify by providing the name of the y column
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.33, random_state=42, stratify=y
)

# knn
knn = KNeighborsClassifier(n_neighbors=4)
knn.fit(X, y)
print(knn.predict(X))

# label encoder
enc = LabelEncoder()
df["X3_enc"] = enc.fit_transform(df["X3"])

# create dummies
df = pd.concat([df, pd.get_dummies(df["X4"])], axis=1)

# get mean of two columns
df["mean_X1_X2"] = df.apply(lambda row: row[["X1", "X2"]].mean(), axis=1)

# working with dates
df["dt"] = pd.to_datetime(df["dt"])
df["dt_day"] = df["dt"].apply(lambda row: row.day)
df["dt_month"] = df["dt"].apply(lambda row: row.month)
print(df[["dt", "dt_day", "dt_month"]])

# regex
# \d+ = search for digits and return all
# \. = rearch for .
# \d+ = idem
pattern = re.compile(r"\d+\.\d+")
df["tx_ext"] = re.match(pattern, "0.8 miles").group(0)
print(df[["tx", "tx_ext"]])


df2 = pd.DataFrame(
    {
        "y": ["a", "b", "b", "a", "b", "a", "b", "b", "a", "b"],
        "X": [
            "bla bla bla",
            "bla bla bla",
            "bla bla bla",
            "bla bla bla",
            "bla bla bla",
            "bla bla bla",
            "bla bla bla",
            "bla bla bla",
            "bla bla bla",
            "bla bla bla",
        ],
    }
)
print(df2)

# tf/idf = term frequency / inverse document frequency
tfidf_vec = TfidfVectorizer()
text_tfidf = tfidf_vec.fit_transform(df2["X"])
y = df2["y"]

X_train, X_test, y_train, y_test = train_test_split(text_tfidf.toarray(), y, stratify=y)

# naive bayes works good with text
nb = GaussianNB()
nb.fit(X_train, y_train)
# print(nb.score(X_test, y_test))

# - redundant features: duplicates or highly correlated ones
# check for correlation
print(df.corr())
