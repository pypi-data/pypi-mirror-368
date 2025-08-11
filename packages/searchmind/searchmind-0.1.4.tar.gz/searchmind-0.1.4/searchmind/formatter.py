# searchmind/formatter.py

from typing import List, Dict, Any

def format_for_llm(results: List[Dict[str, Any]]) -> str:
    """
    Formats a list of search results into a single, concise string
    suitable for use in an LLM prompt.

    Args:
        results (List[Dict[str, Any]]): The list of results from SearchMindClient.search().

    Returns:
        str: A formatted string containing the search results.
    """
    if not results:
        return "No search results found."
    
    formatted_snippets = []
    for result in results:
        snippet_parts = []
        snippet_parts.append(f"[{result.get('position', 'N/A')}] Title: {result.get('title', 'No Title')}")
        snippet_parts.append(f"Snippet: {result.get('snippet', 'No Snippet')}")
        snippet_parts.append(f"URL: {result.get('link', 'No Link')}")
        
        if 'date' in result:
            snippet_parts.append(f"Date: {result.get('date')}")
            
        formatted_snippets.append("\n".join(snippet_parts))
        
    return "\n\n".join(formatted_snippets)