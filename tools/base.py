# tools/base.py
class Tool:
    def __init__(self, name: str, description: str, func):
        self.name = name
        self.description = description
        self.func = func

    def run(self, input_text: str) -> str:
        try:
            return self.func(input_text)
        except Exception as e:
            return f"Error in {self.name}: {e}"
