"""
example file

TODO: PCA
  - remove when correlation with target is suspiciously high
  - high n of missings
  - low variance
  - correlation with other features

"""

import pandas as pd
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


def features_w_high_percentage_na(df: object, threshold=0.9) -> list:
    """
    return a list with features ...
    """
    features = [
        c for c in df.columns if df[c].isnull().mean().round(2) > len(df) * threshold
    ]
    return features


def get_features_with_high_feature_imp(
    X, y, n_features: int = 10, fr: float = 0.9
) -> list:
    """
    returns a list of features of length (n_features) with highest
    feature importance based on a fraction (fr) of the provided data.
    """

    _, X_test, _, y_test = train_test_split(X, y, test_size=fr, stratify=y)
    rf = RandomForestClassifier().fit(X_test, y_test)

    df = pd.DataFrame(
        {"cols": list(range(0, X.shape[1])), "importance": rf.feature_importances_}
    ).sort_values("importance", ascending=False)

    print(df)

    return df.head(n_features).cols.to_list()


X, y = make_classification(n_samples=50_000, n_informative=2, weights=[0.95])

print(get_features_with_high_feature_imp(X, y))
