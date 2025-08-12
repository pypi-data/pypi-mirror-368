import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def features_w_high_percentage_na(df: object, threshold=0.9) -> list:
    """..."""
    features = [
        c for c in df.columns if df[c].isnull().mean().round(2) > len(df) * threshold
    ]
    return features


def features_w_high_rf_importance(df, n_features=5, fr=0.2) -> list:
    """
    returns a list of features with highest importance of
    length (n_features) from a dataframe (df), based on a fraction (fr)
    of the df provided. Deals with missings using mean imputation and features
    importance is based on a RandomForestClassifier
    """
    df = df.sample(frac=fr)
    y = df["label"]
    X = df.filter(like="feature_")
    imp_mean = SimpleImputer(missing_values=np.nan, strategy="mean")
    rf = RandomForestClassifier()
    pipe = make_pipeline(imp_mean, rf)
    pipe.fit(X, y)
    df_imp = pd.DataFrame(rf.feature_importances_, index=X.columns)
    df_imp = df_imp.rename(columns={0: "imp"}).sort_values("imp", ascending=False)
    features = df_imp.head(n_features).index.to_list()
    return features


def features_w_high_correlation_w_label(df, t=0.95) -> list:
    """..."""
    dff = df.filter(like="feature_").reset_index(drop=True)
    scaled = StandardScaler().fit_transform(dff)
    dff = pd.DataFrame(scaled, columns=dff.columns)
    dfl = df[["label"]]
    dff.reset_index(drop=True, inplace=True)
    dfl.reset_index(drop=True, inplace=True)
    df = pd.concat([dfl, dff], axis=1)
    df_corr = df.corr().abs()
    df_corr = df_corr.reset_index().loc[:, ["index", "label"]]
    df_corr = df_corr.rename(columns={"index": "feature", "label": "cwl"})
    df_corr = df_corr[df_corr["feature"] != "label"]
    df_corr = df_corr[df_corr["cwl"] > t].values.tolist()
    return df_corr


def features_w_high_correlation_w_other_features(df: pd.DataFrame, t=0.95) -> list:
    """..."""
    df = df.filter(like="feature_")
    scaled = StandardScaler().fit_transform(df)
    df = pd.DataFrame(scaled, columns=df.columns)
    df_corr = df.corr().abs()
    df_corr = pd.DataFrame(np.triu(df_corr, 1), columns=df_corr.columns)
    features = [i for i in df_corr.columns if (df_corr[i] > t).any()]
    # todo: keep highest correlation - https://www.youtube.com/watch?v=ioXKxulmwVQ
    return features
