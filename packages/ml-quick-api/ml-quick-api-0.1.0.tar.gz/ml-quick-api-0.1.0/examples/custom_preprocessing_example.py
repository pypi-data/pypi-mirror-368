"""
Example: Using Quick-API with custom preprocessing and postprocessing
"""

import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
from quick_api import create_api


def custom_preprocessor(data):
    """Custom preprocessing function"""
    # Convert to numpy array
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    
    # Ensure 2D
    if data.ndim == 1:
        data = data.reshape(1, -1)
    
    # Apply log transformation
    data = np.log1p(np.abs(data))
    
    print(f"Preprocessed data shape: {data.shape}")
    return data


def custom_postprocessor(predictions):
    """Custom postprocessing function"""
    # Convert to list
    if isinstance(predictions, np.ndarray):
        predictions = predictions.tolist()
    
    # Round predictions to 2 decimal places
    if isinstance(predictions, list):
        predictions = [round(p, 2) for p in predictions]
    
    print(f"Postprocessed predictions: {predictions}")
    return predictions


def main():
    # Create sample regression data
    print("Creating sample regression dataset...")
    X, y = make_regression(
        n_samples=1000,
        n_features=5,
        noise=0.1,
        random_state=42
    )
    
    # Train a regression model
    print("Training Random Forest regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Save the model
    model_path = "example_regressor.pkl"
    joblib.dump(model, model_path)
    print(f"Model saved to: {model_path}")
    
    # Create API with custom preprocessing and postprocessing
    print("Creating API with custom preprocessing...")
    api = create_api(
        model_path=model_path,
        title="Custom Preprocessor API",
        description="A regression API with custom preprocessing and postprocessing",
        version="1.0.0",
        preprocess_func=custom_preprocessor,
        postprocess_func=custom_postprocessor
    )
    
    print("Starting API server...")
    print("Visit http://localhost:8000/docs for interactive documentation")
    print("Example prediction request:")
    print("POST http://localhost:8000/predict")
    print('{"data": [[1.0, 2.0, 3.0, 4.0, 5.0]]}')
    
    # Run the API
    api.run()


if __name__ == "__main__":
    main()
