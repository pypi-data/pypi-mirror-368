"""
Tests for model loading functionality
"""

import pytest
import os
import tempfile
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from quick_api.model_loader import ModelLoader


class TestModelLoader:
    """Test cases for ModelLoader class"""
    
    def test_detect_sklearn_pkl_model(self, saved_sklearn_model):
        """Test detection of sklearn .pkl model"""
        loader = ModelLoader(saved_sklearn_model)
        assert loader.model_type == 'sklearn'
    
    def test_detect_sklearn_joblib_model(self, trained_sklearn_model):
        """Test detection of sklearn .joblib model"""
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            joblib.dump(trained_sklearn_model, f.name)
            loader = ModelLoader(f.name)
            assert loader.model_type == 'sklearn'
            os.unlink(f.name)
    
    def test_detect_tensorflow_model(self):
        """Test detection of TensorFlow model"""
        with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as f:
            loader = ModelLoader(f.name)
            assert loader.model_type == 'tensorflow'
            os.unlink(f.name)
    
    def test_detect_pytorch_model(self):
        """Test detection of PyTorch model"""
        with tempfile.NamedTemporaryFile(suffix='.pt', delete=False) as f:
            loader = ModelLoader(f.name)
            assert loader.model_type == 'pytorch'
            os.unlink(f.name)
    
    def test_load_sklearn_model(self, saved_sklearn_model, sample_data):
        """Test loading sklearn model"""
        loader = ModelLoader(saved_sklearn_model)
        model = loader.load()
        
        # Test that model can make predictions
        X, y = sample_data
        predictions = model.predict(X[:5])
        assert len(predictions) == 5
        assert all(pred in [0, 1] for pred in predictions)
    
    def test_get_sklearn_model_info(self, saved_sklearn_model):
        """Test getting sklearn model information"""
        loader = ModelLoader(saved_sklearn_model)
        info = loader.get_model_info()
        
        assert 'model_path' in info
        assert 'model_type' in info
        assert info['model_type'] == 'sklearn'
        assert 'model_class' in info
        assert info['model_class'] == 'RandomForestClassifier'
        assert 'n_features' in info
        assert info['n_features'] == 4
    
    def test_load_nonexistent_model(self):
        """Test loading a non-existent model file"""
        with pytest.raises(ValueError):
            loader = ModelLoader("nonexistent_model.pkl")
            loader.load()
    
    def test_unsupported_model_type(self):
        """Test loading unsupported model type"""
        with tempfile.NamedTemporaryFile(suffix='.unsupported', delete=False) as f:
            loader = ModelLoader(f.name)
            # Should default to sklearn but fail to load
            with pytest.raises(ValueError):
                loader.load()
            os.unlink(f.name)
