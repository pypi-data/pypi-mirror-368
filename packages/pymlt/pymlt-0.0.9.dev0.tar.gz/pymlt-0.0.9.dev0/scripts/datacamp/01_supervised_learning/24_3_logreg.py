#!/usr/local/bin/python3

# https://campus.datacamp.com/courses/supervised-learning-with-scikit-learn/

import numpy as np
from pydataset import data
from sklearn.linear_model import ElasticNet, LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    mean_squared_error,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split

df = data("diamonds")
df["price_cat"] = np.where(df["price"] > 17000, 1, 0)

X = df[["depth", "x"]].values
y = df["price_cat"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

logreg = LogisticRegression()
logreg.fit(X_train, y_train)
y_pred = logreg.predict(X_test)

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

y_pred_prob = logreg.predict_proba(X_test)[:, 1]
fpr, tpr, thresholds = roc_curve(y_test, y_pred_prob)

# Plot ROC curve
# plt.plot([0, 1], [0, 1], 'k--')
# plt.plot(fpr, tpr)
# plt.xlabel('False Positive Rate')
# plt.ylabel('True Positive Rate')
# plt.title('ROC Curve')
# plt.show()

print("AUC:", roc_auc_score(y_test, y_pred_prob))
cv_auc = cross_val_score(logreg, X, y, cv=5, scoring="roc_auc")
print("AUC w/ 5f cv:", cv_auc)


param_grid = {"l1_ratio": np.linspace(0, 1, 30)}
elastic_net = ElasticNet()
gm_cv = GridSearchCV(elastic_net, param_grid, cv=5)
gm_cv.fit(X_train, y_train)

y_pred = gm_cv.predict(X_test)
r2 = gm_cv.score(X_test, y_test)
mse = mean_squared_error(y_test, y_pred)
print("l1 ratio:", gm_cv.best_params_)
print("R2", r2)
print("MSE", mse)
