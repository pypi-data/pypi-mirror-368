"""
Tests for utility functions
"""

import pytest
import numpy as np
from quick_api.utils import (
    default_preprocessor,
    default_postprocessor,
    normalize_features,
    min_max_scale,
    apply_threshold,
    top_k_predictions,
    validate_input_shape,
    convert_to_json_serializable,
)


class TestUtils:
    """Test cases for utility functions"""
    
    def test_default_preprocessor_list(self):
        """Test default preprocessor with list input"""
        data = [1.0, 2.0, 3.0, 4.0]
        result = default_preprocessor(data)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (1, 4)
        assert np.array_equal(result[0], data)
    
    def test_default_preprocessor_2d_list(self):
        """Test default preprocessor with 2D list input"""
        data = [[1.0, 2.0], [3.0, 4.0]]
        result = default_preprocessor(data)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (2, 2)
    
    def test_default_preprocessor_dict(self):
        """Test default preprocessor with dictionary input"""
        data = {"features": [1.0, 2.0, 3.0, 4.0]}
        result = default_preprocessor(data)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (1, 4)
    
    def test_default_postprocessor_numpy(self):
        """Test default postprocessor with numpy array"""
        data = np.array([1, 2, 3])
        result = default_postprocessor(data)
        
        assert isinstance(result, list)
        assert result == [1, 2, 3]
    
    def test_default_postprocessor_list(self):
        """Test default postprocessor with list"""
        data = [1, 2, 3]
        result = default_postprocessor(data)
        
        assert isinstance(result, list)
        assert result == data
    
    def test_normalize_features(self):
        """Test feature normalization"""
        data = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        result = normalize_features(data)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == data.shape
        # Check that mean is approximately 0 and std is approximately 1
        assert np.allclose(np.mean(result, axis=0), 0, atol=1e-10)
        assert np.allclose(np.std(result, axis=0), 1, atol=1e-10)
    
    def test_min_max_scale(self):
        """Test min-max scaling"""
        data = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        result = min_max_scale(data)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == data.shape
        # Check that min is 0 and max is 1
        assert np.allclose(np.min(result, axis=0), 0)
        assert np.allclose(np.max(result, axis=0), 1)
    
    def test_apply_threshold(self):
        """Test threshold application"""
        predictions = np.array([0.3, 0.7, 0.1, 0.9])
        result = apply_threshold(predictions, threshold=0.5)
        
        assert isinstance(result, np.ndarray)
        expected = np.array([0, 1, 0, 1])
        assert np.array_equal(result, expected)
    
    def test_top_k_predictions(self):
        """Test top-k predictions"""
        predictions = np.array([0.1, 0.3, 0.6])
        result = top_k_predictions(predictions, k=2)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]['rank'] == 1
        assert result[0]['class_index'] == 2  # Highest score
        assert result[1]['rank'] == 2
        assert result[1]['class_index'] == 1  # Second highest
    
    def test_top_k_predictions_with_class_names(self):
        """Test top-k predictions with class names"""
        predictions = np.array([0.1, 0.3, 0.6])
        class_names = ['cat', 'dog', 'bird']
        result = top_k_predictions(predictions, k=2, class_names=class_names)
        
        assert result[0]['class_name'] == 'bird'
        assert result[1]['class_name'] == 'dog'
    
    def test_validate_input_shape_valid(self):
        """Test input shape validation with valid shape"""
        data = np.array([[1, 2, 3], [4, 5, 6]])
        expected_shape = (2, 3)
        
        assert validate_input_shape(data, expected_shape) == True
    
    def test_validate_input_shape_invalid(self):
        """Test input shape validation with invalid shape"""
        data = np.array([[1, 2], [3, 4]])
        expected_shape = (2, 3)
        
        assert validate_input_shape(data, expected_shape) == False
    
    def test_validate_input_shape_with_none(self):
        """Test input shape validation with None dimension"""
        data = np.array([[1, 2, 3], [4, 5, 6]])
        expected_shape = (None, 3)  # Variable batch size
        
        assert validate_input_shape(data, expected_shape) == True
    
    def test_convert_to_json_serializable(self):
        """Test JSON serialization conversion"""
        # Test numpy array
        arr = np.array([1, 2, 3])
        result = convert_to_json_serializable(arr)
        assert result == [1, 2, 3]
        
        # Test numpy scalar
        scalar = np.int64(42)
        result = convert_to_json_serializable(scalar)
        assert result == 42
        assert isinstance(result, int)
        
        # Test nested structure
        nested = {'array': np.array([1, 2]), 'scalar': np.float32(3.14)}
        result = convert_to_json_serializable(nested)
        assert result == {'array': [1, 2], 'scalar': 3.140000104904175}
    
    def test_normalize_features_zero_std(self):
        """Test normalization with zero standard deviation"""
        data = np.array([[1.0, 2.0], [1.0, 3.0], [1.0, 4.0]])  # First column has zero std
        result = normalize_features(data)
        
        assert isinstance(result, np.ndarray)
        assert not np.any(np.isnan(result))  # Should not contain NaN values
        assert not np.any(np.isinf(result))  # Should not contain inf values
