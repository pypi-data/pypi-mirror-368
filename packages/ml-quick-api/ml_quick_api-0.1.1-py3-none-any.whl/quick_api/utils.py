"""
Utility functions for Quick-API
"""

import numpy as np
from typing import Any, Callable, Union, List, Dict
import json


def default_preprocessor(data: Union[List, np.ndarray, Dict]) -> np.ndarray:
    """
    Default preprocessing function that converts input data to numpy array
    
    Args:
        data: Input data in various formats
        
    Returns:
        np.ndarray: Preprocessed data ready for model prediction
    """
    if isinstance(data, dict):
        # Handle dictionary input
        if 'features' in data:
            data = data['features']
        elif 'data' in data:
            data = data['data']
        else:
            data = list(data.values())
    
    # Convert to numpy array
    if not isinstance(data, np.ndarray):
        data = np.array(data, dtype=np.float32)
    
    # Ensure 2D array
    if data.ndim == 1:
        data = data.reshape(1, -1)
    
    return data


def default_postprocessor(predictions: Any) -> Any:
    """
    Default postprocessing function that ensures predictions are JSON serializable
    
    Args:
        predictions: Model predictions
        
    Returns:
        JSON serializable predictions
    """
    if isinstance(predictions, np.ndarray):
        return predictions.tolist()
    return predictions


def create_preprocessing_pipeline(*funcs: Callable) -> Callable:
    """
    Create a preprocessing pipeline from multiple functions
    
    Args:
        *funcs: Functions to apply in sequence
        
    Returns:
        Callable: Combined preprocessing function
    """
    def pipeline(data):
        for func in funcs:
            data = func(data)
        return data
    return pipeline


def create_postprocessing_pipeline(*funcs: Callable) -> Callable:
    """
    Create a postprocessing pipeline from multiple functions
    
    Args:
        *funcs: Functions to apply in sequence
        
    Returns:
        Callable: Combined postprocessing function
    """
    def pipeline(data):
        for func in funcs:
            data = func(data)
        return data
    return pipeline


def normalize_features(data: np.ndarray, mean: np.ndarray = None, std: np.ndarray = None) -> np.ndarray:
    """
    Normalize features using z-score normalization
    
    Args:
        data: Input data
        mean: Mean values for normalization (computed if None)
        std: Standard deviation values for normalization (computed if None)
        
    Returns:
        np.ndarray: Normalized data
    """
    if mean is None:
        mean = np.mean(data, axis=0)
    if std is None:
        std = np.std(data, axis=0)
    
    # Avoid division by zero
    std = np.where(std == 0, 1, std)
    
    return (data - mean) / std


def min_max_scale(data: np.ndarray, min_vals: np.ndarray = None, max_vals: np.ndarray = None) -> np.ndarray:
    """
    Scale features using min-max normalization
    
    Args:
        data: Input data
        min_vals: Minimum values for scaling (computed if None)
        max_vals: Maximum values for scaling (computed if None)
        
    Returns:
        np.ndarray: Scaled data
    """
    if min_vals is None:
        min_vals = np.min(data, axis=0)
    if max_vals is None:
        max_vals = np.max(data, axis=0)
    
    # Avoid division by zero
    range_vals = max_vals - min_vals
    range_vals = np.where(range_vals == 0, 1, range_vals)
    
    return (data - min_vals) / range_vals


def apply_threshold(predictions: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    """
    Apply threshold to binary classification predictions
    
    Args:
        predictions: Model predictions
        threshold: Classification threshold
        
    Returns:
        np.ndarray: Thresholded predictions
    """
    return (predictions >= threshold).astype(int)


def top_k_predictions(predictions: np.ndarray, k: int = 5, class_names: List[str] = None) -> List[Dict]:
    """
    Get top-k predictions for multi-class classification
    
    Args:
        predictions: Model predictions (probabilities)
        k: Number of top predictions to return
        class_names: Names of classes (optional)
        
    Returns:
        List[Dict]: Top-k predictions with scores
    """
    if predictions.ndim == 1:
        predictions = predictions.reshape(1, -1)
    
    results = []
    for pred in predictions:
        # Get top-k indices
        top_indices = np.argsort(pred)[-k:][::-1]
        
        sample_results = []
        for i, idx in enumerate(top_indices):
            result = {
                'rank': i + 1,
                'class_index': int(idx),
                'score': float(pred[idx])
            }
            if class_names and idx < len(class_names):
                result['class_name'] = class_names[idx]
            sample_results.append(result)
        
        results.append(sample_results)
    
    return results[0] if len(results) == 1 else results


def validate_input_shape(data: np.ndarray, expected_shape: tuple) -> bool:
    """
    Validate that input data matches expected shape
    
    Args:
        data: Input data
        expected_shape: Expected shape (can include None for variable dimensions)
        
    Returns:
        bool: True if shape is valid
    """
    if len(data.shape) != len(expected_shape):
        return False
    
    for actual, expected in zip(data.shape, expected_shape):
        if expected is not None and actual != expected:
            return False
    
    return True


def convert_to_json_serializable(obj: Any) -> Any:
    """
    Convert objects to JSON serializable format
    
    Args:
        obj: Object to convert
        
    Returns:
        JSON serializable object
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    else:
        return obj
