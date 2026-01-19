calculator_descriptor = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": (
            "Use this agent to perform mathematical calculations. "
            "Input must be a valid math expression."
        ),
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

import ast
import operator

class CalculatorAgent:
    """
    Executes deterministic mathematical calculations.
    No LLM. No reasoning. Pure execution.
    """

    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
    }

    def _safe_eval(self, node):
        if isinstance(node, ast.Num):
            return node.n

        if isinstance(node, ast.BinOp):
            left = self._safe_eval(node.left)
            right = self._safe_eval(node.right)
            op_type = type(node.op)

            if op_type in self.SAFE_OPERATORS:
                return self.SAFE_OPERATORS[op_type](left, right)

        raise ValueError("Unsupported expression")

    def run(self, expression: str) -> str:
        try:
            tree = ast.parse(expression, mode="eval")
            result = self._safe_eval(tree.body)
            return f"Result: {result}"
        except Exception as e:
            return f"Calculator error: {e}"
