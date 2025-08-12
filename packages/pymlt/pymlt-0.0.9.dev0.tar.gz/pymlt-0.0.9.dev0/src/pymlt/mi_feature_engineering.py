"""
Functions that create new relevant features and improve current features. To track our effort we add nf_ to each
new or modified feature.
"""

import numpy as np
import pandas as pd
from src.features.pipeline_decorator import log_decorator


@log_decorator
def to_dummies(df: pd.DataFrame, list_of_variables: list) -> pd.DataFrame:
    """
    Wrapper around Pandas` get_dummies, convenient to extend for future purposes.

    Parameters
    ----------
    df : dataframe
        Input data including the variables to be transformed.
    list_of_variables : list
        List with variable names that correspond to the column names in the input data.

    Returns
    -------
    df_return : dataframe
        The extended dataframe with the transformed dummy variables and without the original variables.
    """
    df_return = pd.get_dummies(df, columns=list_of_variables, prefix="nf_")

    return df_return


@log_decorator
def to_numeric(df: pd.DataFrame, list_of_variables: list) -> pd.DataFrame:
    """
    Transforms categorical- to numerical variables.

    Parameters
    ----------
    df : dataframe
        Input data including the variables to be transformed.
    list_of_variables : list
        List with variable names that correspond to the column names in the input data.

    Returns
    -------
    df : dataframe
        Dataframe with the transformed variables. Please note that the original variables are overwritten.
    """
    for col in list_of_variables:
        df[col] = df[col].astype("float")

    return df


@log_decorator
def klantensevice_ind(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates an indicator variable for contact_lst_jr_aant_freq to neutralize the skewness.

    Parameters
    ----------
    df : dataframe

    Returns
    -------
    df : dataframe
        The extended dataframe with the additional indicator.
    """
    df["nf_contact_lst_jr_aant_ind"] = np.where(
        df["contact_lst_jr_aant_freq"] >= 1, 1, 0
    )

    return df


@log_decorator
def freq_to_ind(df: pd.DataFrame, list_of_variables: list) -> pd.DataFrame:
    """
    Adds indicator variables based on frequency variables with a highly dominant class. This function can be used
    together with the freq_insight() function from the data_exploration.py module.

    Parameters
    ----------
    df : dataframe
        Input data including the variables to be transformed.
    list_of_variables : list
        List with variable names that correspond to the column names in the input data.

    Returns
    -------
    df : dataframe
        Dataframe with the transformed variables.
    """
    for feature in list_of_variables:
        df["nf_" + feature] = np.where(df[feature] > 0, 1, 0)

    return df


@log_decorator
def sqrt_transformer(df: pd.DataFrame, list_of_variables: list) -> pd.DataFrame:
    """
    Applies a square root transformation on features to decrease the skewness.

    Parameters
    ----------
    df : dataframe
        Input data including the variables to be transformed.
    list_of_variables : list
        List with variable names that correspond to the column names in the input data.

    Returns
    -------
    df : dataframe
        Dataframe with the transformed variables.
    """
    for feature in list_of_variables:
        df["nf_" + feature] = np.sqrt(df[feature])

    return df


@log_decorator
def sustainability_sum(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sums indicators which refer to a conscious decision of the consumer to buy a sustainable product like solar energy.

    Parameters
    ----------
    df : dataframe
        Input data including the sparse indicators.

    Returns
    -------
    df : dataframe
        The dataframe including the sum of the rows of the relevant indicator variables.
    """
    sustainable_indicators = [
        "ele_bron_wind_nl_ind",
        "ele_bron_wind_eu_ind",
        "ele_bron_zon_ind",
        "gas_bron_ecogas_ind",
    ]
    df["nf_sustainable_sum"] = np.sum(df[sustainable_indicators], axis=1)

    return df


@log_decorator
def sustainability_interest_web(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sums indicators which refer to an interest in sustainability on the Eneco webpage.

    Parameters
    ----------
    df : dataframe
        Input data including the sparse indicators.

    Returns
    -------
    df : dataframe
        The dataframe including the sum of the rows of the relevant indicator variables.
    """
    sustainable_interest_ind = [
        "web_url_toon_lst_jr_ind",
        "web_url_zonpv_lst_jr_ind",
        "web_url_stukjezon_lst_jr_ind",
        "web_url_verhuizen_lst_jr_ind",
        "web_url_verbruik_lst_jr_ind",
        "web_url_duurzam_ons_lst_jr_ind",
    ]
    df["nf_sustainable_web"] = np.sum(df[sustainable_interest_ind], axis=1)

    return df


@log_decorator
def log_transform(df: pd.DataFrame, list_of_variables: list) -> pd.DataFrame:
    """
    Applies a natural logarithm transformation on features to decrease the skewness. Values <= 0 are transformed
    to positive in order for the natural logarithm to work.

    Parameters
    ----------
    df : dataframe
        Input data including the variables to be transformed.
    list_of_variables : list
        List with variable names that correspond to the column names in the input data.

    Returns
    -------
    df : dataframe
        Dataframe with the transformed variables.
    """
    for col in list_of_variables:
        temp_col = np.where(df[col] <= 0, 0.01, df[col])
        df["nf_" + col + "_log"] = np.log(temp_col)

    return df
