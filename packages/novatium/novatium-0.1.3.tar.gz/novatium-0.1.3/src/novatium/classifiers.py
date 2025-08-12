from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.utils.validation import check_X_y, check_is_fitted, check_array
import numpy as np

class NovaClassifier(BaseEstimator, ClassifierMixin):
    """
    NovaClassifier — Base+Delta classification for cosmic-grade accuracy.
    Combines a base classifier with a delta correction regressor on probability residuals.

    Parameters
    ----------
    base_model : sklearn-like classifier supporting predict_proba
        The primary classifier (e.g., LogisticRegression, GradientBoostingClassifier).
    delta_model : sklearn-like regressor
        Learns residuals on the positive-class probability.
    """

    def __init__(self, base_model, delta_model):
        self.base_model = base_model
        self.delta_model = delta_model

    def fit(self, X, y):
        X, y = check_X_y(X, y, accept_sparse=False)
        self.base_ = clone(self.base_model).fit(X, y)
        base_probs = self.base_.predict_proba(X)[:, 1]
        residuals = y - base_probs
        self.delta_ = clone(self.delta_model).fit(X, residuals)
        return self

    def predict_proba(self, X):
        check_is_fitted(self, ["base_", "delta_"])
        X = check_array(X)
        base_probs = self.base_.predict_proba(X)[:, 1]
        delta = self.delta_.predict(X)
        final_probs = np.clip(base_probs + delta, 1e-7, 1 - 1e-7)
        return np.c_[1 - final_probs, final_probs]

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)
