"""
Test configuration and fixtures
"""

import pytest
import numpy as np
import joblib
import tempfile
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification


@pytest.fixture
def sample_data():
    """Create sample classification data"""
    X, y = make_classification(
        n_samples=100,
        n_features=4,
        n_classes=2,
        random_state=42
    )
    return X, y


@pytest.fixture
def trained_sklearn_model(sample_data):
    """Create and return a trained sklearn model"""
    X, y = sample_data
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    return model


@pytest.fixture
def saved_sklearn_model(trained_sklearn_model):
    """Save model to temporary file and return path"""
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
        joblib.dump(trained_sklearn_model, f.name)
        yield f.name
    # Cleanup
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def sample_prediction_data():
    """Sample data for making predictions"""
    return [[1.0, 2.0, 3.0, 4.0], [0.5, 1.5, 2.5, 3.5]]
