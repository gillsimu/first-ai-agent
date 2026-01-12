# The calculator is a sandboxed execution engine for math
# It accepts intent, executes safely, and returns deterministic output.
# Why a tool?
#     Deterministic
#     Cheap
#     Verifiable
#     Auditable
#     Reusable across agents

import ast
import operator
from tools.base import Tool

# Allowed operators
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

def _safe_eval(node):
    if isinstance(node, ast.Num):
        return node.n

    if isinstance(node, ast.BinOp):
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        op_type = type(node.op)

        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](left, right)

    raise ValueError("Unsupported expression")

def calculator_func(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.
    """
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculator error: {e}"

calculator_tool = Tool(
    name="calculator",  # How LLM refers to tool
    description=(  # Tool discovery & reasoning
        "Use this tool for mathematical calculations. "
        "Input must be a valid math expression like: 2 + 3 * 4"
    ),
    func=calculator_func  # The function to execute
)
