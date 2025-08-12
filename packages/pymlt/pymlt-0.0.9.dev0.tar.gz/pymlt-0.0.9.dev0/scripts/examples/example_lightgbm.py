"""
example file
"""

import lightgbm as lgb
from icecream import ic
from sklearn.datasets import make_classification
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=500_000, n_informative=4, weights=[0.95])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)


model = lgb.LGBMClassifier(
    boosting_type="gbdt",
    colsample_bytree=1.0,
    importance_type="split",
    learning_rate=0.09,
    max_depth=4,
    min_child_samples=200,
    min_child_weight=0.001,
    min_split_gain=0.0,
    n_estimators=100,
    n_jobs=-1,
    num_leaves=31,
    objective=None,
    random_state=None,
    reg_alpha=0.0,
    reg_lambda=0.0,
    subsample=1.0,
    subsample_for_bin=200_000,
    subsample_freq=0,
)

model.fit(
    X_train,
    y_train,
    eval_set=[(X_train, y_train), (X_test, y_test)],
    eval_names=["train", "test"],
    eval_metric="logloss",
    callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(period=0)],
)

y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

ic(roc_auc_score(y_train, y_train_pred))
ic(roc_auc_score(y_test, y_test_pred))
print(classification_report(y_test, y_test_pred))
