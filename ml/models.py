"""
Machine Learning Candidate Models: Chennai Traffic Intelligence
Implements Random Forest and Gradient Boosted Decision Trees (HistGradientBoosting / LightGBM equivalent)
using scikit-learn.
"""

from typing import Dict, Any
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from ml.config import RANDOM_SEED


def build_random_forest_model(params: Dict[str, Any] = None, **kwargs) -> RandomForestRegressor:
    """Builds a tuned Random Forest regressor candidate."""
    default_params = {
        "n_estimators": 100,
        "max_depth": 12,
        "min_samples_split": 5,
        "min_samples_leaf": 3,
        "random_state": RANDOM_SEED,
        "n_jobs": -1
    }
    if params:
        default_params.update(params)
    default_params.update(kwargs)
    return RandomForestRegressor(**default_params)


def build_gradient_boosting_model(params: Dict[str, Any] = None, **kwargs) -> HistGradientBoostingRegressor:
    """
    Builds a high-performance Gradient Boosted Decision Tree (LightGBM equivalent).
    Features native histogram binning, monotonic constraints, and early stopping.
    """
    default_params = {
        "max_iter": 150,
        "max_depth": 8,
        "learning_rate": 0.08,
        "min_samples_leaf": 10,
        "l2_regularization": 1.0,
        "random_state": RANDOM_SEED
    }
    if params:
        default_params.update(params)
    default_params.update(kwargs)
    return HistGradientBoostingRegressor(**default_params)



class MultiHorizonTrafficModel:
    """
    Manages multi-horizon forecasting (+15m, +30m, +45m, +60m) by training
    dedicated models for each horizon.
    """

    def __init__(self, model_type: str = "gradient_boosting"):
        self.model_type = model_type
        self.models: Dict[str, Any] = {}
        self.horizons = ["15min", "30min", "45min", "60min"]

    def _create_base_model(self):
        if self.model_type == "random_forest":
            return build_random_forest_model()
        return build_gradient_boosting_model()

    def fit_horizon(self, horizon: str, X, y):
        model = self._create_base_model()
        model.fit(X, y)
        self.models[horizon] = model
        return model

    def predict(self, horizon: str, X):
        if horizon not in self.models:
            raise KeyError(f"Horizon '{horizon}' has not been trained. Available: {list(self.models.keys())}")
        return self.models[horizon].predict(X)
