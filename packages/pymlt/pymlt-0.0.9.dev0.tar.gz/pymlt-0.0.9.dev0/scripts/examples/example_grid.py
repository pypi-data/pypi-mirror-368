import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, PolynomialFeatures
from sklearn.svm import SVC


def generate_data(n: int = 1_000) -> pd.DataFrame:
    """
    generates data
    """
    df = pd.DataFrame(
        {
            "feature_num1": np.random.randint(1, 12, n),
            "feature_num2": np.random.uniform(500, 3500, n),
            "feature_cat1": np.random.choice(["value_1", "value_2"], n),
            "feature_cat2": np.random.choice(["value_3", "value_4"], n),
            "label": np.random.choice(["cat1", "cat2"], n),
        }
    )

    y = df["label"]
    x = df.filter(like="feature_")

    return train_test_split(x, y, test_size=0.2, random_state=42)


def create_pipeline():
    return Pipeline(
        steps=[
            (
                "ct",
                ColumnTransformer(
                    [
                        (
                            "onehot",
                            OneHotEncoder(drop="first"),
                            ["feature_cat1", "feature_cat2"],
                        ),
                        ("pf", PolynomialFeatures(2), ["feature_num1", "feature_num2"]),
                    ],
                    remainder="passthrough",
                ),
            ),
            ("scaler", MinMaxScaler()),
            ("model", DummyClassifier()),
        ]
    )


def search_parameters():
    return [
        {
            "model": [SVC()],
            "model__kernel": ["linear", "poly", "sigmoid"],
            "model__gamma": ["scale", "auto"],
            "ct__pf__degree": (1, 2, 3),
        },
        {
            "model": [RandomForestClassifier()],
            "model__n_estimators": [100, 200],
            "model__max_depth": [2, 3, 4, 5],
            "model__min_samples_split": [5, 6, 7, 8],
            "ct__pf__degree": (1, 2, 3),
        },
    ]


def predict():
    x_train, x_test, y_train, y_test = generate_data(800)
    pipeline = create_pipeline()
    parameters = search_parameters()
    model = GridSearchCV(pipeline, parameters, cv=5, scoring="accuracy")
    model.fit(x_train, y_train)
    best_model = model.best_estimator_
    print(model.best_score_)
    return best_model.predict(x_test)


if __name__ == "__main__":
    pred = predict()
    print(pred)
