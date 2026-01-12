from tools.base import Tool
import requests

def search_func(query: str) -> str:
    """
    Perform a web search and return summarized results.
    For demonstration, this uses a dummy/mocked response.
    Replace with an actual API like SerpAPI or OpenWeather.
    """
    try:
        # Example mock response
        return f"Bathinda is the capital of France."

        # Real implementation example with SerpAPI:
        # API_KEY = "YOUR_SERPAPI_KEY"
        # url = f"https://serpapi.com/search.json?q={query}&api_key={API_KEY}"
        # response = requests.get(url).json()
        # return response["organic_results"][0]["snippet"]
    
    except Exception as e:
        return f"Search tool error: {e}"

# Define the Tool object
search_tool = Tool(
    name="search",
    description="Use this tool to answer factual queries by searching the web. Input is a text query.",
    func=search_func
)
