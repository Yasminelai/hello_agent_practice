"""Plan-and-Solve agent: plan first, execute second."""

from typing import List, Optional

from .core import LLMClient
from .parsers import parse_python_list
from .prompts import PLAN_PROMPT, SOLVE_STEP_PROMPT


class Planner:
    """Generate an ordered plan for a user question."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def plan(self, question: str) -> List[str]:
        print("--- Generating plan ---")
        response_text = self.llm_client.complete(PLAN_PROMPT.format(question=question)) or ""
        print(f"Plan response:\n{response_text}")

        steps = parse_python_list(response_text)
        if not steps:
            print("Error: Could not parse a valid plan from the LLM response.")
        return steps


class Executor:
    """Execute planned steps while carrying forward previous results."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def execute(self, question: str, plan: List[str]) -> Optional[str]:
        if not plan:
            print("Error: Cannot execute an empty plan.")
            return None

        history = ""
        last_result: Optional[str] = None

        print("\n--- Executing plan ---")
        for index, step in enumerate(plan, start=1):
            print(f"\n-> Step {index}/{len(plan)}: {step}")
            prompt = SOLVE_STEP_PROMPT.format(
                question=question,
                plan=plan,
                history=history or "None",
                current_step=step,
            )
            step_result = self.llm_client.complete(prompt) or ""
            if not step_result:
                print(f"Error: Step {index} did not return a result.")
                return None

            last_result = step_result.strip()
            history += f"Step {index}: {step}\nResult: {last_result}\n\n"
            print(f"Step {index} result: {last_result}")

        return last_result


class PlanAndSolveAgent:
    """Coordinate Planner and Executor."""

    def __init__(self, llm_client: LLMClient):
        self.planner = Planner(llm_client)
        self.executor = Executor(llm_client)

    def run(self, question: str) -> Optional[str]:
        print(f"\n--- Starting Plan-and-Solve ---\nQuestion: {question}")

        plan = self.planner.plan(question)
        if not plan:
            print("\n--- Task stopped: no valid plan was generated. ---")
            return None

        print("\nParsed plan:")
        for index, step in enumerate(plan, start=1):
            print(f"{index}. {step}")

        final_answer = self.executor.execute(question, plan)
        print(f"\n--- Plan-and-Solve complete ---\nFinal answer: {final_answer}")
        return final_answer
