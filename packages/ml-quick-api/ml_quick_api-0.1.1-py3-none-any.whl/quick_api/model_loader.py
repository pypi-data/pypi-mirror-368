"""
Model loader for different types of machine learning models
"""

import os
import pickle
import joblib
from typing import Any, Optional
import warnings


class ModelLoader:
    """Loads different types of machine learning models"""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model_type = self._detect_model_type()
    
    def _detect_model_type(self) -> str:
        """Detect the type of model based on file extension"""
        _, ext = os.path.splitext(self.model_path.lower())
        
        if ext in ['.pkl', '.pickle']:
            return 'sklearn'
        elif ext in ['.joblib']:
            return 'sklearn'
        elif ext in ['.h5', '.keras']:
            return 'tensorflow'
        elif ext in ['.pt', '.pth']:
            return 'pytorch'
        elif os.path.isdir(self.model_path):
            # Could be a TensorFlow SavedModel format
            if os.path.exists(os.path.join(self.model_path, 'saved_model.pb')):
                return 'tensorflow'
        
        # Default to trying pickle/joblib
        return 'sklearn'
    
    def load(self) -> Any:
        """Load the model based on its type"""
        if self.model_type == 'sklearn':
            return self._load_sklearn_model()
        elif self.model_type == 'tensorflow':
            return self._load_tensorflow_model()
        elif self.model_type == 'pytorch':
            return self._load_pytorch_model()
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    def _load_sklearn_model(self) -> Any:
        """Load scikit-learn model"""
        try:
            # Try joblib first (recommended for sklearn)
            return joblib.load(self.model_path)
        except:
            try:
                # Fallback to pickle
                with open(self.model_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                raise ValueError(f"Failed to load sklearn model: {e}")
    
    def _load_tensorflow_model(self) -> Any:
        """Load TensorFlow/Keras model"""
        try:
            import tensorflow as tf
            
            if os.path.isdir(self.model_path):
                # SavedModel format
                return tf.keras.models.load_model(self.model_path)
            else:
                # H5 or Keras format
                return tf.keras.models.load_model(self.model_path)
        except ImportError:
            raise ImportError("TensorFlow is required to load TensorFlow models")
        except Exception as e:
            raise ValueError(f"Failed to load TensorFlow model: {e}")
    
    def _load_pytorch_model(self) -> Any:
        """Load PyTorch model"""
        try:
            import torch
            
            # Load the model state dict
            model_data = torch.load(self.model_path, map_location='cpu')
            
            # If it's just a state dict, we need the model architecture
            # This is a limitation - we'd need the model class definition
            if isinstance(model_data, dict) and 'state_dict' in model_data:
                warnings.warn(
                    "PyTorch model appears to be a state dict. "
                    "You may need to provide the model architecture separately."
                )
                return model_data
            else:
                # Assume it's a complete model
                return model_data
        except ImportError:
            raise ImportError("PyTorch is required to load PyTorch models")
        except Exception as e:
            raise ValueError(f"Failed to load PyTorch model: {e}")
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model"""
        info = {
            'model_path': self.model_path,
            'model_type': self.model_type,
            'file_size': os.path.getsize(self.model_path) if os.path.isfile(self.model_path) else None,
        }
        
        try:
            model = self.load()
            
            if self.model_type == 'sklearn':
                info.update(self._get_sklearn_info(model))
            elif self.model_type == 'tensorflow':
                info.update(self._get_tensorflow_info(model))
            elif self.model_type == 'pytorch':
                info.update(self._get_pytorch_info(model))
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def _get_sklearn_info(self, model) -> dict:
        """Get sklearn model information"""
        info = {}
        if hasattr(model, '__class__'):
            info['model_class'] = model.__class__.__name__
        if hasattr(model, 'n_features_in_'):
            info['n_features'] = model.n_features_in_
        if hasattr(model, 'classes_'):
            info['n_classes'] = len(model.classes_)
        return info
    
    def _get_tensorflow_info(self, model) -> dict:
        """Get TensorFlow model information"""
        info = {}
        if hasattr(model, 'input_shape'):
            info['input_shape'] = model.input_shape
        if hasattr(model, 'output_shape'):
            info['output_shape'] = model.output_shape
        if hasattr(model, 'count_params'):
            info['total_params'] = model.count_params()
        return info
    
    def _get_pytorch_info(self, model) -> dict:
        """Get PyTorch model information"""
        info = {}
        try:
            import torch
            if isinstance(model, torch.nn.Module):
                info['total_params'] = sum(p.numel() for p in model.parameters())
                info['trainable_params'] = sum(p.numel() for p in model.parameters() if p.requires_grad)
        except:
            pass
        return info
