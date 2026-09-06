# AGENTS.md — Guidance for Autonomous AI Agents

This document provides context and behavioral guidance for AI coding agents inspecting, reviewing, or testing **Agnara Historical Reference Application #004 (`agnara-capability-basics`)**.

---

## 1. Repository Status: Historical & Frozen

This repository is a **Historical Reference Application** pinned to **`agnara==0.1.0a3`** and **CPython >= 3.14**.

### Inviolable Constraints for Agents:
1. **Do Not Upgrade Agnara:** Do not modify `pyproject.toml` or `requirements.txt` to use versions later than `0.1.0a3`.
2. **Do Not Introduce Speculative APIs:** Only use APIs present in the installed `agnara==0.1.0a3` distribution.
3. **No External Infrastructure:** Do not add HTTP servers (FastAPI, Starlette, Flask), database drivers, or LLM SDKs to this repository. This reference app exists solely to teach the core capability model in isolation.
4. **Preserve Python 3.14+ Compatibility:** Code must remain strictly compatible with CPython 3.14, including free-threaded semantics.

---

## 2. Quick Verification Commands

Agents performing health checks or code reviews should execute:

```powershell
# 1. Run the test suite
pytest -v

# 2. Check code style and formatting
ruff check .
ruff format --check .

# 3. Run the demonstration
python app.py
```

All commands must exit with code `0`.

---

## 3. Code Organization & Architecture Rules

- **`domain.py`:** Must remain 100% pure Python. No imports from `agnara`. Contains only domain entities, domain exceptions, seed data, and core business algorithms.
- **`catalog.py`:** Owns the `Agnara("catalog")` instance and capability declarations. Must use `@app.capability` with accurate agentic metadata.
- **`app.py`:** The primary pedagogical CLI script. Demonstrates the six learning stages.
- **`tests/`:** Standard `pytest` test cases. Tests both direct callable invocation and `FrozenCapabilityRegistry` lookups.

---

## 4. Key Public APIs in `agnara==0.1.0a3`

When reading or modifying code, remember:
- `Agnara(name: str)`: Namespace root. `name` must be a valid Python identifier.
- `@app.capability`: Decorator for registering capabilities. Returns original function unchanged.
- `app.compile()`: Returns `FrozenCapabilityRegistry`. Freezes registration.
- `FrozenCapabilityRegistry`: Implements `collections.abc.Mapping`. Supports `.in_namespace(str)` and `.with_effect(effect)`.
- `agnara.errors`: `AgnaraError`, `DefinitionError`, `DuplicateCapabilityError`, `RegistryFrozenError`, `UnknownCapabilityError`.