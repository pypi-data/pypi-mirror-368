# searchmind/__init__.py

"""
SearchMind: A simple Python client for the Snapzion Search API.
"""

# Import the main search function to make it accessible at the package level
from .client import search

# Import custom exceptions
from .exceptions import SearchMindError, APIError, NetworkError

# Define the package version
__version__ = "0.1.0"

# Define what gets imported with 'from searchmind import *'
__all__ = [
    'search',
    'SearchMindError',
    'APIError',
    'NetworkError'
]