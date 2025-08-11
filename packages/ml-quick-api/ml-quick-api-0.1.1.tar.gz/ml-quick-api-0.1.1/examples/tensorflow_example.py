"""
Example: Using Quick-API with TensorFlow/Keras model
"""

import numpy as np
import tensorflow as tf
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from quick_api import create_api


def main():
    # Create sample data
    print("Creating sample dataset...")
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_classes=2,
        random_state=42
    )
    
    # Split and scale the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Create a simple neural network
    print("Training neural network...")
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation='relu', input_shape=(10,)),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    # Train the model
    model.fit(
        X_train_scaled, y_train,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        verbose=1
    )
    
    # Save the model
    model_path = "example_neural_network.h5"
    model.save(model_path)
    print(f"Model saved to: {model_path}")
    
    # Create preprocessing function that includes scaling
    def preprocess_with_scaling(data):
        """Preprocess data with the same scaling used during training"""
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        
        if data.ndim == 1:
            data = data.reshape(1, -1)
        
        # Apply the same scaling
        scaled_data = scaler.transform(data)
        return scaled_data
    
    # Create API
    print("Creating API...")
    api = create_api(
        model_path=model_path,
        title="Neural Network Classifier API",
        description="A binary classifier built with TensorFlow/Keras",
        version="1.0.0",
        preprocess_func=preprocess_with_scaling
    )
    
    print("Starting API server...")
    print("Visit http://localhost:8000/docs for interactive documentation")
    print("Example prediction request:")
    print("POST http://localhost:8000/predict")
    print('{"data": [[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]]}')
    
    # Run the API
    api.run()


if __name__ == "__main__":
    main()
