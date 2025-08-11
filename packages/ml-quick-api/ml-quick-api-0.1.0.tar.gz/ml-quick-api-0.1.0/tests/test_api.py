"""
Tests for the main API functionality
"""

import pytest
import numpy as np
from fastapi.testclient import TestClient
from quick_api import create_api
from quick_api.api import QuickAPI


class TestQuickAPI:
    """Test cases for QuickAPI class"""
    
    def test_create_api_basic(self, saved_sklearn_model):
        """Test basic API creation"""
        api = create_api(saved_sklearn_model)
        assert isinstance(api, QuickAPI)
        assert api.model_type == 'sklearn'
        assert api.host == "localhost"
        assert api.port == 8000
    
    def test_create_api_custom_config(self, saved_sklearn_model):
        """Test API creation with custom configuration"""
        api = create_api(
            saved_sklearn_model,
            host="0.0.0.0",
            port=8080,
            title="Test API",
            description="Test Description",
            version="2.0.0"
        )
        assert api.host == "0.0.0.0"
        assert api.port == 8080
    
    def test_api_health_endpoint(self, saved_sklearn_model):
        """Test health check endpoint"""
        api = create_api(saved_sklearn_model)
        client = TestClient(api.get_app())
        
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] == True
        assert "timestamp" in data
    
    def test_api_info_endpoint(self, saved_sklearn_model):
        """Test model info endpoint"""
        api = create_api(saved_sklearn_model)
        client = TestClient(api.get_app())
        
        response = client.get("/info")
        assert response.status_code == 200
        
        data = response.json()
        assert data["model_type"] == "sklearn"
        assert "model_info" in data
        assert "api_version" in data
        assert "endpoints" in data
    
    def test_api_root_endpoint(self, saved_sklearn_model):
        """Test root endpoint"""
        api = create_api(saved_sklearn_model)
        client = TestClient(api.get_app())
        
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert data["model_type"] == "sklearn"
        assert "endpoints" in data
    
    def test_api_predict_endpoint(self, saved_sklearn_model, sample_prediction_data):
        """Test prediction endpoint"""
        api = create_api(saved_sklearn_model)
        client = TestClient(api.get_app())
        
        response = client.post("/predict", json={"data": sample_prediction_data})
        assert response.status_code == 200
        
        data = response.json()
        assert "predictions" in data
        assert "model_type" in data
        assert "timestamp" in data
        assert data["model_type"] == "sklearn"
        assert len(data["predictions"]) == len(sample_prediction_data)
    
    def test_api_predict_single_sample(self, saved_sklearn_model):
        """Test prediction with single sample"""
        api = create_api(saved_sklearn_model)
        client = TestClient(api.get_app())
        
        response = client.post("/predict", json={"data": [1.0, 2.0, 3.0, 4.0]})
        assert response.status_code == 200
        
        data = response.json()
        assert "predictions" in data
        assert len(data["predictions"]) == 1
    
    def test_api_predict_invalid_data(self, saved_sklearn_model):
        """Test prediction with invalid data"""
        api = create_api(saved_sklearn_model)
        client = TestClient(api.get_app())
        
        # Empty data
        response = client.post("/predict", json={"data": []})
        assert response.status_code == 422
        
        # Invalid format
        response = client.post("/predict", json={"invalid": "data"})
        assert response.status_code == 422
    
    def test_api_predict_wrong_dimensions(self, saved_sklearn_model):
        """Test prediction with wrong input dimensions"""
        api = create_api(saved_sklearn_model)
        client = TestClient(api.get_app())
        
        # Wrong number of features (model expects 4, providing 2)
        response = client.post("/predict", json={"data": [[1.0, 2.0]]})
        assert response.status_code == 400
    
    def test_api_with_preprocessing(self, saved_sklearn_model):
        """Test API with custom preprocessing"""
        def custom_preprocess(data):
            # Simple preprocessing that adds 1 to all values
            return data + 1
        
        api = create_api(saved_sklearn_model, preprocess_func=custom_preprocess)
        client = TestClient(api.get_app())
        
        response = client.post("/predict", json={"data": [[0.0, 1.0, 2.0, 3.0]]})
        assert response.status_code == 200
        
        data = response.json()
        assert "predictions" in data
    
    def test_api_with_postprocessing(self, saved_sklearn_model):
        """Test API with custom postprocessing"""
        def custom_postprocess(predictions):
            # Simple postprocessing that converts to string
            return [f"class_{p}" for p in predictions]
        
        api = create_api(saved_sklearn_model, postprocess_func=custom_postprocess)
        client = TestClient(api.get_app())
        
        response = client.post("/predict", json={"data": [[1.0, 2.0, 3.0, 4.0]]})
        assert response.status_code == 200
        
        data = response.json()
        assert "predictions" in data
        assert isinstance(data["predictions"][0], str)
        assert data["predictions"][0].startswith("class_")
    
    def test_api_docs_endpoint(self, saved_sklearn_model):
        """Test that OpenAPI docs are available"""
        api = create_api(saved_sklearn_model)
        client = TestClient(api.get_app())
        
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
