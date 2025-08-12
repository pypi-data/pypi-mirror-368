"""
Functions aimed at gaining insights in the structure of the data, the types of variables, and the quality of the data.
"""

import os
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sqlalchemy as sql
import src.features.data_cleaning as data_clean
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split


def set_aside_test_set(
    df: pd.DataFrame, test_size: float = 0.2, random_state: int = 1337
) -> pd.DataFrame:
    """
    Splits the original dataframe in a train- and test set, and writes these sets in zipped format to your project
    folder.

    Attention: this function assumes you are using the MI modeling template and that you currently are in your
    /notebooks folder. You can check this with the os module via os.getcwd().

    **This function will create a new folder and writes files to your local directory.**

    Parameters
    ----------
    df : Dataframe
        Original dataframe freshly imported from the Datawarehouse.
    test_size : float, default = 0.2
        Percentage of the original dataframe that is being set aside as a test set.
    random_state : int, default = 1337
        Fixes the random seed thereby allowing for reproducibility of the analysis.

    Returns
    -------
    train_set : dataframe
        Original dataframe minus the test set.
    """
    train_set, test_set = train_test_split(
        df, test_size=test_size, random_state=random_state
    )

    dir_list = []
    with os.scandir("../..") as entries:
        for entry in entries:
            if entry.is_dir():
                dir_list.append(entry.name.lower())

    if "data" not in dir_list:
        os.mkdir("../../data/")

    test_path = os.path.join("../..", "data", "test_set")
    train_path = os.path.join("../..", "data", "train_set")

    test_set.to_csv(
        test_path, sep=";", encoding="utf-8", index=False, compression="zip"
    )
    train_set.to_csv(
        train_path, sep=";", encoding="utf-8", index=False, compression="zip"
    )

    message = (
        f"Your original dataframe with shape {df.shape} has been divided in two seperate sets:\n"
        f"test_set: {test_set.shape}\n"
        f"train_set: {train_set.shape}\n\n"
        f"Both sets are stored at '{os.path.join('../..', 'data')}' and the train_set is also returned by this function."
    )

    print(message)

    return train_set


def num_visu_avg(df: pd.DataFrame, num_list: list, normal: bool = True, bins: int = 30):
    """
    Visualizing numeric variables without outliers. Either based on the assumption of a normal distribution or without the assumption of a distribution.
    Plots
        - if normal = True, the values within (avarage minus 3*standard deviation) and (average plus 3*standard deviation), red dotted line is the average.
        - if normal = False, the values within (median minus 3*inter quartile range) and (median plus 3*inter quartile range), red dotted line is the median.

    Parameters
    ----------
    df : dataframe
        Dataframe containing numeric variables.
    num_list: list
        List of numeric variables.
    normal: bool
        Boolean, if True assumes normal distribution.
    bins: int
        Number of bins to show in the histogram. Indicates granularity of visualisation.

    Returns
    -------
    None, prints plots.
    """

    fig, axes = plt.subplots(nrows=int(len(num_list) / 2), ncols=2, figsize=(15, 10))
    plt.subplots_adjust(hspace=0.5)
    axes = axes.reshape(-1)

    for idx, name in enumerate(num_list):
        if normal:
            avg = df[name].mean()
            sd = df[name].std()

            if sd > 0:
                df[(df[name] < (avg + 3 * sd)) & (df[name] > (avg - 3 * sd))][
                    name
                ].plot(kind="hist", ax=axes[idx], bins=bins)
                axes[idx].set_title(name)
                axes[idx].axvline(avg, ls="--", color="r")
            else:
                print(
                    f"The figure for {name} can't be shown because the standard deviation = 0"
                )

        else:
            md = df[name].median()
            q1 = df[name].quantile(0.25)
            q3 = df[name].quantile(0.75)
            iqr = q3 - q1

            if iqr > 0:
                df[(df[name] < (md + 3 * iqr)) & (df[name] > (md - 3 * iqr))][
                    name
                ].plot(kind="hist", ax=axes[idx], bins=bins)
                axes[idx].set_title(name)
                axes[idx].axvline(md, ls="--", color="r")
            else:
                print(
                    f"The figure for {name} can't be shown because the Inter Quartile Range = 0"
                )

    plt.show()


def return_dwh_table(
    db_user: str, db_password: str, db_server: str, sql_query: str
) -> pd.DataFrame:
    """
    Creates a connection to a data warehouse, extracts the data, and transforms the data to a Pandas dataframe.
    Please refer to the README how you can import your username, password, and server address in a safe manner.

    Parameters
    ----------
    db_user : str
    db_password : str
    db_server : str
    sql_query : str
        The sql query which should be executed on the database, e.g. 'SELECT * FROM cltv_trainingsset_toon_xsell'

    Returns
    -------
    df : pd.Dataframe
        Input data which can be used to start the data exploration phase.
    """
    engine = sql.create_engine(
        f"oracle+cx_oracle://{db_user}:{db_password}@{db_server}"
    )

    connection = engine.connect()
    df = pd.read_sql(sql=sql_query, con=connection)
    connection.close()

    return df


def postfix_counter(df: pd.DataFrame, return_counter: bool = False):
    """
    Creates a list of postfixes for each column within a dataframe. The postfix is determined by the characters
    after the last underscore (_) of each column name.

    Parameters
    ----------
    df : dataframe
        Input data which contains the columns to be checked on postfixes.
    return_counter : bool, default False
        If true a Counter dictionary is returned instead of a list.

    Returns
    -------
    postfix_list : List or collections.Counter object
    """
    postfix_list = []
    for column in df.columns:
        postfix_list.append(column.split("_")[-1])

    if return_counter:
        postfix_list = Counter(postfix_list)

    return postfix_list


def describe_df(df: pd.DataFrame, dependent_variable: str) -> None:
    """
    Prints a summary of a dataframe which help to give direction to data preparation functions. Currently the following
    characteristics are considered:
    - Number of rows and columns
    - Percentage of ones (1) in the dependent variable
    - A counter of the postfixes
    - Variables with missing values and percentage missing
    - First 5 rows for each object variable

    Parameters
    ----------
    df : dataframe
        Input data which incldues all the variables of interest, including the dependent variable.
    dependent_variable : str
        Column name of the dependent variable which should be part of the input data, for example "y_var".

    Returns
    -------
    NoneType : the result is directly printed to the screen.
    """
    try:
        shape_df = df.shape
        value_dv = df[dependent_variable].value_counts()
        dtype_df = df.dtypes.value_counts()
        missings = df.isna().mean()
        missings = missings.reset_index()
        missings.columns = ["column", "perc_missings"]
        missings_msg = missings[missings["perc_missings"] > 0].sort_values(
            "perc_missings", ascending=False
        )
        postfix_count = postfix_counter(df, return_counter=True)

        message = (
            f"This dataframe has {shape_df[0]} rows and {shape_df[1]} columns.\n\n"
            f"The dependent variable consists of {value_dv[1] / (value_dv[0] + value_dv[1]):.1%} of ones.\n\n"
            f"The variables have the following data types:\n{dtype_df}\n\n"
            f"The postfixes are distributed as follows:\n{postfix_count}\n\n"
            f"The following variables have missing values:\n{missings_msg}\n\n"
        )
        print(message)

    except AttributeError:
        print("You must use a Pandas DataFrame as input")

    return None


def _corr_df_start(df: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function for multicollinearity(), this helper function serves 3 purposes:
    - change all correlation values to absolute
    - keep only the upper half of the correlation matrix, thereby excluding the duplicates
    - rename the standard columns for better interpretability

    Parameters
    ----------
    df : dataframe
        Input data for which each correlation coefficient is calculated.

    Returns
    -------
    corr_start : dataframe
        Dataframe with all the possible pairs and correlations.
    """
    corr_start = df.corr().abs()
    corr_start = corr_start.where(
        np.triu(np.ones(corr_start.shape), k=1).astype(np.bool)
    )
    corr_start = (
        corr_start.stack()
        .reset_index()
        .rename(columns={"level_0": "var_1", "level_1": "var_2", 0: "corr"})
    )

    return corr_start


def _corr_add_y(corr_cutoff: pd.DataFrame, corr_with_y: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function for multicollinearity() which adds the correlation with the dependent variable (y) for each
    variable in each pair.

    Parameters
    ----------
    corr_cutoff : dataframe
        The input data which excluded all correlation pairs below a certain threshold.
    corr_with_y : dataframe
        The input data including the correlation of each variable with the dependent variable.

    Returns
    -------
    cor_cutoff : dataframe
        DataFrame with the correlation coefficients of the dependent variable for each pair of independent variables.
    """
    var_corr_names = [["var_1", "y_corr_var_1"], ["var_2", "y_corr_var_2"]]

    for combination in var_corr_names:
        corr_with_y.columns = combination
        corr_cutoff = pd.merge(corr_cutoff, corr_with_y, how="left")

    return corr_cutoff


def multicollinearity(
    df: pd.DataFrame, cut_off: float = 0.95, dependent_variable: str = "y_var"
) -> pd.DataFrame:
    """
    Returns the pearson correlation coefficient for every pair of variables and the correlation with the dependent
    variable. The variable with the lowest correlation with the dependent variable is suggested to drop since
    highly correlated variables carry the same information, slow down the modeling process and possibly disturb
    the end result.

    Parameters
    ----------
    df : dataframe
        Input data, should only contain numerical variables.
    cut_off : float, default 0.95
        Float between 0 and 1 which determine the correlation cut off.
    dependent_variable : str, default "y_var"
        Column name of the dependent variable which should be part of the dataframe.

    Returns
    -------
    corr_merge : Dataframe with 6 variables:
    - var_1 : first variable of each pair
    - var_2 : second variable of each pair
    - corr : Pearson correlation of the pair
    - y_corr_var_1 : correlation between var_1 and the dependent variable
    - y_corr_var_2 : correlation between var_2 and the dependent variable
    - drop_suggestion : variable suggested to drop based on lowest correlation with the dependent variable
    """
    corr_start = _corr_df_start(df)
    corr_with_y = corr_start[corr_start["var_1"] == dependent_variable].drop(
        "var_1", axis=1
    )

    corr_cutoff = corr_start[corr_start["corr"] > cut_off]
    corr_merge = _corr_add_y(corr_cutoff, corr_with_y)

    return corr_merge.assign(
        drop_suggestion=lambda x: np.where(
            x["y_corr_var_1"] > x["y_corr_var_2"], x["var_2"], x["var_1"]
        )
    )


def postfix_to_column(
    df: pd.DataFrame, postfix: str, dependent_variable: str = "y_var"
) -> list:
    """
    Provides a list of the full variable names including the dependent variable based on the postfix.

    Parameters
    ----------
    df : dataframe
        Input data which should contain columns including postfixes.
    postfix : str
        The postfix string, e.g., 'ind' for indicators, 'freq' for frequency variables.
    dependent_variable : str, default "y_var"
        Column name of the dependent variable which should be part of the dataframe.

    Returns
    -------
    ind_list: list
        A list with all the variables given the postfix and the dependent variable.
    """
    postfix_list = postfix_counter(df, return_counter=False)
    ind_list = df.columns[[item in postfix for item in postfix_list]]

    if dependent_variable:
        return ind_list.insert(0, dependent_variable)

    return ind_list


def odds_ind(
    df: pd.DataFrame, postfix: str = "ind", dependent_variable: str = "y_var"
) -> pd.DataFrame:
    """
    Provides the odds of the dependent variable for each value of the independent indicator variable (0/1).

    These insights can uncover independent variables with a strong association with the dependent variable. Be aware of
    the sum(y) for the independent variables. When (very) low the absolute and relative differences can be misleading.

    Parameters
    ----------
    df : dataframe
        Input data which should include indicator variables and the dependent variable.
    postfix : str, default "ind"
        See postfix_to_column() for more information.
    dependent_variable: str, default "y_var"
        Column name of the dependent variable which should be part of the dataframe.

    Returns
    -------
    return_df : Dataframe with 4 variables, row indexes are the independent variables (indicators):
    - mean(y) for value=0 : mean of the dependent variable for the value 0 in the independent variable
    - sum(y) for value=0 : sum of the dependent variable for the value 0 in the independent variable
    - mean(y) for value=1 : mean of the dependent variable for the value 1 in the independent variable
    - sum(y) for value=1 : sum of the dependent variable for the value 1 in the independent variable
    - abs : absolute difference between mean(y) for value=1 and mean(y) for value=0
    - odds : relative difference between mean(y) for value=1 and mean(y) for value=0
    """
    df = data_clean.nzv(df)  # exclude indicators with only a single value
    ind_list = postfix_to_column(df, postfix, dependent_variable)

    empty_dict = {}
    for col in ind_list:
        empty_dict[col] = list(
            df[ind_list].groupby(col)[dependent_variable].agg(["mean", "sum"]).stack()
        )

    return_df = pd.DataFrame(data=empty_dict.values(), index=empty_dict.keys())
    return_df.columns = [
        "mean(y) for value=0",
        "sum(y) for value=0",
        "mean(y) for value=1",
        "sum(y) for value=1",
    ]

    for col in ["sum(y) for value=0", "sum(y) for value=1"]:
        return_df[col] = return_df[col].astype("int")

    return_df = return_df.assign(
        abs=lambda x: x["mean(y) for value=1"] - x["mean(y) for value=0"],
        odds=lambda x: x["mean(y) for value=1"] / x["mean(y) for value=0"],
    )

    return return_df.sort_values(by="abs", ascending=False)


def freq_insight(df: pd.DataFrame, postfix: str = "freq") -> pd.DataFrame:
    """
    Provides the 5 most prevalent values per variable and the absolute difference between the top 2 values.

    This insight can be used to determine which variables carry very little information or are interesting for
    further feature engineering.

    Parameters
    ----------
    df : dataframe
        Input data which should include the frequency variables.
    postfix : str, default "freq"
        See postfix_to_column() for more information.

    Returns
    -------
    Dataframe with 6 variables, row indexes are the independent variables (frequency variables):
    - 0:4 : cumulative prevalence of the first, second, .. 5th value of each independent variable
    - abs : absolute difference between the two most prevalent values
    """
    freq_list = postfix_to_column(df, postfix, dependent_variable=None)

    empty_dict = {}
    for col in freq_list:
        empty_dict[col] = list(np.cumsum(df[col].value_counts(normalize=True))[:5])

    return_df = pd.DataFrame(data=empty_dict.values(), index=empty_dict.keys())
    return_df = return_df.assign(abs=lambda x: x[1] - x[0])

    return return_df.sort_values(by="abs", ascending=False)


def cat_visu(
    df: pd.DataFrame, postfix: str = "cat", dependent_variable: str = "y_var"
) -> pd.DataFrame:
    """
    Plots the mean of the dependent variable per value per categorical variable.

    This can be used for further feature engineering and selection. Please note that the indexes should be similar
    and not too widespread.

    Parameters
    ----------
    df : dataframe
        Input data which should include the categorical variables and the dependent variable.
    postfix : str
        See postfix_to_column() for more information.
    dependent_variable: str, default "y_var"
        Column name of the dependent variable which should be part of the dataframe.

    Returns
    -------
    visu_df, None : DataFrame and the plot are returned by this function
    """
    cat_list = list(postfix_to_column(df, postfix, None))
    cat_list.remove("energie_label_incl_vrlopig_cat")

    appended_data = []
    for variable in cat_list:
        if variable == "stedelijkheid_cat":
            pd_series = (
                df.groupby("stedelijkheid_cat")[dependent_variable]
                .mean()
                .reindex([1.0, 2.0, 3.0, 4.0, 5.0])
            )
        else:
            pd_series = df.groupby(variable)[dependent_variable].mean()
        appended_data.append(pd_series)

    visu_df = pd.concat(appended_data, axis=1)
    visu_df.columns = cat_list

    visu_df.plot(
        kind="barh",
        subplots=True,
        layout=(3, 3),
        figsize=(15, 10),
        legend=False,
        title="mean of the dependent variable\nper categorical value",
    )

    return visu_df


def num_visu(df: pd.DataFrame, postfix: str = "num") -> None:
    """
    Plots the distribution of every numeric variable in the dataset.

    Parameters
    ----------
    df : dataframe
        Input data which should include the numerical variables.
    postfix : str
        See postfix_to_column() for more information.

    Returns
    -------
    None : A matplotlib.pyplot is directly plotted.
    """
    num_list = postfix_to_column(df, postfix, None)

    fig, axes = plt.subplots(nrows=4, ncols=2, figsize=(15, 10))
    plt.subplots_adjust(hspace=0.5)
    axes = axes.reshape(-1)

    for idx, name in enumerate(num_list):
        plt.figure()
        df[name].plot(kind="hist", ax=axes[idx], bins=25)
        axes[idx].set_title(name)

    return None


def pca_visu(df: pd.DataFrame, dependent_variable: str = "y_var"):
    """
    Plots the cumulative variance vs. the number of dimensions in the data set by using a PCA transformation.

    Parameters
    ----------
    df : DataFrame
        Input data which should be non-missing and numeric although the function handles these aspects as well.
    dependent_variable: str, default "y_var"
        Column name of the dependent variable which should be part of the dataframe.

    Returns
    -------
    pca: scikit-learn PCA object including all its attributes.
    """
    x = df.drop(dependent_variable, axis=1)
    x = x.select_dtypes(include=["int64", "float64"])
    x = x.dropna(axis=1, how="any")

    pca = PCA()
    pca.fit(x)

    cumulative_variance = pd.Series(np.cumsum(pca.explained_variance_ratio_))

    variance_plot = cumulative_variance.plot(
        kind="line",
        figsize=(16, 8),
        xticks=np.arange(0, 400, 25),
        yticks=np.arange(0, 1.1, 0.1),
    )
    variance_plot.set_xlabel("dimensions", size=15)
    variance_plot.set_ylabel("explained variance", size=15)

    return pca
