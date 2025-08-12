import matplotlib.pyplot as plt
from sklearn.datasets import load_wine
from sklearn.metrics import plot_roc_curve
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

X, y = load_wine(return_X_y=True)
y = y == 2
print(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
svc = SVC(random_state=42)
svc.fit(X_train, y_train)

svc_disp = plot_roc_curve(svc, X_test, y_test)
plt.show()
