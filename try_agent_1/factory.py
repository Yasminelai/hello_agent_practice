"""Factory functions for creating configured tutorial agents."""

from .core import LLMClient, ToolExecutor
from .plan import PlanAndSolveAgent
from .react import ReActAgent
from .reflection import ReflectionAgent
from .tools import register_default_tools


def build_react_agent(max_steps: int = 5) -> ReActAgent:
    """Build a ReAct agent with all default tools registered."""
    llm_client = LLMClient()
    tool_executor = register_default_tools(ToolExecutor())
    return ReActAgent(llm_client=llm_client, tool_executor=tool_executor, max_steps=max_steps)


def build_plan_agent() -> PlanAndSolveAgent:
    """Build a Plan-and-Solve agent."""
    return PlanAndSolveAgent(llm_client=LLMClient())


def build_reflection_agent(max_iterations: int = 2) -> ReflectionAgent:
    """Build a Reflection agent."""
    return ReflectionAgent(llm_client=LLMClient(), max_iterations=max_iterations)
