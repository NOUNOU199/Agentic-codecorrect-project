# Copilot Instructions for TP-OGL: AI Agent Refactoring Evaluation

## Project Overview
**TP IGL (2025-2026)**: Scientific evaluation of AI coding agents performing code refactoring tasks using LLM-based analysis and generation. This project creates a controlled experiment environment to measure agent effectiveness on legacy code improvement.

**Objective**: Deploy multi-agent swarms to analyze and refactor code, logging all interactions for post-experiment analysis.

**Stack**: Python 3.10+, LangChain, LangGraph, Google Generative AI

---

## Architecture & Critical Data Flow

### Core Components

1. **Entry Point** [main.py](main.py)
   - Accepts `--target_dir` parameter pointing to code to be analyzed/refactored
   - Initializes experiment session and logs startup
   - Currently minimal; agents will extend this flow

2. **Experiment Logging** [src/utils/logger.py](src/utils/logger.py)
   - **Purpose**: Capture every agent decision/output for scientific analysis
   - **Function**: `log_experiment(agent_name, model_used, action, details, status)`
   - **Mandatory fields in `details`**:
     - `input_prompt`: The exact prompt sent to the LLM
     - `output_response`: The full LLM response received
   - **Action types** (use `ActionType` enum):
     - `CODE_ANALYSIS`: Code inspection, bug detection, style review
     - `CODE_GEN`: Generate refactored code, tests, documentation
     - `DEBUG`: Analyze execution errors or runtime issues
     - `FIX`: Apply correctional patches to code
   - **Output**: JSON array to `logs/experiment_data.json` with unique `id` per entry (enables log merging from multiple runs)

3. **Environment Validation** [check_setup.py](check_setup.py)
   - Enforces Python 3.10/3.11 (LangChain compatibility)
   - Verifies `.env` contains `GOOGLE_API_KEY`
   - Creates `logs/` directory
   - Run before development: `python check_setup.py`

4. **Target Code** (`--target_dir`)
   - Legacy/refactoring candidate code passed as argument
   - Agents analyze and process this directory
   - Structure left flexible for different code types (Python, multi-language, etc.)

---

## TP-Specific Workflows

### Initial Setup
```bash
python check_setup.py          # Validate environment
pip install -r requirements.txt
# Create .env with: GOOGLE_API_KEY=<your-key>
```

### Running Experiment
```bash
python main.py --target_dir ./sandbox  # or path to legacy code
```
Produces: `logs/experiment_data.json` with all agent interactions

### Analyzing Results
```python
import json
with open('logs/experiment_data.json') as f:
    experiments = json.load(f)
    for entry in experiments:
        print(f"{entry['agent']} ({entry['model']}): {entry['action']} → {entry['status']}")
```

### Multi-Agent Execution
- Each agent logs separately with distinct `agent_name`
- All logs append to same JSON file (use `id` field to deduplicate if re-running)
- Enables comparison: same code analyzed by different agents/models

---

## Mandatory Logging Pattern

**Every agent interaction MUST follow this pattern:**

```python
from src.utils.logger import log_experiment, ActionType

log_experiment(
    agent_name="CodeAuditor",                    # Identify which agent
    model_used="gemini-1.5-flash",              # Track which LLM variant
    action=ActionType.ANALYSIS,                 # Use enum, not string
    details={
        "input_prompt": "Analyze this Python function for code smells:\n```python\ndef old_func()...```",
        "output_response": "I identified 3 issues: ...",
        # Optional: add custom fields for analysis
        "target_file": "src/legacy.py",
        "issues_found": 3
    },
    status="SUCCESS"  # or "FAILURE" if LLM call failed
)
```

**Why this matters for TP**: Professors will analyze these logs to evaluate agent reasoning patterns and refactoring quality.

---

## Project Conventions

### Directory Structure
```
src/
  utils/          # Shared utilities
    logger.py     # Experiment logging (DO NOT MODIFY)
  agents/         # Add new agent implementations here
    (TODO: create per-agent modules)
logs/
  experiment_data.json  # Committed (do not .gitignore) for grading
```

### Critical Constraints
1. **ActionType enum mandatory**: Pass `ActionType.FIX`, never string `"FIX"` → will error
2. **Prompt/response tracking non-negotiable**: Logger validates presence; missing fields raise `ValueError`
3. **Log file format immutable**: JSON array structure; append-only operations
4. **Python version locked**: 3.10–3.11 only (LangChain requirement)

### Code Quality Baseline
- Use `pylint` (configured in requirements): `pylint src/`
- Write tests with `pytest` (included in stack)
- Keep agent code modular—each agent in separate file

---

## External APIs & Dependencies

| Module | Purpose | Notes |
|--------|---------|-------|
| `langchain` | LLM orchestration primitives | Chains, agents, memory |
| `langchain-google-genai` | Google Generative AI integration | Uses `GOOGLE_API_KEY` |
| `langgraph` | Agent state graphs/workflows | For multi-step reasoning |
| `python-dotenv` | Environment variable loading | Required for API keys |
| `pandas` | Log analysis | Post-experiment data processing |
| `pytest`, `pylint` | QA tools | Testing & linting |

**Single external dependency**: Google Generative AI API key in `.env`

---

## Common Pitfalls

| Issue | Cause | Solution |
|-------|-------|----------|
| `ValueError: input_prompt missing` | Logging without full prompt dict | Always include both `input_prompt` and `output_response` |
| `AttributeError: ActionType` | Using string `"ANALYSIS"` instead of enum | Change to `ActionType.ANALYSIS` |
| `KeyError: GOOGLE_API_KEY` | Missing `.env` file | Run `check_setup.py` and populate `.env` |
| Logs not persisting | Directory permissions or corrupted JSON | Logger auto-creates `logs/`; check file encoding (UTF-8) |
| Duplicate log entries | Re-running same experiment | Use unique `agent_name` or check `id` field to deduplicate |

---

## Adding New Agents

1. Create `src/agents/agent_name.py`
2. Implement function taking `target_dir` and `model_name` as parameters
3. For each refactoring action:
   - Craft LLM prompt (code snippet + question)
   - Call LLM via LangChain
   - Log result with `log_experiment()`
4. Call from [main.py](main.py) or orchestrator script
5. Test with: `python main.py --target_dir ./test_code`

---

## Grading Expectations

This TP is evaluated on:
- **Experiment completeness**: All agent interactions logged with non-empty prompts/responses
- **Code quality**: Refactoring suggestions are meaningful, not superficial
- **Agent diversity**: Different agents/models tested and compared
- **Log integrity**: `logs/experiment_data.json` valid and complete

→ **Focus on logging quality**: Professors read the logs, not just the refactored code.
