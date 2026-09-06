# Agnara Historical Reference Application #004: `agnara-capability-basics`

[![Agnara Version](https://img.shields.io/badge/agnara-0.1.0a3-blue.svg)](https://pypi.org/project/agnara/0.1.0a3/)
[![Python](https://img.shields.io/badge/python-%3E%3D3.14-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-Historical%20%2F%20Frozen-lightgrey.svg)](#historical-status)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)

> **The canonical educational entry point for developers learning the capability-first architecture of Agnara.**
> Demonstrates capability declarations, agentic metadata, compilation immutability, and execution mechanics using **`agnara==0.1.0a3`** on **CPython >= 3.14**.

---

## Historical Status

This repository is **Historical Reference Application #004** in the Agnara reference suite:

| Dimension | Specification |
|---|---|
| **Framework Release** | `agnara==0.1.0a3` (pinned PyPI release) |
| **Python Runtime** | CPython >= 3.14 (free-threaded compatible under PEP 703) |
| **Repository Status** | **Historical / Frozen** |
| **API Scope** | Strictly uses the real public API surface of 0.1.0a3; no unreleased APIs |
| **Educational Focus** | Capability model fundamentals in isolation (no transport or DI distractions) |

For autonomous AI agent operational instructions, see [AGENTS.md](AGENTS.md).

---

## What You Will Learn

Most backend frameworks organize code around **transports**: HTTP routes (`@app.get`), RPC service stubs, or LLM chatbot tools. When you want to expose the same operation over REST, CLI, and an AI agent, you either rewrite logic or introduce complex adapter layers.

**Agnara inverts this model by making the Capability the primary unit of software construction.**

By exploring this reference application, you will learn:
1. **What a Capability is:** An atomic, transport-neutral business operation that exists independently of HTTP, WebSockets, or AI protocols.
2. **Clean Declaration:** How to declare capabilities using `Agnara("<namespace>")` and `@app.capability`.
3. **Decoupled Naming:** How to separate public capability IDs (`catalog.list_products`) from internal Python function names (`query_catalog_items`) to keep client contracts stable during code refactoring.
4. **Agentic Metadata:** How to annotate capabilities with side effects, operational risk, human confirmation requirements, idempotency, and authorization scopes.
5. **Synchronous & Asynchronous Capabilities:** How Agnara treats both sync functions and `async def` coroutines as first-class citizens with identical declaration ergonomics.
6. **Two-Phase Registry Lifecycle:** How `app.compile()` transitions the application from mutable setup to an immutable, thread-safe `FrozenCapabilityRegistry`.
7. **Zero-Overhead Direct Invocation:** Why `@app.capability` returns the underlying Python function completely unwrapped, enabling direct unit testing without framework harnesses.
8. **Observable Error Behaviors:** How Agnara cleanly separates domain business exceptions from framework lifecycle errors.

---

## Quick Start (Under 2 Minutes)

### 1. Prerequisites
- **CPython 3.14+** installed.
- PowerShell, Bash, or Command Prompt.

### 2. Setup Environment
```bash
# Clone the repository
git clone https://github.com/agnara-project/agnara-capability-basics.git
cd agnara-capability-basics

# Create a virtual environment using Python 3.14
py -3.14 -m venv .venv

# Activate the virtual environment
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
# source .venv/bin/activate

# Install exact pinned dependencies and editable project with dev tools
pip install -r requirements.txt
pip install -e ".[dev]"
```

### 3. Run the Interactive Demonstration
```bash
python app.py
```

### 4. Run the Test Suite
```bash
pytest -v
```

---

## The Pedagogical Application: Product Catalog

The reference application implements a compact product catalog in two files:
- **`domain.py`:** 100% pure Python domain models (`Product`, `PriceBreakdown`, `InventoryStatus`), business calculations, and domain exceptions. Zero framework imports.
- **`catalog.py`:** Declares the Agnara application namespace and registers 4 distinct capabilities, each teaching a specific architectural lesson:

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

### 1. Single Entity Lookup (`get_product`)
Demonstrates implicit naming and automatic docstring extraction. When `description` is omitted, Agnara captures the first paragraph of the docstring:

```python
@app.capability(
    scopes=["catalog:read"],
    effects=[StandardEffect.READ],
    risk=Risk.LOW,
    confirmation=Confirmation.NEVER,
    idempotent=True,
)
def get_product(sku: str) -> Product:
    """Retrieve product specifications by its unique SKU identifier.

    Detailed internal notes below the first paragraph are ignored.
    """
    return find_product_by_sku(sku)
```

### 2. Collection Query with Explicit Naming (`list_products`)
Demonstrates decoupling the public capability ID (`catalog.list_products`) from the internal implementation name (`query_catalog_items`):

```python
@app.capability(
    name="list_products",
    description="Filter and retrieve matching products from the catalog.",
    scopes=["catalog:read"],
    effects=[StandardEffect.READ],
    risk=Risk.LOW,
    confirmation=Confirmation.NEVER,
    idempotent=True,
)
def query_catalog_items(
    category: str | None = None,
    max_price: float | None = None,
) -> list[Product]:
    return search_products(category=category, max_price=max_price)
```

### 3. Business Calculation & Structured Output (`calculate_price`)
Capabilities are not limited to CRUD database queries; pure business logic and algorithms are first-class capabilities:

```python
@app.capability(
    description="Calculate full order pricing including volume subtotals, discounts, and taxes.",
    scopes=["catalog:read"],
    effects=[StandardEffect.READ],
    risk=Risk.LOW,
    confirmation=Confirmation.NEVER,
    idempotent=True,
)
def calculate_price(
    sku: str,
    quantity: int,
    discount_code: str | None = None,
) -> PriceBreakdown:
    return compute_pricing(sku=sku, quantity=quantity, discount_code=discount_code)
```

### 4. Asynchronous Non-blocking Capability (`check_warehouse_availability`)
Agnara preserves asynchronous coroutines transparently:

```python
@app.capability(
    description="Asynchronously query real-time warehouse logistics for stock availability.",
    scopes=["inventory:read"],
    effects=[StandardEffect.READ],
    risk=Risk.LOW,
    confirmation=Confirmation.NEVER,
    idempotent=True,
)
async def check_warehouse_availability(sku: str) -> InventoryStatus:
    await asyncio.sleep(0.01)  # Non-blocking I/O simulation
    return lookup_warehouse_inventory(sku)
```

---

## The 6-Stage Demonstration (`app.py`)

Running `python app.py` walks you through each stage of the capability lifecycle:

```text
==============================================================================
  Agnara Historical Reference Application #004: agnara-capability-basics
  Target: agnara==0.1.0a3 | Python: CPython >=3.14 | Status: Historical / Frozen
==============================================================================
Python Version: 3.14.4

==============================================================================
  1. DECLARATION & METADATA (Pre-Compilation State)
==============================================================================
Application Name (Namespace): 'catalog'
Is Compiled? False
Number of registered capabilities: 4

Registered Capabilities:
  - ID:           catalog.get_product
    Description:  Retrieve product specifications by its unique SKU identifier.
    Risk:         low
    Effects:      ['read']
    Scopes:       ['catalog:read']
    Idempotency:  yes

  - ID:           catalog.list_products
    Description:  Filter and retrieve matching products from the catalog.
    Risk:         low
    Effects:      ['read']
    Scopes:       ['catalog:read']
    Idempotency:  yes

  - ID:           catalog.calculate_price
    Description:  Calculate full order pricing including volume subtotals, discounts, and taxes.
    Risk:         low
    Effects:      ['read']
    Scopes:       ['catalog:read']
    Idempotency:  yes

  - ID:           catalog.check_warehouse_availability
    Description:  Asynchronously query real-time warehouse logistics for stock availability.
    Risk:         low
    Effects:      ['read']
    Scopes:       ['inventory:read']
    Idempotency:  yes

==============================================================================
  2. DIRECT INVOCATION (Zero Decorator Distortion)
==============================================================================
In Agnara, '@app.capability' records the declaration but returns the function
completely unwrapped and unchanged. Capabilities remain plain Python callables
that can be called directly by unit tests without framework setup.

>> Calling catalog.get_product('KB-900') directly:
   Result: Mechanical Keyboard Pro (SKU: KB-900) - Price: $129.99

>> Calling catalog.calculate_price('LP-100', quantity=2, discount_code='SUMMER20') directly:
   Subtotal:  $2998.00
   Discount: -$599.60 (SUMMER20)
   Tax (19%): +$455.70
   Total:     $2854.10

==============================================================================
  3 & 4. COMPILATION & REGISTRY QUERYING
==============================================================================
Calling 'app.compile()' freezes registration (ADR 0005) and yields an immutable,
thread-safe FrozenCapabilityRegistry with deterministic ordering.

Is Compiled now? True
Registry Type:   FrozenCapabilityRegistry
Total Entries:   4

>> Querying registry with namespace filter (.in_namespace('catalog')):
   Found 4 capabilities in namespace 'catalog'

>> Querying registry with effect filter (.with_effect(StandardEffect.READ)):
   Found 4 capabilities with effect 'read':
   * catalog.get_product
   * catalog.list_products
   * catalog.calculate_price
   * catalog.check_warehouse_availability

>> Invoking capability handler through registry lookup:
   Filtered peripherals <= $100 via catalog.list_products:
   - Ergonomic Wireless Mouse ($59.99)

==============================================================================
  5. ASYNCHRONOUS CAPABILITY EXECUTION
==============================================================================
Agnara treats asynchronous handlers as first-class citizens.
Async capabilities are ordinary coroutines executed with standard asyncio.

>> Executing async capability: catalog.check_warehouse_availability
   Direct Call Result: Available=True in 'central-hub-eu' (Stock: 45)
   Registry Call Result (CA-010): Available=False in 'central-hub-eu' (Stock: 0)

==============================================================================
  6. OBSERVABLE ERROR BEHAVIORS
==============================================================================
Agnara separates domain exceptions from framework lifecycle errors.

>> 1. Domain Error: ProductNotFoundError
   CAUGHT EXPECTED: ProductNotFoundError: Product with SKU 'NON-EXISTENT-SKU' not found in catalog

>> 2. Domain Error: InvalidQuantityError
   CAUGHT EXPECTED: InvalidQuantityError: Quantity must be a positive integer, got: 0

>> 3. Domain Error: InvalidDiscountError
   CAUGHT EXPECTED: InvalidDiscountError: Invalid or unrecognized discount code: 'INVALID_PROMO'

>> 4. Registry Error: UnknownCapabilityError
   CAUGHT EXPECTED: UnknownCapabilityError: no capability registered as 'catalog.non_existent_capability'

>> 5. Lifecycle Error: RegistryFrozenError
   CAUGHT EXPECTED: RegistryFrozenError: cannot register catalog.late_addition after the registry was frozen; registration belongs to startup compilation (ADR 0005)

>> 6. Definition Error: DuplicateCapabilityError
   CAUGHT EXPECTED: DuplicateCapabilityError: capability isolated.entry is already registered; ids must be unique because policies, audit records and agent manifests reference them

>> 7. Definition Error: DefinitionError (Malformed Name)
   CAUGHT EXPECTED: DefinitionError: invalid capability name in 'isolated.invalid-dashed-name': 'invalid-dashed-name' is not a valid Python identifier

==============================================================================
  DEMONSTRATION COMPLETED SUCCESSFULLY
==============================================================================
```

---

## Architectural Foundations

### 1. Two-Phase Registry Lifecycle (ADR 0005)
Agnara strictly separates the **authoring phase** from the **execution phase**:
- **Authoring (`CapabilityRegistry`):** Mutable collection where `@app.capability` records definitions during startup.
- **Freeze Step (`app.compile()`):** Closes registration, returning a `FrozenCapabilityRegistry`. Under free-threaded CPython 3.14 (PEP 703), the frozen registry provides lock-free read operations across multiple threads with guaranteed deterministic iteration order. Subsequent registration attempts raise `RegistryFrozenError`.

### 2. The Unwrapped Callable Guarantee
In traditional frameworks, decorators wrap functions in closures or proxies, complicating unit testing and adding overhead. In Agnara, `@app.capability` records the declaration in the registry and returns the function **completely unwrapped**:
```python
# You can test your function directly without any Agnara harness:
product = get_product("KB-900")
assert product.sku == "KB-900"
```

### 3. Agentic Metadata Ontology
Agnara provides standardized vocabularies describing what an operation *does*:
- **`StandardEffect`:** `READ`, `CACHE_WRITE`, `DATABASE_WRITE`, `EXTERNAL_WRITE`, `FINANCIAL_WRITE`, `DESTRUCTIVE`.
- **`Risk`:** `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
- **`Confirmation`:** `NEVER` (fully autonomous), `POLICY` (context-dependent), `REQUIRED` (always human-approved).
- **`Idempotency`:** `YES` (safe to retry), `NO` (retries produce extra side effects), `UNKNOWN` (default honest tri-state).
- **`scopes`:** Logical authorization labels (e.g. `catalog:read`, `inventory:read`).

---

## Git & Development Workflow

The repository follows a clean, professional GitFlow structure:
- **`main`:** Contains strictly the historical, stable release baseline (`v0.1.0`). Direct commits are forbidden.
- **`develop`:** Active development branch where changes, verification runs, and tests are validated.
- **Pull Requests:** All feature or fix work targets `develop`. Milestone releases are promoted from `develop` into `main` via validated PRs.

---

## Real Limitations of `agnara==0.1.0a3`

To maintain historical accuracy, this reference application respects the real boundaries of the 0.1.0a3 release:
1. **Core Kernel Only:** In `0.1.0a3`, Agnara is an execution kernel. Transport adapters (HTTP, REST, MCP server tools, CLI commands) are external projections and not part of the core package.
2. **Authoring Surface Scope:** In `0.1.0a3`, `@app.capability` accepts metadata, but does not take policy rules or DI providers directly. Dependency injection is authored through `DIRegistry` (see Reference App #002) and policies via `ScopePolicy` (see Reference App #003).
3. **No Coercion on Direct Calls:** Invoking capability functions directly relies on standard Python argument binding without transport-level string coercion.

---

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).