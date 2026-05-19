"""Shared infrastructure for all learning agents.

This module keeps provider access, tool registration, and short-term memory in
one place so the three agent patterns can share the same building blocks.
"""

import os
from typing import Any, Callable, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class LLMClient:
    """OpenAI-compatible chat completion client.

    The client works with OpenAI and compatible providers such as DeepSeek when
    the correct model id, API key, and base URL are configured in .env.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.model = model or os.getenv("LLM_MODEL_ID")
        api_key = api_key or os.getenv("LLM_API_KEY")
        base_url = base_url or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", "60"))

        if not all([self.model, api_key, base_url]):
            raise ValueError("Please configure LLM_MODEL_ID, LLM_API_KEY, and LLM_BASE_URL in .env.")

        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

    def complete(self, prompt: str, temperature: float = 0) -> Optional[str]:
        """Send a single prompt and return the assistant text."""
        return self.chat([{"role": "user", "content": prompt}], temperature=temperature)

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0) -> Optional[str]:
        """Send chat messages and return the assistant text.

        temperature defaults to 0 because these tutorial agents depend on stable
        output formats such as Action[...] and Python lists.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            print(f"Error while calling the LLM API: {exc}")
            return None


# Backward-friendly alias for earlier tutorial code.
HelloAgentsLLM = LLMClient


class ToolExecutor:
    """Register tools and dispatch tool calls by name."""

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, name: str, description: str, func: Callable[[str], str]) -> None:
        """Add one callable tool to the registry."""
        self.tools[name] = {"description": description, "func": func}

    def get_tool(self, name: str) -> Optional[Callable[[str], str]]:
        """Return a registered tool function by name, or None if missing."""
        tool = self.tools.get(name)
        return tool["func"] if tool else None

    def describe_tools(self) -> str:
        """Format all registered tools for prompt injection."""
        return "\n".join(
            f"- {name}: {info['description']}" for name, info in self.tools.items()
        )


class Memory:
    """Chronological text memory used by iterative agents."""

    def __init__(self):
        self.records: List[Dict[str, str]] = []

    def add(self, record_type: str, content: str) -> None:
        """Add one memory record."""
        self.records.append({"type": record_type, "content": content})
        print(f"Memory updated: added one '{record_type}' record.")

    def render(self) -> str:
        """Render records as prompt-ready text."""
        parts = []
        for record in self.records:
            label = record["type"].replace("_", " ").title()
            parts.append(f"--- {label} ---\n{record['content']}")
        return "\n\n".join(parts)

    def latest(self, record_type: str) -> Optional[str]:
        """Return the latest record content for a type."""
        for record in reversed(self.records):
            if record["type"] == record_type:
                return record["content"]
        return None
