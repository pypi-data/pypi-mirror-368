# Quick-API Development Guide

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/quick-api.git
cd quick-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

## Running Tests

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=quick_api --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_api.py
```

## Code Formatting

Format code with Black:
```bash
black quick_api/ tests/
```

Check code style:
```bash
flake8 quick_api/ tests/
```

Type checking:
```bash
mypy quick_api/
```

## Building and Publishing

1. Build the package:
```bash
python -m build
```

2. Check the package:
```bash
twine check dist/*
```

3. Upload to TestPyPI (for testing):
```bash
twine upload --repository testpypi dist/*
```

4. Upload to PyPI:
```bash
twine upload dist/*
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Project Structure

```
quick-api/
├── quick_api/           # Main package
│   ├── __init__.py     # Package initialization
│   ├── core.py         # Core API creation function
│   ├── api.py          # FastAPI application
│   ├── model_loader.py # Model loading utilities
│   ├── utils.py        # Utility functions
│   └── cli.py          # Command-line interface
├── tests/              # Test suite
├── examples/           # Usage examples
├── setup.py           # Setup configuration
├── pyproject.toml     # Modern Python packaging
└── README.md          # Documentation
```

## Adding New Model Types

To add support for a new model type:

1. Update `ModelLoader._detect_model_type()` to recognize the file format
2. Add a new `_load_<type>_model()` method
3. Add prediction logic in `QuickAPI._predict_<type>()`
4. Add tests for the new model type

## Release Process

1. Update version in `setup.py` and `pyproject.toml`
2. Update CHANGELOG.md
3. Create a git tag
4. Build and upload to PyPI
