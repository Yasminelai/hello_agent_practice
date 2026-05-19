"""External tools available to tool-using agents.

To add a new ReAct tool:
1. Write a function that accepts one string and returns one string.
2. Add a ToolSpec entry to DEFAULT_TOOL_SPECS.
3. The factory will register it automatically.
"""

import ast
import operator
import os
from dataclasses import dataclass
from typing import Callable, List

from dotenv import load_dotenv
from serpapi import SerpApiClient

from .core import ToolExecutor


load_dotenv()


@dataclass(frozen=True)
class ToolSpec:
    """Declarative description of a callable tool."""

    name: str
    description: str
    func: Callable[[str], str]


def search(query: str) -> str:
    """Search the web with SerpApi and return a concise observation."""
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return "Error: SERPAPI_API_KEY is not configured in .env."

    try:
        client = SerpApiClient(
            {
                "engine": "google",
                "q": query,
                "api_key": api_key,
                "gl": "cn",
                "hl": "en",
            }
        )
        results = client.get_dict()

        if "answer_box_list" in results:
            return "\n".join(str(item) for item in results["answer_box_list"])

        answer_box = results.get("answer_box", {})
        if answer_box.get("answer"):
            return answer_box["answer"]
        if answer_box.get("snippet"):
            return answer_box["snippet"]

        knowledge_graph = results.get("knowledge_graph", {})
        if knowledge_graph.get("description"):
            return knowledge_graph["description"]

        organic_results = results.get("organic_results", [])
        if organic_results:
            snippets = []
            for index, item in enumerate(organic_results[:3], start=1):
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                snippets.append(f"[{index}] {title}\n{snippet}".strip())
            return "\n\n".join(snippets)

        return f"No information was found for '{query}'."
    except Exception as exc:
        return f"Error while searching: {exc}"


_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def calculator(expression: str) -> str:
    """Safely evaluate an arithmetic expression.

    Supported syntax:
    - numbers
    - parentheses
    - +, -, *, /, //, %, **
    - unary + and -

    Function calls, names, attributes, imports, and all other Python syntax are
    rejected. This keeps the calculator useful for ReAct while avoiding plain
    eval().
    """
    normalized_expression = (
        expression.strip()
        .replace("×", "*")
        .replace("÷", "/")
        .replace("^", "**")
    )

    if not normalized_expression:
        return "Error: Calculator received an empty expression."

    try:
        tree = ast.parse(normalized_expression, mode="eval")
        result = _evaluate_math_node(tree.body)
    except ZeroDivisionError:
        return "Error: Division by zero."
    except Exception as exc:
        return f"Error: Invalid arithmetic expression: {exc}"

    if isinstance(result, float) and result.is_integer():
        result = int(result)
    return str(result)


def _evaluate_math_node(node: ast.AST) -> int | float:
    """Recursively evaluate only whitelisted arithmetic AST nodes."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp):
        operator_func = _BINARY_OPERATORS.get(type(node.op))
        if not operator_func:
            raise ValueError(f"unsupported operator: {type(node.op).__name__}")
        left = _evaluate_math_node(node.left)
        right = _evaluate_math_node(node.right)
        return operator_func(left, right)

    if isinstance(node, ast.UnaryOp):
        operator_func = _UNARY_OPERATORS.get(type(node.op))
        if not operator_func:
            raise ValueError(f"unsupported unary operator: {type(node.op).__name__}")
        operand = _evaluate_math_node(node.operand)
        return operator_func(operand)

    raise ValueError(f"unsupported expression: {type(node).__name__}")


DEFAULT_TOOL_SPECS: List[ToolSpec] = [
    ToolSpec(
        name="Search",
        description=(
            "A web search engine. Use it when the answer requires current facts, "
            "external knowledge, or information not already available in the prompt."
        ),
        func=search,
    ),
    ToolSpec(
        name="Calculator",
        description=(
            "A safe arithmetic calculator. Use it for exact math expressions. "
            "Input should contain only numbers, parentheses, and arithmetic operators."
        ),
        func=calculator,
    ),
]


def register_tools(tool_executor: ToolExecutor, tool_specs: List[ToolSpec]) -> ToolExecutor:
    """Register a list of tool specs into a ToolExecutor."""
    for spec in tool_specs:
        tool_executor.register_tool(spec.name, spec.description, spec.func)
    return tool_executor


def register_default_tools(tool_executor: ToolExecutor) -> ToolExecutor:
    """Register the default ReAct tools."""
    return register_tools(tool_executor, DEFAULT_TOOL_SPECS)
