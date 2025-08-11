"""
Tests for the core functionality
"""

import pytest
import os
from quick_api.core import create_api
from quick_api.api import QuickAPI


class TestCore:
    """Test cases for core functionality"""
    
    def test_create_api_file_not_found(self):
        """Test create_api with non-existent file"""
        with pytest.raises(FileNotFoundError):
            create_api("nonexistent_model.pkl")
    
    def test_create_api_success(self, saved_sklearn_model):
        """Test successful API creation"""
        api = create_api(saved_sklearn_model)
        
        assert isinstance(api, QuickAPI)
        assert api.model is not None
        assert api.model_type == 'sklearn'
    
    def test_create_api_with_all_params(self, saved_sklearn_model):
        """Test API creation with all parameters"""
        def dummy_preprocess(data):
            return data
        
        def dummy_postprocess(data):
            return data
        
        api = create_api(
            model_path=saved_sklearn_model,
            host="0.0.0.0",
            port=9000,
            title="Test API",
            description="Test Description",
            version="2.0.0",
            input_shape=(1, 4),
            preprocess_func=dummy_preprocess,
            postprocess_func=dummy_postprocess,
        )
        
        assert api.host == "0.0.0.0"
        assert api.port == 9000
        assert api.input_shape == (1, 4)
        assert api.preprocess_func == dummy_preprocess
        assert api.postprocess_func == dummy_postprocess
