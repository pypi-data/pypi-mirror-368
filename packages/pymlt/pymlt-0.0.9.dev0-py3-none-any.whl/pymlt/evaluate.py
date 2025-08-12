import time

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score

from src import utils

_logger = utils.logging.getLogger(__name__)


class ModelEvaluation:
    """
    creates class with model evaluation info; retrieve info using the get_ methods
    """

    def __init__(self, pipeline, X_test: pd.DataFrame, y_test: pd.Series):
        self.evaluation_metrics = {}
        self.pipeline = pipeline
        self.X_test = X_test
        self.y_test = y_test
        self._validate()
        self._create_model_evaluation()
        self._create_model_shap()

    def _validate(self):
        if len(self.X_test) == 0:
            raise ValueError("X is empty")

    def _create_model_evaluation(self):
        # use pipeline to predict on X_test
        self.y_test_pred = self.pipeline.predict(self.X_test)
        self.y_test_proba = self.pipeline.predict_proba(self.X_test)[:, 1]
        # calculate accuracy
        self.accuracy = round(accuracy_score(self.y_test, self.y_test_pred), 6)
        self.evaluation_metrics.update({"accuracy": self.accuracy})

    def _create_model_shap(self):
        pass

    def info(self):
        _logger.info(f"accuracy score on test: {self.accuracy}")

    def get_accuracy(self):
        return self.accuracy

    def get_metrics(self):
        return self.evaluation_metrics

    def get_model_lift_table(self):
        """
        takes y and y_proba and returns df with model lift
        """
        # todo: check if self.y_test is numeric
        df = pd.DataFrame({"y": self.y_test, "y_proba": self.y_test_proba})
        print(df)
        df = df.sort_values(by="y_proba", ascending=False)
        n_true = df.y.sum()
        table_p, table_g, table_l = [], [], []
        for i in range(1, 11, 1):
            i = i / 10
            n_true_p = df.head(round(i * len(df))).y.sum()
            gain = n_true_p / n_true
            lift = gain / i
            table_p.append(i)
            table_g.append(gain)
            table_l.append(lift)
        return pd.DataFrame({"p": table_p, "gain": table_g, "lift": table_l})


class GrafanaLog:
    """
    creates class for grafana logging during predict phase
    """

    def __init__(self):
        self.grafana_dict = {}
        self.start_time = time.perf_counter()
        self.df = pd.DataFrame()
        self.features = []
        self.label = "label"

    def add_df(self, df: pd.DataFrame):
        """
        adds df with features (and labels)
        """
        self.df = df
        self.grafana_dict.update({"n_rows": len(self.df)})

    def add_feature_descriptives(self):
        """
        adds descriptives of features to grafana_dict dict
        """

        assert len(self.df) > 0, "no df added yet"

        # set features
        self.features = self.df.filter(like="feature_").columns.to_list()

        for f in self.features:
            fname = f.replace(" ", "_")

            self.grafana_dict.update(
                {f"{fname}_frac_missing": self.df[f].isna().mean()}
            )

            if self.df[f].dtypes == "float":
                self.grafana_dict.update({f"{fname}_mean": np.mean(self.df[f])})
                self.grafana_dict.update({f"{fname}_std": np.std(self.df[f])})
                self.grafana_dict.update({f"{fname}_var": np.var(self.df[f])})
            else:
                self.grafana_dict.update({f"{fname}_nunique": self.df[f].nunique()})

    # def add_pred_descriptives(self):
    #
    #     pred: str = "y_proba":
    #     """
    #     adds descriptives of predictions to grafana_dict dict
    #     """``
    #
    #
    # def add_pred_descriptives(self), pred: str = "y_proba":
    #     """
    #     adds descriptives of predictions to grafana_dict dict
    #     """
    #
    #     assert len(self.df) > 0, "no df added yet"
    #
    #     # set label
    #     self.label = label
    #
    #     # add overall mean to grafana_dict
    #     self.grafana_dict.update({f"label_mean": np.mean(self.df[self.label])})
    #
    #     # order predictions
    #     self.df = self.df.sort_values(self.label).reset_index(drop=True)
    #
    #     # add group mean to grafana_dict
    #     self.df["group"] = (np.arange(0, len(self.df), 1) / len(self.df) * 10).astype(
    #         int
    #     ) + 1
    #     groups = list(self.df.group.unique())
    #
    #     for g in groups:
    #         self.grafana_dict.update(
    #             {
    #                 f"label_mean_group_{g}": self.df.query(f"group == {g}")[
    #                     self.label
    #                 ].mean()
    #             }
    #         )
    #
    #     # add frac size of bins to grafana_dict
    #     bins = [
    #         (0, 0.1),
    #         (0.1, 0.2),
    #         (0.2, 0.3),
    #         (0.3, 0.4),
    #         (0.4, 0.5),
    #         (0.5, 0.6),
    #         (0.6, 0.7),
    #         (0.7, 0.8),
    #         (0.8, 0.9),
    #         (0.9, 1.0),
    #     ]
    #     for b in bins:
    #         frac = len(
    #             self.df.query(f"{self.label} > {b[0]} and {self.label} <= {b[1]}")
    #         ) / len(self.df)
    #         self.grafana_dict.update({f"label_size_bin_{int(b[0] * 10)}": frac})
    #
    # def get_final_dict(self) -> dict:
    #     """
    #     stops the timer and returns the final dict
    #     """
    #     self.grafana_dict.update({f"duration": time.perf_counter() - self.start_time})
    #
    #     # round values in dict
    #     self.grafana_dict = {
    #         key: round(self.grafana_dict[key], 4) for key in self.grafana_dict
    #     }
    #
    #     return self.grafana_dict
