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
