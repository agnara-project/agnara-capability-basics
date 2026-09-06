# Agnara Historical Reference Application #004: `agnara-capability-basics`

[![Agnara Version](https://img.shields.io/badge/agnara-0.1.0a3-blue.svg)](https://pypi.org/project/agnara/0.1.0a3/)
[![Python](https://img.shields.io/badge/python-%3E%3D3.14-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-Historical%20%2F%20Frozen-lightgrey.svg)](#frozen-status)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)

> **The canonical educational entry point for developers learning the capability-first architecture of Agnara.**
> Demonstrates capability declarations, agentic metadata, compilation immutability, and execution mechanics using **`agnara==0.1.0a3`** on **CPython >= 3.14**.

---

## 1. What is this Project?

`agnara-capability-basics` is a compact, production-grade pedagogical application demonstrating the core capability-first model of Agnara in isolation.

In traditional software development, business operations are tightly bound to specific communication protocols: an endpoint is an HTTP route, an RPC procedure, or a chatbot tool callback. When transports evolve, developers are forced to rewrite handlers or maintain complex adapter shims.

**In Agnara, a Capability is an atomic, transport-neutral business operation.** It represents pure domain intent, decoupled from HTTP, WebSockets, or AI wire formats.

---

## 2. What You Will Learn

By exploring this repository, you will understand:
1. **The Capability-First Model:** Why capabilities represent business operations, not endpoints or protocol bindings.
2. **Real Declaration Ergonomics:** How to declare capabilities using `Agnara("<namespace>")` and `@app.capability` in `0.1.0a3`.
3. **Decoupled Identity:** How to separate public capability IDs (`catalog.list_products`) from internal Python function names (`query_catalog_items`) to keep client manifests stable during refactors.
4. **Agentic Metadata Vocabularies:** How to declare side effects (`StandardEffect`), operational risk (`Risk`), human confirmation requirements (`Confirmation`), idempotency (`Idempotency`), and authorization scopes.
5. **Synchronous and Asynchronous Handlers:** How Agnara treats both synchronous callables and `async def` coroutines as first-class capabilities with identical declaration ergonomics.
6. **Two-Phase Registry Lifecycle:** How `app.compile()` freezes registration (ADR 0005) into an immutable, thread-safe `FrozenCapabilityRegistry`.
7. **Zero Decorator Distortion:** Why `@app.capability` returns the underlying function completely unwrapped, enabling native Python direct testing without framework harnesses.
8. **Observable Error Behaviors:** How domain business exceptions and framework lifecycle errors are cleanly distinguished.

---

## 3. Historical Baseline & Version Pinning

| Dimension | Specification |
|---|---|
| **Framework Version** | Strictly pinned to **`agnara==0.1.0a3`** |
| **Python Runtime** | **CPython >= 3.14** (designed for lock-free free-threaded execution under PEP 703) |
| **Repository Status** | **Historical / Frozen** |
| **Public API Scope** | Uses exclusively real public exports available in `0.1.0a3`; no speculative or post-a3 APIs |

---

## 4. Prerequisites

- **Python:** CPython >= 3.14 (Free-threaded build or standard build).
- **Shell:** PowerShell, Bash, or Zsh.
- **Git:** Standard Git installation.

---

## 5. Quick Start (Under 2 Minutes)

```bash
# 1. Clone the repository
git clone https://github.com/agnara-project/agnara-capability-basics.git
cd agnara-capability-basics

# 2. Create virtual environment with Python 3.14
py -3.14 -m venv .venv

# 3. Activate the virtual environment
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
# source .venv/bin/activate

# 4. Install exact pinned dependencies and editable project with dev tools
pip install -r requirements.txt
pip install -e ".[dev]"

# 5. Run the interactive demonstration
python app.py

# 6. Run the comprehensive test suite
pytest -v
```

---

## 6. The Pedagogical Application

The application implements a compact product catalog across two modules:
- **`domain.py`:** Pure Python standard library. Zero framework imports. Contains `Product`, `PriceBreakdown`, and `InventoryStatus` dataclasses, catalog seed data, and domain calculations.
- **`catalog.py`:** Initializes `Agnara("catalog")` and declares 4 reference capabilities:

```
┌─────────────────────────────────────────────────────────────┐
│                    Agnara("catalog")                        │
├─────────────────────────────────────────────────────────────┤
│  1. get_product(sku) -> Product                             │
│     * Single entity query                                   │
│     * Docstring summary fallback for description            │
│     * StandardEffect.READ | Risk.LOW | idempotent=True      │
├─────────────────────────────────────────────────────────────┤
│  2. list_products(category, max_price) -> list[Product]     │
│     * Collection filtering with optional criteria           │
│     * Explicit naming override: name="list_products"        │
│     * Decoupled from internal function: query_catalog_items │
├─────────────────────────────────────────────────────────────┤
│  3. calculate_price(sku, qty, discount) -> PriceBreakdown   │
│     * Multi-parameter domain calculation                    │
│     * Business rule validations (qty > 0, discount check)   │
│     * Compound structured return type                       │
├─────────────────────────────────────────────────────────────┤
│  4. check_warehouse_availability(sku) -> InventoryStatus   │
│     * Asynchronous execution (async def)                    │
│     * Non-blocking warehouse logistics simulation           │
│     * Unwrapped native coroutine semantics                  │
└─────────────────────────────────────────────────────────────┘
```

### Executing the Demonstration (`python app.py`)

Running `python app.py` executes the 6-stage capability lifecycle:
1. **Declaration & Metadata:** Inspects pre-compilation application state (`app.is_compiled == False`) and lists declared metadata.
2. **Direct Invocation:** Calls `get_product("KB-900")` and `calculate_price("LP-100", 2)` directly as raw Python functions with zero wrapper overhead.
3. **Compilation:** Calls `app.compile()` to freeze registration into a `FrozenCapabilityRegistry` (`app.is_compiled == True`).
4. **Registry Querying:** Filters capabilities by namespace (`in_namespace("catalog")`) and effect (`with_effect(StandardEffect.READ)`), and executes handlers via registry lookup.
5. **Asynchronous Execution:** Runs `check_warehouse_availability` asynchronously with `asyncio.run()`.
6. **Observable Error Behaviors:** Demonstrates expected exceptions (`ProductNotFoundError`, `InvalidQuantityError`, `UnknownCapabilityError`, `RegistryFrozenError`, `DuplicateCapabilityError`, `DefinitionError`).

---

## 7. Key Agnara Concepts Demonstrated

### Capability vs Transport
Agnara Core owns the semantics shared by every transport: capabilities, metadata, the registry, and errors. Transports (REST HTTP, MCP, CLI) are external projections that point to capabilities.

### Two-Phase Registry Lifecycle (ADR 0005)
Registration occurs strictly during startup. Calling `app.compile()` freezes the registry, returning a `FrozenCapabilityRegistry`. Subsequent registration attempts raise `RegistryFrozenError`. Under free-threaded CPython 3.14, the frozen registry provides lock-free concurrency.

### Zero-Overhead Direct Invocation
`@app.capability` records declarations as a side effect and returns the callable completely unaltered. Handlers can be tested directly with standard assertions without framework harnesses.

---

## 8. Project Structure

```
agnara-capability-basics/
├── AGENTS.md                   # Operational manual for AI agents
├── README.md                   # Progressive learning guide for human developers
├── ARCHITECTURE.md             # In-depth architectural design and ADR references
├── CONTRIBUTING.md             # GitFlow and contribution guidelines
├── SECURITY.md                 # Security disclosure policy
├── CHANGELOG.md                # Release ledger
├── LICENSE                     # Apache 2.0
├── pyproject.toml              # Packaging and dev dependencies
├── requirements.txt            # Exact pinned core dependency (agnara==0.1.0a3)
├── domain.py                   # Pure Python domain logic and dataclasses
├── catalog.py                  # Agnara("catalog") setup and capability declarations
├── app.py                      # Pedagogical 6-stage demonstration script
├── docs/
│   ├── capability-lifecycle.md # State machine and compilation lifecycle
│   └── public-api-boundary.md  # Permitted exports and prohibited anti-patterns
└── tests/
    ├── test_capabilities.py    # Handler execution, domain rules, async behavior
    ├── test_metadata_and_registry.py # Identity, metadata, registry query methods
    └── test_lifecycle_and_errors.py  # Compile freeze, duplicates, invalid definitions
```

---

## 9. Testing & Quality Assurance

Run the test suite:
```powershell
pytest -v
```

Check code formatting and linting:
```powershell
ruff check .
ruff format --check .
```

Verify package build:
```powershell
pip wheel . --no-deps -w dist
Remove-Item -Recurse -Force dist
```

---

## 10. Relation to Historical Reference Applications

This repository belongs to the Agnara Historical Reference Application series:

| App # | Designation | Pinned Release | Pedagogical Focus |
|---|---|---|---|
| **#001** | `agnara-task-intelligence` | `agnara==0.1.0a2` | Task lifecycle, step execution, & orchestration |
| **#002** | `agnara-dependency-intelligence` | `agnara==0.1.0a2` | Dependency injection & graph resolution |
| **#003** | `agnara-secure-operations` | `agnara==0.1.0a2` | Execution governance, policies, & confirmation |
| **#004** | **`agnara-capability-basics`** | **`agnara==0.1.0a3`** | **Capability-first authoring, metadata, & compilation** |

---

## 11. Frozen Status

This repository is **Historical / Frozen**. It serves as an immutable pedagogical baseline for `agnara==0.1.0a3`. It does not accept upgrades to newer Agnara releases or unreleased development branches.

---

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).