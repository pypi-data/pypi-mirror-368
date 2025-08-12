import pandas as pd


class Understand:
    def __init__(self, df: pd.DataFrame(), features: list[str], target: str):
        self.df = df
        self.features = features
        self.target = target

        # auto trigger functions
        self.init_logging()
        self._validate_df()

    def __str__(self) -> str:
        # string representation
        return "class containing data and data understanding methods"

    def __repr__(self) -> str:
        # object representation
        return "class containing data and data understanding methods"

    def init_logging(self):
        # logger
        logger.info("Understand class instantiated")

    def _validate_df(self):
        if not isinstance(self.df, pd.DataFrame):
            raise TypeError("Your df is not a pandas dataframe")

        if len(self.df) == 0:
            raise ValueError("Your df has 0 rows")

        if len(self.df.columns) == 0:
            raise ValueError("Your df has 0 columns")

        if self.target not in self.df.columns.tolist():
            raise ValueError(
                f"Target variable '{self.target}' not found in the provided df"
            )

    def info(self):
        # print info
        print(f"class contains df w/ {len(self.df)} lines")
        print(f"class contains df w/ {len(self.features)} features: {self.features}")
        print(f"class contains df w/ target: {self.target}")

    def df_head(self) -> pd.DataFrame():
        return self.df.head()

    def understand_target(self) -> pd.DataFrame():
        """
        Functionality to check for missings in provided dataframe
        :return: DataFrame with counts and percentages per class in target variable
        """
        result_count = pd.DataFrame({"count": self.df[self.target].value_counts()})
        result_percentage = pd.DataFrame(
            {"percentage": self.df[self.target].value_counts(normalize=True)}
        )
        result = result_count.merge(
            result_percentage, left_index=True, right_index=True
        )
        return result

    def missings(self):
        perc_full_lines = round(
            self.df.notnull().all(axis="columns").sum() / len(self.df) * 100
        )
        print(f"rows without missings: {perc_full_lines}%")
