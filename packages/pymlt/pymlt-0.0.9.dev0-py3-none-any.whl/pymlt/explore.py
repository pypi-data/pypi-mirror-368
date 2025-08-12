"""
TODO: include feature selection?
 - drop features with lot of missing data
 - drop faatures with low variantion
 - check for pairwise correlation
 - check for correlation with target
 - forward / backward / stepwise selection
 - set feature importance threshold in e.g. randomForest
 - dimension reduction via PCA / Factor Analysis
"""

import pandas as pd

from src import utils

_logger = utils.logging.getLogger(__name__)


class Understand:
    """
    data understand class
    init class with a dataframe that contains columns with feature_ and a column called label
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.X = df.filter(like="feature_")
        self.y = df["label"]
        self._validate()
        self.info()

    def __str__(self) -> str:
        """
        string representation
        """
        return "class containing data and data understanding methods"

    def __repr__(self) -> str:
        """
        object representation
        """
        return "class containing data and data understanding methods"

    def _validate(self):
        if not isinstance(self.df, pd.DataFrame):
            raise TypeError("df is not a pandas dataframe")

        if not isinstance(self.X, pd.DataFrame):
            raise TypeError("X is not a pandas dataframe")

        if not isinstance(self.y, pd.Series):
            raise TypeError("y is not a pandas series")

        if len(self.X) == 0:
            raise ValueError("X is empty")

        if len(self.y) == 0:
            raise ValueError("y is empty")

        if not self.y.isin([0, 1]).all():
            raise ValueError("y incorrect value in y")

        if len(self.X) != len(self.y):
            raise ValueError("X and y not same length")

    def info(self):
        """
        logs info on the training data provided
        """
        _logger.info(f"features set: {self.X.columns.to_list()}")
        _logger.info(f"n samples: {len(self.X)}")
        _logger.info(f"n features: {len(self.X.columns)}")
        _logger.info(f"n classes in y: {len(self.y.unique())}")
        _logger.info(f"frac missing in y: {self.y.isna().mean()}")
        _logger.info(f"dist in y: {dict(self.y.value_counts(normalize=True).round(2))}")

    def get_x(self):
        return self.X

    def get_y(self):
        return self.y
