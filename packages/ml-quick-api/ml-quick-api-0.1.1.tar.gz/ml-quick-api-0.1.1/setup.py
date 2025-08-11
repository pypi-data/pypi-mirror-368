from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ml-quick-api",
    version="0.1.1",
    author="Your Name",
    author_email="abhishek.naiir@gmail.com",
    description="Turn a Model into an API in One Line",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AbhishekNair050/quick-api",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
        "numpy>=1.19.0",
        "scikit-learn>=0.24.0",
        "joblib>=1.0.0",
        "tensorflow>=2.6.0; platform_machine != 'arm64'",
        "keras>=2.6.0; platform_machine != 'arm64'",
        "torch>=1.9.0; platform_machine != 'arm64'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.15.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "quick-api=quick_api.cli:main",
        ],
    },
)
