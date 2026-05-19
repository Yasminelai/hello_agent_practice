"""ReAct agent: Thought -> Action -> Observation."""

from typing import List, Optional

from .core import LLMClient, ToolExecutor
from .parsers import parse_action, parse_react_output
from .prompts import REACT_PROMPT


class ReActAgent:
    """Run a tool-using ReAct loop until Finish[...] or max_steps."""

    def __init__(self, llm_client: LLMClient, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history: List[str] = []

    def run(self, question: str) -> Optional[str]:
        self.history = []

        for step in range(1, self.max_steps + 1):
            print(f"\n--- Step {step} ---")
            prompt = REACT_PROMPT.format(
                tools=self.tool_executor.describe_tools(),
                question=question,
                history="\n".join(self.history) or "None",
            )
            response_text = self.llm_client.complete(prompt)
            if not response_text:
                print("Error: The LLM did not return a valid response.")
                return None

            thought, action = parse_react_output(response_text)
            if thought:
                print(f"Thought: {thought}")
            if not action:
                print(f"Warning: Could not parse a valid Action. Raw output:\n{response_text}")
                return None

            tool_name, tool_input = parse_action(action)
            if tool_name == "Finish":
                print(f"Finished: {tool_input}")
                return tool_input
            if not tool_name or not tool_input:
                observation = f"Error: Invalid Action format: {action}"
            else:
                print(f"Action: {tool_name}[{tool_input}]")
                tool = self.tool_executor.get_tool(tool_name)
                observation = tool(tool_input) if tool else f"Error: Tool '{tool_name}' was not found."

            print(f"Observation: {observation}")
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        print("Reached the maximum number of steps. The agent stopped.")
        return None
