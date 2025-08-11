"""
Example: Basic usage of Quick-API with a scikit-learn model
"""

import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from quick_api import create_api


def main():
    # Create sample data
    print("Creating sample dataset...")
    X, y = make_classification(
        n_samples=1000,
        n_features=4,
        n_classes=2,
        random_state=42
    )
    
    # Train a simple model
    print("Training Random Forest model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Save the model
    model_path = "example_classifier.pkl"
    joblib.dump(model, model_path)
    print(f"Model saved to: {model_path}")
    
    # Create API with one line
    print("Creating API...")
    api = create_api(
        model_path=model_path,
        title="Example Classifier API",
        description="A simple binary classifier built with Random Forest",
        version="1.0.0"
    )
    
    print("Starting API server...")
    print("Visit http://localhost:8000/docs for interactive documentation")
    print("Example prediction request:")
    print("POST http://localhost:8000/predict")
    print('{"data": [[1.0, 2.0, 3.0, 4.0]]}')
    
    # Run the API
    api.run()


if __name__ == "__main__":
    main()
