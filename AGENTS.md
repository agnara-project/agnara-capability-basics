# AGENTS.md — Operational Manual for Autonomous AI Agents

> **Audience:** Claude Code, OpenAI Codex, Antigravity, and other autonomous AI coding agents inspecting, maintaining, or extending this codebase.
> **Role:** Single source of operational truth for machine agents. For human-oriented documentation, see `README.md`.

---

## 1. Project Identity & Historical Context

- **Repository:** `agnara-project/agnara-capability-basics`
- **Designation:** **Agnara Historical Reference Application #004**
- **Framework Version:** Strictly pinned to **`agnara==0.1.0a3`**
- **Python Version:** **CPython >= 3.14** (designed for free-threaded compatibility under PEP 703)
- **Status:** **Historical / Frozen**
- **Mission:** Serve as the official pedagogical entry point for developers learning the capability-first architecture of Agnara in isolation, without external transport or infrastructure distractions.

---

## 2. Inviolable Architectural Constraints

1. **Do Not Upgrade Agnara:** Under no circumstances should `pyproject.toml` or `requirements.txt` be altered to reference versions later than `0.1.0a3` or unreleased development branches (`main`/`develop`).
2. **Do Not Invent Speculative APIs:** Only use the actual public API surface present in `agnara==0.1.0a3`. Do not extrapolate future features.
3. **No External Infrastructure:** Do not introduce web frameworks (FastAPI, Flask, Starlette), database ORMs/drivers, HTTP clients, or LLM SDKs. All data must remain pure in-memory Python domain structures.
4. **Preserve CPython 3.14+ Compatibility:** Maintain strict compatibility with modern Python 3.14+ idioms, including free-threaded execution semantics (lock-free reads on frozen objects).
5. **No Synthetic Function Wrappers:** `@app.capability` must return the original callable unaltered. Never insert interceptors, closures, or wrapper proxies around handlers.

---

## 3. Codebase Structure & Ownership

```
agnara-capability-basics/
├── AGENTS.md                   # Operational instructions for AI agents (this file)
├── README.md                   # Progressive learning guide for human developers
├── CHANGELOG.md                # Historical release ledger
├── LICENSE                     # Apache 2.0 License
├── pyproject.toml              # Hatchling build configuration & optional dev dependencies
├── requirements.txt            # Exact pinned core dependency (agnara==0.1.0a3)
├── domain.py                   # Pure business logic, dataclasses, domain exceptions, seed data
├── catalog.py                  # Agnara("catalog") setup, capability declarations, metadata
├── app.py                      # Pedagogical CLI runner executing the 6 capability stages
└── tests/
    ├── test_capabilities.py    # Unit tests for capability handlers and business calculations
    ├── test_metadata_and_registry.py # Tests for capability identity, metadata, and registry queries
    └── test_lifecycle_and_errors.py  # Tests for compilation freeze, idempotency, and error cases
```

### Module Responsibilities:
- **`domain.py`:** 100% pure Python standard library. **Zero imports from `agnara`**. Contains `Product`, `PriceBreakdown`, `InventoryStatus`, domain exceptions (`ProductNotFoundError`, etc.), and pricing logic.
- **`catalog.py`:** Owns `Agnara("catalog")` and registers the 4 core capabilities (`get_product`, `list_products`, `calculate_price`, `check_warehouse_availability`).
- **`app.py`:** Executable demonstration that walks through the 6 stages of the capability lifecycle with console telemetry.
- **`tests/`:** Standard `pytest` test suite verifying both direct callable invocation and `FrozenCapabilityRegistry` lookups.

---

## 4. Reproducible Command Palette

Agents performing modifications, health checks, or code reviews must run commands using the local virtual environment:

```powershell
# 1. Clean Environment Initialization
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Dependency Installation
pip install -r requirements.txt
pip install -e ".[dev]"

# 3. Interactive CLI Demonstration
python app.py

# 4. Comprehensive Test Suite
pytest -v

# 5. Code Style & Formatting Verification
ruff check .
ruff format --check .

# 6. Optional Code Auto-formatting
ruff format .

# 7. Package Build Verification
pip wheel . --no-deps -w dist
Remove-Item -Recurse -Force dist
```

All verification commands (`pytest`, `ruff check`, `ruff format --check`, `python app.py`) must exit with return code `0`.

---

## 5. Public API Surface in `agnara==0.1.0a3`

When reading or authoring code, use only these verified public exports:

| Symbol | Module / Origin | Verified Usage |
|---|---|---|
| `Agnara(name: str)` | `agnara.application` | Root application instance. `name` must be a valid Python identifier. |
| `@app.capability(...)` | `agnara.application` | Decorator recording declarations. Returns original callable untouched. |
| `app.compile()` | `agnara.application` | Freezes registration; returns `FrozenCapabilityRegistry`. Sets `is_compiled=True`. |
| `CapabilityId` | `agnara.capability.identity` | Qualified identifier (`namespace.name`). Immutable dataclass. |
| `CapabilityDefinition` | `agnara.capability.definition` | Immutable declaration record with `.has_effect()` and `.requires_scope()`. |
| `FrozenCapabilityRegistry` | `agnara.capability.registry` | Read-only `Mapping` supporting `.in_namespace(str)` and `.with_effect(effect)`. |
| `StandardEffect` | `agnara.capability.metadata` | Enum: `READ`, `CACHE_WRITE`, `DATABASE_WRITE`, `EXTERNAL_WRITE`, `FINANCIAL_WRITE`, `DESTRUCTIVE`. |
| `Risk` | `agnara.capability.metadata` | Enum: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`. |
| `Confirmation` | `agnara.capability.metadata` | Enum: `NEVER`, `POLICY`, `REQUIRED`. |
| `Idempotency` | `agnara.capability.metadata` | Enum: `YES`, `NO`, `UNKNOWN` (mapped from `idempotent=True/False/None`). |
| `agnara.errors` | `agnara.errors` | `AgnaraError`, `DefinitionError`, `DuplicateCapabilityError`, `RegistryFrozenError`, `UnknownCapabilityError`. |

---

## 6. Negative Constraints: APIs That Must NOT Be Invented

To preserve historical accuracy, agents must avoid the following anti-patterns:
- **No `policies` parameter on `@app.capability(...)`:** In `0.1.0a3`, the `@app.capability` authoring decorator does **not** accept a `policies` argument. Policies are evaluated in execution pipelines (see Reference App #003).
- **No transport routing decorators:** Do not invent `@app.route`, `@app.endpoint`, or `@app.tool`. Agnara Core is transport-agnostic (ADR 0002).
- **No DI container injection on direct calls:** Direct calls (`get_product(...)`) are raw Python calls without runtime DI resolution. DI resolution occurs via `ExecutionContext` in runtime pipelines (see Reference App #002).
- **No synthetic wrappers around handlers:** Do not wrap handlers in runtime interceptors.

---

## 7. GitFlow Protocol for AI Agents

The repository follows a simplified, professional GitFlow model:

```
[develop] ────●────●────●────● (Validated changes & PR staging)
                            │
                            │ Pull Request (Review & Validation)
                            ▼
[main] ─────────────────────● (Historical / Frozen release baseline)
```

1. **`main` Branch:**
   - Represents the frozen, production-grade historical state.
   - Direct commits to `main` are prohibited.
   - Only merges from `develop` via pull requests are permitted for milestone closures.
2. **`develop` Branch:**
   - Active branch for agent tasks, testing, and structural validation.
   - All feature or bugfix work originates from and merges back into `develop`.
3. **Commit Standards:**
   - Use Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`).
4. **Pull Requests:**
   - Target is `develop` for daily work.
   - Final release PR targets `main` from `develop`.

---

## 8. Definition of Done (DoD) for AI Agents

An agent task is complete only when all criteria are satisfied:
1. `pytest -v` exits with code `0` (all 25 tests pass).
2. `ruff check .` exits with code `0` (zero linting errors).
3. `ruff format --check .` exits with code `0` (all code properly formatted).
4. `python app.py` runs end-to-end and exits with code `0`.
5. `pip wheel . --no-deps` builds successfully without warnings.
6. `git status` is completely clean: no untracked files, no temporary build artifacts (`dist/`, `.pytest_cache/`, `__pycache__/`).
7. Dependencies remain strictly pinned to `agnara==0.1.0a3`.
8. Documentation and technical contracts match the implemented behavior exactly.