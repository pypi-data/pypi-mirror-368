# Quick-API

Turn a Model into an API in One Line

Quick-API is a Python library that wraps saved machine learning models (like `.pkl`, `.h5`, `.joblib` files) in a simple REST API using FastAPI with just one line of code.

## Features

- 🚀 **One-line API creation** - Turn any saved model into a REST API instantly
- 🔄 **Auto data conversion** - Automatically handles JSON to NumPy array conversion
- 📊 **Multiple model formats** - Supports scikit-learn, TensorFlow/Keras, PyTorch models
- ⚡ **FastAPI powered** - Built on FastAPI for high performance and automatic documentation
- 🔍 **Automatic endpoint discovery** - Creates `/predict` endpoint automatically
- 📝 **Interactive docs** - Get Swagger UI documentation out of the box
- 🛡️ **Input validation** - Built-in request validation and error handling

## Installation

```bash
pip install quick-api
```

## Quick Start

### 1. Basic Usage

```python
from quick_api import create_api

# Turn your model into an API with one line
api = create_api("path/to/your/model.pkl")

# Run the API
api.run()
```

### 2. Advanced Usage

```python
from quick_api import create_api

# Create API with custom configuration
api = create_api(
    model_path="models/my_classifier.pkl",
    host="0.0.0.0",
    port=8080,
    title="My ML API",
    description="A custom machine learning API",
    version="1.0.0"
)

# Run with custom settings
api.run(reload=True, workers=4)
```

### 3. Using the API

Once your API is running, you can make predictions:

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"data": [[1.0, 2.0, 3.0, 4.0]]}'
```

Or visit `http://localhost:8000/docs` for interactive Swagger documentation.

## Supported Model Types

- **Scikit-learn models** (`.pkl`, `.joblib`)
- **TensorFlow/Keras models** (`.h5`, `.keras`, saved_model format)
- **PyTorch models** (`.pt`, `.pth`)
- **Custom models** with predict method

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predict` | POST | Make predictions with your model |
| `/health` | GET | Check API health status |
| `/info` | GET | Get model information |
| `/docs` | GET | Interactive API documentation |

## Examples

### Scikit-learn Example

```python
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from quick_api import create_api

# Train and save a model
X, y = make_classification(n_samples=1000, n_features=4)
model = RandomForestClassifier()
model.fit(X, y)
joblib.dump(model, "classifier.pkl")

# Create API
api = create_api("classifier.pkl")
api.run()
```

### TensorFlow Example

```python
import tensorflow as tf
from quick_api import create_api

# Assuming you have a saved TensorFlow model
api = create_api("path/to/model.h5")
api.run()
```

## Configuration Options

```python
api = create_api(
    model_path="model.pkl",           # Path to your model file
    host="localhost",                 # Host to run the API on
    port=8000,                       # Port to run the API on
    title="Quick-API",               # API title
    description="ML Model API",      # API description
    version="1.0.0",                # API version
    input_shape=None,                # Expected input shape (auto-detected)
    preprocess_func=None,            # Custom preprocessing function
    postprocess_func=None,           # Custom postprocessing function
)
```

## CLI Usage

Quick-API also provides a command-line interface:

```bash
# Basic usage
quick-api serve model.pkl

# With custom options
quick-api serve model.pkl --host 0.0.0.0 --port 8080 --title "My API"
```

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/quick-api.git
cd quick-api

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black quick_api/

# Type checking
mypy quick_api/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.0
- Initial release
- Support for scikit-learn, TensorFlow, and PyTorch models
- FastAPI-based REST API
- Automatic documentation
- CLI interface
