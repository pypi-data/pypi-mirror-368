import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

X, y = make_classification(
    n_samples=1000,
    n_informative=1,
    n_features=20,
    n_clusters_per_class=1,
    n_redundant=0,
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=12
)

clf = KNeighborsClassifier()
clf.fit(X_train, y_train)
clean_dataset_score = clf.score(X_test, y_test)

for index in range(X.shape[1]):
    X_train_noisy = X_train.copy()
    np.random.shuffle(X_train_noisy[:, index])
    X_test_noisy = X_test.copy()
    np.random.shuffle(X_test_noisy[:, index])
    clf.fit(X_train_noisy, y_train)
    noisy_score = clf.score(X_test_noisy, y_test)
    print(clean_dataset_score - noisy_score, clean_dataset_score, noisy_score)
