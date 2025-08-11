# agentik/tools/calculator.py
"""
Safe math evaluator (AST-based).
Supports + - * / // % **, parentheses, and selected math functions.
"""
import ast
import operator as op
import math

from agentik.tools.base import Tool

_ALLOWED_FUNCS = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
_ALLOWED_NAMES = {**_ALLOWED_FUNCS, "pi": math.pi, "e": math.e}
_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}

def _eval(node):
    if isinstance(node, ast.Num):  # py<3.8
        return node.n
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("constants other than numbers not allowed")
    if isinstance(node, ast.BinOp):
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return _OPS[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Call):
        fn = _eval(node.func)
        args = [_eval(a) for a in node.args]
        return fn(*args)
    if isinstance(node, ast.Name):
        if node.id in _ALLOWED_NAMES:
            return _ALLOWED_NAMES[node.id]
        raise ValueError(f"name '{node.id}' not allowed")
    if isinstance(node, ast.Attribute):
        raise ValueError("attributes not allowed")
    raise ValueError("unsupported expression")

class CalculatorTool(Tool):
    name = "calculator"
    description = "Evaluate math expressions safely. Example: 'calculator sin(pi/2) + 3**2'"

    def run(self, input_text: str) -> str:
        expr = input_text[len(self.name):].strip().lstrip(":").strip()
        if not expr:
            return "[CalculatorTool] Provide an expression."
        try:
            tree = ast.parse(expr, mode="eval")
            result = _eval(tree.body)
            return f"Result: {result}"
        except Exception as e:
            return f"[CalculatorTool Error] {e}"
