"""
FastAPI application for serving machine learning models
"""

import uvicorn
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import Any, List, Union, Optional, Callable, Dict
import logging
from datetime import datetime


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictionRequest(BaseModel):
    """Request model for predictions"""
    data: Union[List[List[float]], List[float], Dict[str, Any]]
    
    @validator('data')
    def validate_data(cls, v):
        if not v:
            raise ValueError("Data cannot be empty")
        return v


class PredictionResponse(BaseModel):
    """Response model for predictions"""
    predictions: Union[List[float], List[List[float]], List[int], List[str]]
    model_type: str
    timestamp: str
    input_shape: Optional[tuple] = None
    
    model_config = {"protected_namespaces": ()}


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    timestamp: str
    model_loaded: bool
    
    model_config = {"protected_namespaces": ()}


class ModelInfoResponse(BaseModel):
    """Response model for model information"""
    model_type: str
    model_info: Dict[str, Any]
    api_version: str
    endpoints: List[str]
    
    model_config = {"protected_namespaces": ()}


class QuickAPI:
    """Main API class for serving machine learning models"""
    
    def __init__(
        self,
        model: Any,
        model_type: str,
        host: str = "localhost",
        port: int = 8000,
        title: str = "Quick-API",
        description: str = "Machine Learning Model API",
        version: str = "1.0.0",
        input_shape: Optional[tuple] = None,
        preprocess_func: Optional[Callable] = None,
        postprocess_func: Optional[Callable] = None,
    ):
        self.model = model
        self.model_type = model_type
        self.host = host
        self.port = port
        self.input_shape = input_shape
        self.preprocess_func = preprocess_func
        self.postprocess_func = postprocess_func
        
        # Create FastAPI app
        self.app = FastAPI(
            title=title,
            description=description,
            version=version,
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"QuickAPI initialized for {model_type} model")
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.post("/predict", response_model=PredictionResponse)
        async def predict(request: PredictionRequest):
            """Make predictions using the loaded model"""
            try:
                # Convert input data to numpy array
                input_data = self._prepare_input(request.data)
                
                # Apply preprocessing if provided
                if self.preprocess_func:
                    input_data = self.preprocess_func(input_data)
                
                # Make prediction
                predictions = self._make_prediction(input_data)
                
                # Apply postprocessing if provided
                if self.postprocess_func:
                    predictions = self.postprocess_func(predictions)
                
                # Convert predictions to list for JSON serialization
                if isinstance(predictions, np.ndarray):
                    predictions = predictions.tolist()
                
                return PredictionResponse(
                    predictions=predictions,
                    model_type=self.model_type,
                    timestamp=datetime.now().isoformat(),
                    input_shape=input_data.shape if hasattr(input_data, 'shape') else None
                )
                
            except Exception as e:
                logger.error(f"Prediction error: {e}")
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health():
            """Health check endpoint"""
            return HealthResponse(
                status="healthy",
                timestamp=datetime.now().isoformat(),
                model_loaded=self.model is not None
            )
        
        @self.app.get("/info", response_model=ModelInfoResponse)
        async def info():
            """Get model information"""
            return ModelInfoResponse(
                model_type=self.model_type,
                model_info=self._get_model_info(),
                api_version="1.0.0",
                endpoints=["/predict", "/health", "/info", "/docs"]
            )
        
        @self.app.get("/")
        async def root():
            """Root endpoint with basic information"""
            return {
                "message": "Welcome to Quick-API",
                "model_type": self.model_type,
                "endpoints": ["/predict", "/health", "/info", "/docs"],
                "documentation": "/docs"
            }
    
    def _prepare_input(self, data: Union[List, Dict]) -> np.ndarray:
        """Prepare input data for prediction"""
        if isinstance(data, dict):
            # Handle dictionary input (convert to array based on keys)
            if 'features' in data:
                data = data['features']
            elif 'data' in data:
                data = data['data']
            else:
                # Use all values from the dictionary
                data = list(data.values())
        
        # Convert to numpy array
        try:
            input_array = np.array(data, dtype=np.float32)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Could not convert input data to numpy array: {e}")
        
        # Ensure 2D array for most models
        if input_array.ndim == 1:
            input_array = input_array.reshape(1, -1)
        
        return input_array
    
    def _make_prediction(self, input_data: np.ndarray) -> Any:
        """Make prediction using the loaded model"""
        try:
            if self.model_type == 'sklearn':
                return self._predict_sklearn(input_data)
            elif self.model_type == 'tensorflow':
                return self._predict_tensorflow(input_data)
            elif self.model_type == 'pytorch':
                return self._predict_pytorch(input_data)
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
        except Exception as e:
            logger.error(f"Model prediction error: {e}")
            raise
    
    def _predict_sklearn(self, input_data: np.ndarray) -> Any:
        """Make prediction with sklearn model"""
        if hasattr(self.model, 'predict'):
            return self.model.predict(input_data)
        elif hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(input_data)
        else:
            raise ValueError("Model does not have predict or predict_proba method")
    
    def _predict_tensorflow(self, input_data: np.ndarray) -> Any:
        """Make prediction with TensorFlow model"""
        try:
            predictions = self.model.predict(input_data)
            return predictions
        except Exception as e:
            raise ValueError(f"TensorFlow prediction failed: {e}")
    
    def _predict_pytorch(self, input_data: np.ndarray) -> Any:
        """Make prediction with PyTorch model"""
        try:
            import torch
            
            # Convert numpy to torch tensor
            input_tensor = torch.FloatTensor(input_data)
            
            # Set model to evaluation mode
            if hasattr(self.model, 'eval'):
                self.model.eval()
            
            # Make prediction
            with torch.no_grad():
                if hasattr(self.model, 'forward'):
                    predictions = self.model.forward(input_tensor)
                elif callable(self.model):
                    predictions = self.model(input_tensor)
                else:
                    raise ValueError("PyTorch model is not callable")
            
            # Convert back to numpy
            return predictions.numpy()
            
        except ImportError:
            raise ImportError("PyTorch is required for PyTorch model predictions")
        except Exception as e:
            raise ValueError(f"PyTorch prediction failed: {e}")
    
    def _get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        info = {
            "model_type": self.model_type,
            "has_preprocess": self.preprocess_func is not None,
            "has_postprocess": self.postprocess_func is not None,
        }
        
        try:
            if self.model_type == 'sklearn':
                if hasattr(self.model, '__class__'):
                    info['model_class'] = self.model.__class__.__name__
                if hasattr(self.model, 'n_features_in_'):
                    info['n_features'] = self.model.n_features_in_
                if hasattr(self.model, 'classes_'):
                    info['n_classes'] = len(self.model.classes_)
                    info['classes'] = self.model.classes_.tolist()
            
            elif self.model_type == 'tensorflow':
                if hasattr(self.model, 'input_shape'):
                    info['input_shape'] = self.model.input_shape
                if hasattr(self.model, 'output_shape'):
                    info['output_shape'] = self.model.output_shape
            
            elif self.model_type == 'pytorch':
                import torch
                if isinstance(self.model, torch.nn.Module):
                    info['total_params'] = sum(p.numel() for p in self.model.parameters())
        
        except Exception as e:
            info['info_error'] = str(e)
        
        return info
    
    def run(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        reload: bool = False,
        workers: int = 1,
        **kwargs
    ):
        """Run the API server"""
        host = host or self.host
        port = port or self.port
        
        logger.info(f"Starting Quick-API server on {host}:{port}")
        logger.info(f"Model type: {self.model_type}")
        logger.info(f"API documentation available at: http://{host}:{port}/docs")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            **kwargs
        )
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance"""
        return self.app
