# Contributing to `agnara-capability-basics`

Thank you for your interest in the Agnara Historical Reference Applications!

## Historical Reference Notice

`agnara-capability-basics` is **Historical Reference Application #004**, designed specifically to capture and teach the capability-first architecture of **`agnara==0.1.0a3`** under **CPython >= 3.14**.

Because of this pedagogical and historical role:
- **This repository is Frozen.**
- We do **not** accept PRs updating the core dependency to newer Agnara versions (e.g. `0.2.0` or `main`).
- We do **not** accept additions that introduce external transports (HTTP, MCP, CLI servers) or heavy third-party dependencies, as doing so would dilute the educational focus on the core capability model.

## What Contributions Are Accepted?

1. **Clarifications to documentation:** If an explanation in `README.md` or `ARCHITECTURE.md` is unclear or contains typos.
2. **Pedagogical bug fixes:** If an existing example behaves inconsistently with `agnara==0.1.0a3` specifications.
3. **Additional unit tests:** Expanding test coverage for existing capability behaviors without altering runtime semantics.

## Development Workflow

1. Fork and clone the repository.
2. Ensure you have CPython 3.14+ installed.
3. Create a virtual environment and install development dependencies:
   ```powershell
   py -3.14 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```
4. Run validation checks before submitting a PR:
   ```powershell
   ruff check .
   ruff format --check .
   pytest -v
   python app.py
   ```