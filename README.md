# Agentic-codecorrect-project

Minimal Python project for running an agent-style startup flow, validating local setup, and logging experiment events.

## Features

- CLI entry point (`main.py`) with a required target directory argument
- Environment sanity check script (`check_setup.py`)
- Structured JSON logging utility (`src/utils/logger.py`)
- Example environment file (`.env.example`)

## Prerequisites

- Python 3.10 or 3.11 (recommended by project setup check)
- `pip`

## Installation

```bash
python -m venv .venv
```

Activate the environment:

**Linux/macOS**

```bash
source .venv/bin/activate
```

**Windows (CMD)**

```bat
.venv\Scripts\activate
```

**Windows (PowerShell)**

```powershell
.venv\Scripts\Activate.ps1
```

Then install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file from the example:

   ```bash
   cp .env.example .env
   ```

2. Add your API key in `.env`:

   ```env
   GOOGLE_API_KEY="your_key_here"
   ```

## Usage

### 1) Run setup check

```bash
python check_setup.py
```

This verifies Python version, `.env` presence, and `logs/` directory readiness.

### 2) Run main script

```bash
python main.py --target_dir /absolute/path/to/target
```

Expected behavior:

- Validates that `--target_dir` exists
- Prints startup/completion messages
- Attempts to log an experiment entry

## Project Structure

```text
.
├── .env.example
├── check_setup.py
├── main.py
├── requirements.txt
├── logs/
└── src/
    └── utils/
        └── logger.py
```

## Development Notes

- Tests: `python -m pytest` (currently no tests discovered)
- Lint: `python -m pylint main.py src`
