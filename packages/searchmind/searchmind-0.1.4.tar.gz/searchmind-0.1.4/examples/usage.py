# examples/usage.py

from searchmind import SearchMindClient, format_for_llm, APIError

def run_example():
    """Demonstrates basic and LLM-focused usage of the searchmind library."""
    
    print("--- Basic Usage Example ---")
    
    # 1. Initialize the client
    client = SearchMindClient()

    # 2. Perform a search
    query = "artificial intelligence trends"
    try:
        results = client.search(query)
        
        print(f"Found {len(results)} results for '{query}':\n")
        for item in results[:3]: # Print first 3 results
            print(f"[{item.get('position')}] {item.get('title')}")
            print(f"   Link: {item.get('link')}\n")

    except APIError as e:
        print(f"An error occurred: {e}")
        return

    print("\n" + "="*50 + "\n")

    print("--- LLM Formatter Example ---")

    # 3. Format the same results for an LLM
    search_context = format_for_llm(results)
    print("Formatted context string to be passed to an LLM:\n")
    print(search_context)

if __name__ == "__main__":
    run_example()