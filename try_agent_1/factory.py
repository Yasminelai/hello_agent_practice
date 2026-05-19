"""Factory functions for creating configured tutorial agents."""

from .core import LLMClient, ToolExecutor
from .plan import PlanAndSolveAgent
from .react import ReActAgent
from .reflection import ReflectionAgent
from .tools import search


SEARCH_TOOL_DESCRIPTION = (
    "A web search engine. Use it when the answer requires current facts, "
    "external knowledge, or information not already available in the prompt."
)


def build_react_agent(max_steps: int = 5) -> ReActAgent:
    """Build a ReAct agent with the Search tool registered."""
    llm_client = LLMClient()
    tool_executor = ToolExecutor()
    tool_executor.register_tool("Search", SEARCH_TOOL_DESCRIPTION, search)
    return ReActAgent(llm_client=llm_client, tool_executor=tool_executor, max_steps=max_steps)


def build_plan_agent() -> PlanAndSolveAgent:
    """Build a Plan-and-Solve agent."""
    return PlanAndSolveAgent(llm_client=LLMClient())


def build_reflection_agent(max_iterations: int = 2) -> ReflectionAgent:
    """Build a Reflection agent."""
    return ReflectionAgent(llm_client=LLMClient(), max_iterations=max_iterations)
