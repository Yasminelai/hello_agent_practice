"""Command-line entry point for the chapter-4 learning agents."""

import argparse

from try_agent_1 import build_plan_agent, build_react_agent, build_reflection_agent


DEFAULT_REACT_QUESTION = "What is the latest Huawei phone, and what are its main selling points?"
DEFAULT_PLAN_QUESTION = (
    "A fruit shop sold 15 apples on Monday. On Tuesday it sold twice as many as Monday. "
    "On Wednesday it sold 5 fewer apples than Tuesday. How many apples were sold in total?"
)
DEFAULT_REFLECTION_TASK = "Write a Python function that returns all prime numbers from 1 to n."


def parse_args() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description="Run a chapter-4 learning agent.")
    parser.add_argument(
        "--mode",
        choices=("react", "plan", "reflection"),
        default="react",
        help="Agent pattern to run.",
    )
    parser.add_argument(
        "--question",
        default=None,
        help="Question or task to answer. If omitted, the program asks interactively.",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=5,
        help="Maximum ReAct loop steps. Only used in react mode.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=2,
        help="Maximum Reflection review/refine iterations. Only used in reflection mode.",
    )
    return parser.parse_args()


def default_question(mode: str) -> str:
    """Return a mode-specific default prompt."""
    if mode == "plan":
        return DEFAULT_PLAN_QUESTION
    if mode == "reflection":
        return DEFAULT_REFLECTION_TASK
    return DEFAULT_REACT_QUESTION


def read_question(mode: str, question_arg: str | None) -> str:
    """Get the question from CLI, stdin, or a mode-specific default."""
    if question_arg:
        return question_arg.strip()

    try:
        question = input("Enter your question or task: ").strip()
    except EOFError:
        question = ""

    if question:
        return question

    question = default_question(mode)
    print(f"No question entered. Using default question: {question}")
    return question


def main() -> None:
    """Run the selected agent from the terminal."""
    args = parse_args()
    question = read_question(args.mode, args.question)

    if args.mode == "plan":
        agent = build_plan_agent()
    elif args.mode == "reflection":
        agent = build_reflection_agent(max_iterations=args.max_iterations)
    else:
        agent = build_react_agent(max_steps=args.max_steps)

    answer = agent.run(question)

    print("\nFinal answer:")
    if answer:
        print(answer)
    else:
        print("The agent did not produce a final answer.")


if __name__ == "__main__":
    main()
