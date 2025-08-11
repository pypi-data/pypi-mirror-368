# searchmind/client.py

import requests
import json
from .exceptions import APIError, NetworkError

# The API endpoint URL
API_URL = "https://search.snapzion.com/get-snippets"

# Headers to mimic a real browser request, as seen in your cURL command.
# We only need the most important ones.
HEADERS = {
    'accept': '*/*',
    'content-type': 'application/json',
    'origin': 'https://search.snapzion.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
}

def search(query: str, timeout: int = 15) -> dict:
    """
    Performs a search using the Snapzion Search API.

    This function sends a query to the Snapzion API and returns the search results.

    Args:
        query (str): The search term you want to look up.
        timeout (int, optional): The number of seconds to wait for a server
                                 response. Defaults to 15.

    Returns:
        dict: A dictionary containing the search results, typically with a
              key 'organic_results'.

    Raises:
        TypeError: If the provided query is not a string.
        NetworkError: If there's a problem with the network connection
                      (e.g., timeout, DNS error).
        APIError: If the API responds with an error status code or if the
                  response is not valid JSON.
    """
    if not isinstance(query, str):
        raise TypeError("The search query must be a string.")

    if not query.strip():
        raise ValueError("The search query cannot be empty.")

    payload = {"query": query}

    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json=payload,
            timeout=timeout
        )

        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()

        # Try to parse the JSON response
        return response.json()

    except requests.exceptions.HTTPError as e:
        # This catches non-200 status codes
        raise APIError(f"API Error: Received status {e.response.status_code}. Response: {e.response.text}") from e
    except requests.exceptions.RequestException as e:
        # This catches connection errors, timeouts, etc.
        raise NetworkError(f"A network error occurred: {e}") from e
    except json.JSONDecodeError:
        # This catches cases where the response is not valid JSON
        raise APIError("Failed to decode the API response. It was not valid JSON.")