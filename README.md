# Agentic CodeCorrect Project

This project is a Python starter for an agent-based code analysis/correction workflow.

## What it does

- Validates local setup with `check_setup.py` (Python version, `.env`, and `logs/` folder).
- Runs an entrypoint (`main.py`) that accepts a target directory and starts an experiment run.
- Logs experiment activity in `logs/experiment_data.json` through `src/utils/logger.py` for later analysis.

In short, it provides a minimal foundation to launch agentic runs and track their actions/results in structured logs.
