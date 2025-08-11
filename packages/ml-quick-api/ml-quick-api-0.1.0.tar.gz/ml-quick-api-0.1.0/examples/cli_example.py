"""
Example: Using Quick-API with CLI commands
"""

import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification


def create_sample_model():
    """Create and save a sample model for testing CLI"""
    print("Creating sample model for CLI testing...")
    
    # Create sample data
    X, y = make_classification(
        n_samples=1000,
        n_features=4,
        n_classes=3,
        n_redundant=0,
        random_state=42
    )
    
    # Train model
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    # Save model
    model_path = "cli_test_model.pkl"
    joblib.dump(model, model_path)
    print(f"Model saved to: {model_path}")
    
    return model_path


def main():
    model_path = create_sample_model()
    
    print("\nNow you can test the CLI commands:")
    print("\n1. Get model information:")
    print(f"   quick-api info {model_path}")
    
    print("\n2. Serve the model (basic):")
    print(f"   quick-api serve {model_path}")
    
    print("\n3. Serve with custom settings:")
    print(f"   quick-api serve {model_path} --host 0.0.0.0 --port 8080 --title 'My CLI API'")
    
    print("\n4. Serve with development mode:")
    print(f"   quick-api serve {model_path} --reload")
    
    print("\n5. Test prediction with curl:")
    print('   curl -X POST "http://localhost:8000/predict" \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"data": [[1.0, 2.0, 3.0, 4.0]]}\'')
    
    print(f"\nModel file created: {model_path}")
    print("Run the commands above to test the CLI interface!")


if __name__ == "__main__":
    main()
