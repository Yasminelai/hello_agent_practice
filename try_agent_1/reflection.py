"""Reflection agent: generate, review, and refine."""

from typing import Optional

from .core import LLMClient, Memory
from .prompts import INITIAL_SOLUTION_PROMPT, REFINE_PROMPT, REVIEW_PROMPT


class ReflectionAgent:
    """Improve a generated solution through reviewer feedback."""

    def __init__(self, llm_client: LLMClient, max_iterations: int = 2):
        self.llm_client = llm_client
        self.max_iterations = max_iterations
        self.memory = Memory()

    def run(self, task: str) -> Optional[str]:
        print(f"\n--- Starting Reflection ---\nTask: {task}")

        print("\n--- Initial execution ---")
        initial_solution = self.llm_client.complete(INITIAL_SOLUTION_PROMPT.format(task=task)) or ""
        if not initial_solution:
            print("Error: Initial execution did not return a solution.")
            return None
        self.memory.add("execution", initial_solution)

        for iteration in range(1, self.max_iterations + 1):
            print(f"\n--- Reflection iteration {iteration}/{self.max_iterations} ---")
            last_solution = self.memory.latest("execution")
            if not last_solution:
                print("Error: No previous execution found for reflection.")
                return None

            print("\n-> Reviewing latest solution...")
            feedback = self.llm_client.complete(REVIEW_PROMPT.format(task=task, code=last_solution)) or ""
            if not feedback:
                print("Error: Reflection did not return feedback.")
                return None
            self.memory.add("reflection", feedback)
            print(f"Reviewer feedback:\n{feedback}")

            if "NO_IMPROVEMENT_NEEDED" in feedback:
                print("\nReflection says no further improvement is needed.")
                break

            print("\n-> Refining solution...")
            refined_solution = self.llm_client.complete(
                REFINE_PROMPT.format(
                    task=task,
                    last_solution=last_solution,
                    feedback=feedback,
                    trajectory=self.memory.render(),
                )
            ) or ""
            if not refined_solution:
                print("Error: Refinement did not return a solution.")
                return None
            self.memory.add("execution", refined_solution)
            print(f"Refined solution:\n{refined_solution}")

        final_solution = self.memory.latest("execution")
        print(f"\n--- Reflection complete ---\nFinal solution:\n{final_solution}")
        return final_solution
