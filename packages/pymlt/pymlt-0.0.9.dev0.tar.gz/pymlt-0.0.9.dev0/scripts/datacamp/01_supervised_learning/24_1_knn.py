#!/usr/local/bin/python3

# https://campus.datacamp.com/courses/supervised-learning-with-scikit-learn/

from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

digits = datasets.load_digits()

print(digits.keys())
# print(digits.DESCR)

X = digits.data
y = digits.target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

knn = KNeighborsClassifier(n_neighbors=7)

knn.fit(X_train, y_train)

print(round(knn.score(X_test, y_test), 4))


# Loop over different values of k
for i in range(1, 10):
    knn = KNeighborsClassifier(n_neighbors=i)
    knn.fit(X_train, y_train)

    print(i, "train:", round(knn.score(X_train, y_train), 5))
    print(i, "test :", round(knn.score(X_test, y_test), 5))
