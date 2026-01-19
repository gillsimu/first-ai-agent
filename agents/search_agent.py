search_schema = {
    "type": "function",
    "function": {
        "name": "search",
        "description": "Search the web for factual information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query, e.g., 'Python programming tutorials'"
                }
            },
            "required": ["query"]
        }
    }
}


from typing import Dict, Any

class SearchAgent:
    """
    Executes factual searches using external APIs.
    No LLM. No reasoning. Pure data retrieval.
    """

    def __init__(self, api_key: str, provider: str = "serpapi"):
        self.api_key = api_key
        self.provider = provider

    def run(self, query: str) -> Dict[str, Any]:
        if not query or not isinstance(query, str):
            return {"error": "Invalid query"}

        try:
            if self.provider == "serpapi":
                return self._search_serpapi(query)
            else:
                return {"error": f"Unsupported provider: {self.provider}"}

        except Exception as e:
            return {"error": str(e)}

    def _search_serpapi(self, query: str) -> Dict[str, Any]:
        """
        Perform a web search and return summarized results.
        For demonstration, this uses a dummy/mocked response.
        Replace with an actual API like SerpAPI or OpenWeather.
        """
        try:
            # Example mock response
            return {"result": "Bathinda is the capital of France."}

            # Real implementation example with SerpAPI:
            # API_KEY = "YOUR_SERPAPI_KEY"
            # url = f"https://serpapi.com/search.json?q={query}&api_key={API_KEY}"
            # response = requests.get(url).json()
            # return response["organic_results"][0]["snippet"]
        
        except Exception as e:
            return {"error": f"Search tool error: {e}"}
