#!/usr/local/bin/python3


import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB

df = pd.DataFrame(
    {
        "y": ["a", "b", "b", "a", "b", "a", "b", "b", "a", "b"],
        "X": [
            "blah blah blah",
            "bla bla bla",
            "bla bla bla",
            "blah blah blah",
            "bla bla bla",
            "blah blah blah",
            "bla bla bla",
            "bla bla bl",
            "blar blar blar",
            "bla bla bla",
        ],
    }
)
print(df)

# tf/idf = term frequency / inverse document frequency
tfidf_vec = TfidfVectorizer()
text_tfidf = tfidf_vec.fit_transform(df["X"])
y = df["y"]

X_train, X_test, y_train, y_test = train_test_split(text_tfidf.toarray(), y, stratify=y)

# naive bayes works good with text
nb = GaussianNB()
nb.fit(X_train, y_train)
print(nb.score(X_test, y_test))
