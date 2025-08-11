# searchmind/exceptions.py

class SearchMindError(Exception):
    """Base exception class for the searchmind library."""
    pass

class APIError(SearchMindError):
    """Raised when the API returns an error status code or invalid response."""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

    def __str__(self):
        if self.status_code:
            return f"API Error (Status {self.status_code}): {self.args[0]}"
        return f"API Error: {self.args[0]}"