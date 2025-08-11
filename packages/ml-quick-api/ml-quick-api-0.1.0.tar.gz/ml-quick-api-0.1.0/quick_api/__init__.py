"""
Quick-API: Turn a Model into an API in One Line

A Python library that wraps saved machine learning models in a simple REST API.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import create_api
from .api import QuickAPI

__all__ = ["create_api", "QuickAPI"]
