"""
config
"""

import logging
import os

# set logger
FORMAT = "%(asctime)s: %(levelname)s: %(name)s: %(lineno)d: %(message)s"
logging.basicConfig(format=FORMAT, datefmt="%H:%M:%S", level=logging.INFO)

# project settings
PROJECT_NAME = "clf_train"
PROJECT_LABEL = "clf"
CACHE = True
CACHE_PATH = "/data/cache"
N_SAMPLES = 50
N_FEATURES = 10
DATA_DROP_MISSING_THRESHOLD = 0.9
NAME = "rf"
PREPROCESSOR_NUM_IMPUTE = "mean"
PREPROCESSOR_CAT_IMPUTE = "most_frequent"
ESTIMATOR = "RandomForestClassifier"
ESTIMATOR_CALIBRATE = True
HYPERPARAM = "scikit-optimize"
HYPERPARAM_RUNS = 30
HYPERPARAM_TIME_OUT_SECS = 300
HYPERPARAM_METRIC = "roc_auc"
PICKLE_PATH = "out/"
SHAP_LOG_TO_OUT = True
MLFLOW_LOG = False
MLFLOW_EXPERIMENT_NAME = "clf_train"
MLFLOW_RUN_NAME = "train-pipeline"

# create sql dict with all sql files as string
sql_dict = {}
for filename in os.listdir("sql/"):
    path = os.path.join("sql/", filename)
    if os.path.isfile(path):
        sql_key = filename.replace(".sql", "")
        sql_obj = open(path)
        sql_string = sql_obj.read()
        sql_dict.update({sql_key: sql_string})
