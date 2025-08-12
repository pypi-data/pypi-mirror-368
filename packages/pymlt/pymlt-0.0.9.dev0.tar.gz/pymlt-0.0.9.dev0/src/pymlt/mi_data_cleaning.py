"""
Data cleaning functions focused on removing non-informative features and missing values imputation.
"""

import pandas as pd
from sklearn.feature_selection import VarianceThreshold
from src.features.pipeline_decorator import log_decorator


@log_decorator
def copy_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Copies the input dataset to prevent the original data from being affected, especially useful in a pandas pipeline.

    Parameters
    ----------
    df : dataframe

    Returns
    -------
    df : dataframe
    """
    return df.copy()


@log_decorator
def drop_missings(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """
    Drops variables with a percentage missing above the threshold. Imputation of these missing values should
    be considered before dropping the full variables.

    Parameters
    ----------
    df : dataframe
        Input data.
    threshold : float
        Float between 0 and 1 which corresponds to the percentage of missing values per variable.

    Returns
    -------
    df: dataframe
        The dataframe without the dropped variables based on the threshold.
    """
    if (threshold > 1) | (threshold < 0):
        raise ValueError("Choose a threshold between 0 and 1")
    else:
        try:
            missings = df.isna().mean().reset_index()
            missings.columns = ["column", "perc_missings"]
            drop_list = missings[missings["perc_missings"] >= threshold][
                "column"
            ].tolist()
            return df.drop(columns=drop_list, axis=1)
        except AttributeError:
            print("You must use a Pandas DataFrame as input")


@log_decorator
def nzv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes numeric features with zero variance based on the VarianceThreshold method from scikit-learn.

    Parameters
    ----------
    df : dataframe
        Input data with numeric variables although there is a check on numeric variables in the function.

    Returns
    -------
    df_return : dataframe
        The dataframe without the zero-variance variables.

    """
    df_include = df.select_dtypes(include=["int64", "float64"])
    df_exclude = df.select_dtypes(exclude=["int64", "float64"])

    selector = VarianceThreshold()
    selector.fit(df_include)

    nzv_return = df_include[df_include.columns[selector.get_support(indices=True)]]
    df_return = pd.concat([nzv_return, df_exclude], axis=1, sort=False)

    return df_return


@log_decorator
def median_impute(df: pd.DataFrame, list_of_variables: list) -> pd.DataFrame:
    """
    Imputes the median of the variable for all missing values in the variables which are listed in list_of_variables.

    Parameters
    ----------
    df : dataframe
        Input data including variables with missing data.
    list_of_variables : list
        List with variable names that correspond to the column names in the input data.

    Returns
    -------
    df_return : dataframe
        The complete dataframe including the imputed values.
    """
    df_missing = df[list_of_variables].fillna(df[list_of_variables].median())
    df_return = pd.concat(
        [df.drop(list_of_variables, axis=1), df_missing], axis=1, sort=False
    )

    return df_return


@log_decorator
def fill_na_zero(df: pd.DataFrame, list_of_variables: list) -> pd.DataFrame:
    """
    Fills NaN with 0 (zero), be aware of the practical implications of using zeros for missing values.

    Parameters
    ----------
    df : dataframe
        Input data including categorical variables.
    list_of_variables : list
        List with variable names that correspond to the column names in the input data.

    Returns
    -------
    df : dataframe
        The complete dataframe including the imputed values.
    """
    df_missing = df[list_of_variables].fillna(0)
    df_return = pd.concat(
        [df.drop(list_of_variables, axis=1), df_missing], axis=1, sort=False
    )

    return df_return
