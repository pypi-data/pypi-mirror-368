"""
Core functionality for Quick-API
"""

from .api import QuickAPI
from .model_loader import ModelLoader
from typing import Optional, Callable, Any
import os


def create_api(
    model_path: str,
    host: str = "localhost",
    port: int = 8000,
    title: str = "Quick-API",
    description: str = "Machine Learning Model API",
    version: str = "1.0.0",
    input_shape: Optional[tuple] = None,
    preprocess_func: Optional[Callable] = None,
    postprocess_func: Optional[Callable] = None,
) -> QuickAPI:
    """
    Create a REST API from a saved machine learning model.
    
    Args:
        model_path (str): Path to the saved model file
        host (str): Host to run the API on (default: "localhost")
        port (int): Port to run the API on (default: 8000)
        title (str): API title for documentation
        description (str): API description for documentation
        version (str): API version
        input_shape (tuple, optional): Expected input shape (auto-detected if None)
        preprocess_func (callable, optional): Custom preprocessing function
        postprocess_func (callable, optional): Custom postprocessing function
    
    Returns:
        QuickAPI: Configured API instance ready to run
    
    Example:
        >>> from quick_api import create_api
        >>> api = create_api("model.pkl")
        >>> api.run()
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    # Load the model
    model_loader = ModelLoader(model_path)
    model = model_loader.load()
    
    # Create and configure the API
    api = QuickAPI(
        model=model,
        model_type=model_loader.model_type,
        host=host,
        port=port,
        title=title,
        description=description,
        version=version,
        input_shape=input_shape,
        preprocess_func=preprocess_func,
        postprocess_func=postprocess_func,
    )
    
    return api
