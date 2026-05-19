"""Output parsers shared by the tutorial agents."""

import ast
import re
from typing import List, Optional, Tuple


def parse_react_output(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract Thought and Action sections from a ReAct model response."""
    thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
    action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
    thought = thought_match.group(1).strip() if thought_match else None
    action = action_match.group(1).strip() if action_match else None
    return thought, action


def parse_action(action_text: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse Action text such as Search[query] or `Finish[answer]`."""
    match = re.match(r"`?(\w+)\[(.*)\]`?", action_text.strip(), re.DOTALL)
    if not match:
        return None, None
    return match.group(1), match.group(2).strip()


def parse_python_list(response_text: str) -> List[str]:
    """Parse a Python list of strings from an LLM response.

    The planner is instructed to return a list inside a code block, but this
    parser also accepts a bare list as a fallback.
    """
    candidates = []

    code_block_match = re.search(r"```(?:python)?\s*(.*?)```", response_text, re.DOTALL)
    if code_block_match:
        candidates.append(code_block_match.group(1).strip())

    bracket_match = re.search(r"\[(.*)\]", response_text, re.DOTALL)
    if bracket_match:
        candidates.append("[" + bracket_match.group(1).strip() + "]")

    for candidate in candidates:
        try:
            parsed = ast.literal_eval(candidate)
        except (ValueError, SyntaxError):
            continue
        if isinstance(parsed, list) and all(isinstance(item, str) for item in parsed):
            return [item.strip() for item in parsed if item.strip()]

    return []
