# Agnara Historical Reference Application #004: `agnara-capability-basics`

[![Agnara Version](https://img.shields.io/badge/agnara-0.1.0a3-blue.svg)](https://pypi.org/project/agnara/0.1.0a3/)
[![Python](https://img.shields.io/badge/python-%3E%3D3.14-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-Historical%20%2F%20Frozen-lightgrey.svg)](#historical-status)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)

> **Official educational entry point for developers learning the capability-first architecture of Agnara.**
> Demonstrates the core capability authoring surface, agentic metadata, immutability guarantees, and execution model using **`agnara==0.1.0a3`** on **CPython >= 3.14**.

---

## Historical Status

This repository is **Historical Reference Application #004** in the Agnara reference suite:

| Dimension | Specification |
|---|---|
| **Release Target** | `agnara==0.1.0a3` (published release) |
| **Python Runtime** | CPython >= 3.14 (free-threaded compatible design) |
| **Repository Status** | **Historical / Frozen** |
| **API Boundary** | Uses strictly the public API surface of 0.1.0a3; no unreleased APIs from `main` |
| **Mission** | Provide the canonical beginner tutorial for Agnara's capability-first model |

---

## What is a Capability?

In traditional frameworks, business logic is tightly bound to infrastructure: an endpoint is an HTTP route, an RPC procedure, or a chatbot tool callback. When transports change, developers are forced to rewrite handlers or add complex adapter shims.

**In Agnara, a Capability is an atomic, transport-neutral business operation.**

- **A capability is not a route:** It does not know whether it is exposed over REST, GraphQL, gRPC, MCP, or a background queue.
- **A capability is not an LLM tool:** It is an intrinsic domain operation that agentic systems can discover and invoke via metadata.
- **A capability is an ordinary Python callable:** The `@app.capability` decorator records declarations into an application registry without wrapping, modifying, or altering function call behaviour.

```
┌─────────────────────────────────────────────────────────────┐
│                     Transport Layer                         │
│       HTTP REST   │   MCP Tool   │   CLI   │   A2A / RPC    │
└──────────────────────────────┬──────────────────────────────┘
                               │ (projects / exposes)
┌──────────────────────────────▼──────────────────────────────┐
│                    Agnara Capability                        │
│   catalog.get_product, catalog.calculate_price, etc.        │
│   - Pure business logic & domain validations                │
│   - Metadata: effects, risk, scopes, idempotency            │
└──────────────────────────────┬──────────────────────────────┘
                               │ (pure execution)
┌──────────────────────────────▼──────────────────────────────┐
│                      Domain Entities                        │
│         Product, PriceBreakdown, InventoryStatus            │
└─────────────────────────────────────────────────────────────┘
```

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

# Install exact dependencies
pip install -r requirements.txt
pip install -e ".[dev]"
```

### 3. Run the Demonstration
```bash
python app.py
```

### 4. Run the Tests
```bash
pytest -v
```

---

## Core Concepts Taught

### 1. Declaration with Real 0.1.0a3 API
Capabilities are declared by instantiating `Agnara("<namespace>")` and using the `@app.capability` decorator:

```python
from agnara import Agnara, Risk, StandardEffect, Confirmation

app = Agnara("catalog")


@app.capability(
    scopes=["catalog:read"],
    effects=[StandardEffect.READ],
    risk=Risk.LOW,
    confirmation=Confirmation.NEVER,
    idempotent=True,
)
def get_product(sku: str) -> Product:
    """Retrieve product specifications by its unique SKU identifier."""
    return find_product_by_sku(sku)
```

### 2. Naming Decoupling (`name=...`)
Agnara decouples the public, stable capability ID from the internal Python function name. This protects client manifests, audit logs, and security policies from breaking when internal code is refactored:

```python
@app.capability(name="list_products")
def query_catalog_items(...) -> list[Product]:
    ...
```
- **Capability ID:** `catalog.list_products`
- **Internal Python Callable:** `query_catalog_items`

### 3. Agentic Metadata Vocabularies
Agnara metadata describes what invoking a capability *does* in a structured format readable by policy engines and agent discovery surfaces:

| Metadata Field | Type / Enum | Description | Real 0.1.0a3 Value in Demo |
|---|---|---|---|
| `name` | `str | None` | Overrides the logical capability name segment | `"list_products"` |
| `description` | `str | None` | Explains capability purpose (defaults to docstring summary) | Extracted or explicit |
| `effects` | `Iterable[str \| StandardEffect]` | Declares side-effects (`read`, `database-write`, `destructive`, etc.) | `StandardEffect.READ` |
| `risk` | `Risk \| str` | Operational damage potential (`low`, `medium`, `high`, `critical`) | `Risk.LOW` |
| `confirmation` | `Confirmation \| str` | Human approval requirements (`never`, `policy`, `required`) | `Confirmation.NEVER` |
| `idempotency` | `bool \| None` -> `Idempotency` | Safe retry indicator (`yes`, `no`, `unknown`) | `idempotent=True` -> `Idempotency.YES` |
| `scopes` | `Iterable[str]` | Required logical authorization scopes | `("catalog:read",)` |

### 4. Zero-Overhead Direct Invocation
The `@app.capability` decorator returns the underlying callable untouched:
```python
# No mocks, no DI container, no test client needed:
product = get_product("KB-900")
assert product.name == "Mechanical Keyboard Pro"
```

### 5. Asynchronous Capabilities
Agnara handles synchronous and asynchronous operations identically:
```python
@app.capability(
    description="Asynchronously query real-time warehouse logistics.",
    scopes=["inventory:read"],
    effects=[StandardEffect.READ],
)
async def check_warehouse_availability(sku: str) -> InventoryStatus:
    await asyncio.sleep(0.01)
    return lookup_warehouse_inventory(sku)
```

### 6. Compilation & Immutability (`app.compile()`)
Calling `app.compile()` transitions the application from authoring to compiled mode:
1. Freezes the internal registry into a `FrozenCapabilityRegistry`.
2. Closes registration (`app.is_compiled == True`). Any subsequent `@app.capability` raises `RegistryFrozenError`.
3. Guarantees deterministic iteration order and lock-free thread safety under free-threaded CPython 3.14.

```python
registry = app.compile()

# Access via logical ID
cap = registry["catalog.get_product"]
result = cap.handler("KB-900")

# Query by effect or namespace
read_only_caps = list(registry.with_effect(StandardEffect.READ))
catalog_caps = list(registry.in_namespace("catalog"))
```

### 7. Observable Error Behavior
Agnara cleanly differentiates domain failures from framework lifecycle errors:

| Exception Class | Origin | Trigger Condition |
|---|---|---|
| `ProductNotFoundError` | Domain | Requesting a SKU that does not exist |
| `InvalidQuantityError` | Domain | Passing zero or negative quantity for pricing |
| `InvalidDiscountError` | Domain | Supplying an unrecognized promo code |
| `UnknownCapabilityError` | Agnara Registry | Looking up unregistered capability key in `FrozenCapabilityRegistry` |
| `RegistryFrozenError` | Agnara Lifecycle | Attempting to register `@app.capability` after `app.compile()` |
| `DuplicateCapabilityError` | Agnara Definition | Registering two capabilities with the same logical ID |
| `DefinitionError` | Agnara Definition | Invalid namespace/name identifier, non-callable handler, invalid metadata |

---

## Repository Structure

```
agnara-capability-basics/
├── pyproject.toml              # Build configuration, CPython >=3.14, agnara==0.1.0a3
├── requirements.txt            # Locked core dependency
├── domain.py                   # Pure Python entities (Product, PriceBreakdown, etc.)
├── catalog.py                  # Capability definitions and compilation helper
├── app.py                      # Standalone 6-step runnable educational demo
├── tests/
│   ├── test_capabilities.py    # Unit tests for capability execution & domain logic
│   ├── test_metadata_and_registry.py # Tests for metadata, naming, and registry queries
│   └── test_lifecycle_and_errors.py  # Tests for compile freeze, lifecycle, and errors
├── ARCHITECTURE.md             # Deep architectural design and Agnara principles
├── AGENTS.md                   # Guidance for autonomous AI agents
├── CHANGELOG.md                # Release history
├── CONTRIBUTING.md             # Contribution policy (frozen reference app)
├── SECURITY.md                 # Security disclosure process
└── LICENSE                     # Apache 2.0
```

---

## Verification & Output Sample

Running `python app.py` outputs the full lifecycle demonstration:

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
>> Executing async capability: catalog.check_warehouse_availability
   Direct Call Result: Available=True in 'central-hub-eu' (Stock: 45)
   Registry Call Result (CA-010): Available=False in 'central-hub-eu' (Stock: 0)

==============================================================================
  6. OBSERVABLE ERROR BEHAVIORS
==============================================================================
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

## Real Limitations of `agnara==0.1.0a3` & Scope Boundaries

Inspecting the real published package `agnara==0.1.0a3` establishes clear architectural boundaries:

1. **No Transport Adapters in Core:** In 0.1.0a3, Agnara is strictly an execution kernel. HTTP, FastAPI, Flask, MCP, and CLI protocol drivers are deferred to external adapters.
2. **Authoring Decorator Scope:** `@app.capability` in a3 accepts metadata (`name`, `description`, `scopes`, `effects`, `risk`, `confirmation`, `idempotent`), but does not take direct policy rules or dependency injection bindings. Dependency injection is authored via `DIRegistry` (see Reference App #002) and policies via `ScopePolicy` / `ConfirmationVerifier` (see Reference App #003).
3. **No Automatic Reflection at Invocation Time:** Metadata inspection and registry freezing are strictly startup operations. Invoking a capability directly avoids reflection overhead.

---

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).