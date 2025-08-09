from trauto import EnhancedTrackRailSystem, TRAConfig
from sklearn.datasets import make_classification, make_regression
from sklearn.model_selection import train_test_split
import numpy as np

def test_classification_basic():
    X, y = make_classification(
        n_samples=100,
        n_features=8,
        n_classes=2,
        n_informative=4,
        random_state=42
    )
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    config = TRAConfig(task_type="classification")
    tra = EnhancedTrackRailSystem(config)
    tra.fit(X_train, y_train)
    y_pred = tra.predict(X_test)
    assert isinstance(y_pred, (np.ndarray, list)), "Prediction should be array or list"
    assert len(y_pred) == len(y_test), "Number of predictions doesn't match test samples"
    metrics = tra.get_performance_metrics(X_test, y_test)
    # You may want to check accuracy is within [0,1]
    assert 0 <= metrics.get("overall_accuracy", 0) <= 1

def test_regression_basic():
    X, y = make_regression(
        n_samples=100,
        n_features=6,
        n_informative=4,
        random_state=0
    )
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    config = TRAConfig(task_type="regression")
    tra = EnhancedTrackRailSystem(config)
    tra.fit(X_train, y_train)
    y_pred = tra.predict(X_test)
    assert isinstance(y_pred, (np.ndarray, list)), "Prediction should be array or list"
    assert len(y_pred) == len(y_test), "Number of predictions doesn't match test samples"
    metrics = tra.get_performance_metrics(X_test, y_test)
    # For regression, negative MSE is typically returned
    assert isinstance(metrics.get("overall_accuracy", 0), float), "Regression metric should be a float"

