#!/usr/local/bin/python3

# https://campus.datacamp.com/courses/supervised-learning-with-scikit-learn/

import numpy as np
from pydataset import data
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

df = data("diamonds")
df["price_cat"] = np.where(df["price"] > 17000, 1, 0)
print(df.head(5))
print(df["price_cat"].value_counts())

# construct clf
# sk models are classes
# sk takes a numpy array or pd dataframe
# all features must be numerical, not categorical
# features cannot have na's
# tagets needs to be a single column

df = df[["cut", "depth", "table", "x", "y", "z"]]
y = df["cut"].values
X = df.drop("cut", axis=1).values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)
print(X_train[1:5, :])
X_train_new = SelectKBest(chi2, k=2).fit_transform(X_train, y_train)
print(X_train_new[1:5, :])

# scaler = StandardScaler()
# scaler.fit(X_train)
# X_train = scaler.transform(X_train)
# X_test = scaler.transform(X_test)


clf = KNeighborsClassifier(n_neighbors=3)  # create class
clf.fit(X_train, y_train)  # fit/train model
y_pred = clf.predict(X_test)  # returns predictions
print(clf.score(X_test, y_test))  # check accuracy of clf
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

for i in range(0, 31, 3):
    if i == 0:
        continue
    knn = KNeighborsClassifier(n_neighbors=i)
    knn.fit(X_train, y_train)
    pred_i = knn.predict(X_test)
    print(i, round(100 * np.mean(pred_i != y_test), 2))
