# searchmind/client.py

import requests
from typing import List, Dict, Any
from .exceptions import APIError

class SearchMindClient:
    """
    A Python client for the Snapzion Search API.
    """
    
    BASE_URL = "https://search.snapzion.com/get-snippets"
    
    def __init__(self, timeout: int = 10):
        """
        Initializes the SearchMindClient.

        Args:
            timeout (int): The request timeout in seconds.
        """
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': f'SearchMind-Python-Client/0.1.3' # Updated User-Agent
        })
        self.timeout = timeout

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Performs a search query and returns the organic results.

        Args:
            query (str): The search term.

        Returns:
            List[Dict[str, Any]]: A list of search result dictionaries.

        Raises:
            APIError: If the API call fails or returns a non-200 status.
        """
        payload = {"query": query}
        
        try:
            response = self.session.post(
                self.BASE_URL,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise APIError(f"Network error during API request: {e}") from e

        try:
            data = response.json()
            return data.get("organic_results", [])
        except ValueError:
            raise APIError("Failed to decode JSON from API response.", response.status_code)