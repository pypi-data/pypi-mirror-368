# searchmind/exceptions.py

class SearchMindError(Exception):
    """Base exception for the searchmind library."""
    pass

class APIError(SearchMindError):
    """Raised when the Snapzion API returns an error status or malformed response."""
    pass

class NetworkError(SearchMindError):
    """Raised for network-related issues (e.g., connection timeout)."""
    pass