from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.utils.validation import check_X_y, check_is_fitted, check_array
import numpy as np

class NovaRegressor(BaseEstimator, RegressorMixin):
    """
    NovaRegressor — Base+Delta regression for cosmic-grade performance.
    Combines a base model with a delta correction model.

    Parameters
    ----------
    base_model : sklearn-like regressor
        The primary regressor (e.g., LinearRegression, RandomForestRegressor).
    delta_model : sklearn-like regressor
        Learns residuals of the base model to correct its predictions.
    """

    def __init__(self, base_model, delta_model):
        self.base_model = base_model
        self.delta_model = delta_model

    def fit(self, X, y):
        X, y = check_X_y(X, y, accept_sparse=False, y_numeric=True)
        self.base_ = clone(self.base_model).fit(X, y)
        residuals = y - self.base_.predict(X)
        self.delta_ = clone(self.delta_model).fit(X, residuals)
        return self

    def predict(self, X):
        check_is_fitted(self, ["base_", "delta_"])
        X = check_array(X)
        return self.base_.predict(X) + self.delta_.predict(X)
