# Hello Agent 2

A compact learning project for three classic agent patterns from chapter 4 of the Hello-Agents tutorial:

- ReAct
- Plan-and-Solve
- Reflection

The project uses an OpenAI-compatible LLM API, so it can work with providers such as OpenAI or DeepSeek as long as `.env` is configured correctly.

## File Structure

```text
hello_agent_2/
├─ .env
├─ README.md
├─ requirements.txt
├─ try_agent.py
└─ try_agent_1/
   ├─ __init__.py
   ├─ core.py
   ├─ factory.py
   ├─ parsers.py
   ├─ prompts.py
   ├─ tools.py
   ├─ react.py
   ├─ plan.py
   └─ reflection.py
```

## Main Files

- `try_agent.py`: command-line entry point.
- `try_agent_1/core.py`: shared infrastructure, including `LLMClient`, `ToolExecutor`, and `Memory`.
- `try_agent_1/factory.py`: factory functions for creating configured agents.
- `try_agent_1/prompts.py`: all prompt templates in one place.
- `try_agent_1/parsers.py`: shared parsers for ReAct actions and Plan-and-Solve plans.
- `try_agent_1/tools.py`: external tools and tool registration, currently `Search` and `Calculator`.
- `try_agent_1/react.py`: ReAct agent implementation.
- `try_agent_1/plan.py`: Plan-and-Solve implementation, including `Planner`, `Executor`, and `PlanAndSolveAgent`.
- `try_agent_1/reflection.py`: Reflection agent implementation.

## Agent Types

### ReAct

ReAct follows a loop:

```text
Thought -> Action -> Observation -> ... -> Finish
```

The model reasons about the next step, chooses an action, receives an observation from a tool, and repeats until it returns a final answer.

Use this mode when the task may need external information, such as web search. It also includes a safe `Calculator` tool for exact arithmetic.

### Plan-and-Solve

Plan-and-Solve separates the task into two stages:

```text
Plan -> Execute each step -> Final answer
```

The planner first creates a full list of steps. The executor then completes each step in order while carrying forward previous results.

Use this mode for multi-step reasoning tasks where an explicit plan is useful.

### Reflection

Reflection uses an iterative improvement loop:

```text
Initial solution -> Review feedback -> Refined solution
```

The agent first generates a solution, then reviews it, and optionally refines it based on reviewer feedback.

Use this mode for code generation or tasks where the first answer should be checked and improved.

## Environment Setup

Install dependencies in the `agent1` conda environment:

```powershell
cd "D:\files for coding\learn agents\agent practice\hello_agent_2"
conda activate agent1
pip install -r requirements.txt
```

Required `.env` values:

```env
LLM_MODEL_ID="your-model-name"
LLM_BASE_URL="your-openai-compatible-base-url"
LLM_API_KEY="your-api-key"
SERPAPI_API_KEY="your-serpapi-key"
```

`SERPAPI_API_KEY` is only required when ReAct uses the `Search` tool.

Optional:

```env
LLM_TIMEOUT="60"
```

## Usage

Run from the project root:

```powershell
cd "D:\files for coding\learn agents\agent practice\hello_agent_2"
conda activate agent1
```

### ReAct

```powershell
python try_agent.py --mode react
```

With a custom question:

```powershell
python try_agent.py --mode react --question "Recommend a badminton racket to a beginner."
```

Set the maximum ReAct loop steps:

```powershell
python try_agent.py --mode react --question "Recommend a badminton racket to a beginner." --max-steps 5
```

Calculator example:

```powershell
python try_agent.py --mode react --question "Calculate (123 + 456) * 789 / 12."
```

### Plan-and-Solve

```powershell
python try_agent.py --mode plan
```

With a custom question:

```powershell
python try_agent.py --mode plan --question "Recommend a badminton racket to a beginner."
```

### Reflection

```powershell
python try_agent.py --mode reflection
```

With a custom task:

```powershell
python try_agent.py --mode reflection --question "Write a Python function that returns all prime numbers from 1 to n."
```

Set the maximum number of reflection iterations:

```powershell
python try_agent.py --mode reflection --question "Write a Python function that returns all prime numbers from 1 to n." --max-iterations 2
```

## CLI Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `--mode` | `react`, `plan`, `reflection` | `react` | Selects the agent pattern to run. |
| `--question` | text | mode-specific default | Question or task passed to the agent. |
| `--max-steps` | integer | `5` | Maximum ReAct loop steps. Used only in `react` mode. |
| `--max-iterations` | integer | `2` | Maximum Reflection review/refine iterations. Used only in `reflection` mode. |

## Import Usage

You can also use the package directly in Python:

```python
from try_agent_1 import build_react_agent, build_plan_agent, build_reflection_agent

react_agent = build_react_agent(max_steps=5)
print(react_agent.run("Recommend a badminton racket to a beginner."))

plan_agent = build_plan_agent()
print(plan_agent.run("Recommend a badminton racket to a beginner."))

reflection_agent = build_reflection_agent(max_iterations=2)
print(reflection_agent.run("Write a Python function that returns all prime numbers from 1 to n."))
```

