calculator_schema = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Perform safe mathematical calculations",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression like 2 + 3 * (4 - 1)"
                }
            },
            "required": ["expression"]
        }
    }
}
