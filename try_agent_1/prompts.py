"""Prompt templates for the chapter-4 learning agents."""

REACT_PROMPT = """
You are a helpful assistant that can call external tools.

Available tools:
{tools}

You must respond in exactly the following format:

Thought: Your reasoning process. Use this to analyze the question, break down the task, and decide the next step.
Action: The action you want to take. It must be one of the following forms:
- `{{tool_name}}[{{tool_input}}]`: Call one available tool.
- `Finish[final_answer]`: Return the final answer when you have enough information.

Rules:
- Use only tools listed in Available tools.
- Use Calculator for exact arithmetic instead of doing mental math.
- Do not invent observations. Observations are provided by the program after tool calls.
- When you have enough information to answer the original question, use `Finish[final_answer]`.
- Keep the final answer concise and directly useful.

Question: {question}
History: {history}
""".strip()

PLAN_PROMPT = """
You are an expert AI planner. Break the user's problem into a clear sequence of small, executable steps.

Rules:
- Keep the steps logically ordered.
- Do not solve the problem in this phase.
- Return only a Python list of strings inside a python code block.

Question: {question}

Output format:
```python
["step 1", "step 2", "step 3"]
```
""".strip()

SOLVE_STEP_PROMPT = """
You are an expert AI executor. Follow the given plan step by step.

Original question:
{question}

Full plan:
{plan}

Previous step results:
{history}

Current step:
{current_step}

Return only the result for the current step.
""".strip()

INITIAL_SOLUTION_PROMPT = """
You are a senior Python developer. Write Python code for the following task.

Requirements:
- Include a complete function signature.
- Include a clear docstring.
- Follow PEP 8 style.
- Return only code. Do not add explanations outside the code block.

Task:
{task}
""".strip()

REVIEW_PROMPT = """
You are a strict code reviewer and senior algorithm engineer. Review the Python code below.

Focus on:
- Algorithmic efficiency.
- Time and space complexity.
- Logical correctness.
- Edge cases.
- Whether a significantly better algorithm exists.

Original task:
{task}

Code to review:
```python
{code}
```

If the code can be improved, give specific, actionable feedback.
If the code is already good enough for the task, include the exact phrase: NO_IMPROVEMENT_NEEDED.
Return only the feedback.
""".strip()

REFINE_PROMPT = """
You are a senior Python developer improving code based on reviewer feedback.

Original task:
{task}

Previous code attempt:
{last_solution}

Reviewer feedback:
{feedback}

Full reflection trajectory:
{trajectory}

Generate an improved version of the code.
Requirements:
- Include a complete function signature.
- Include a clear docstring.
- Follow PEP 8 style.
- Return only code. Do not add explanations outside the code block.
""".strip()
