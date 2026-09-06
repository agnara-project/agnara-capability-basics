# Architecture — Agnara Capability Fundamentals

This document specifies the architectural principles and design patterns implemented in **Agnara Historical Reference Application #004 (`agnara-capability-basics`)**, based on `agnara==0.1.0a3` and CPython >= 3.14.

---

## 1. Capability-First vs Transport-First Architecture

Traditional backend architectures organize code around **transports**:
- Web frameworks structure logic around **HTTP routes** (`@app.get("/items")`).
- RPC frameworks structure logic around **proto service definitions**.
- Agent tool frameworks structure logic around **LLM function declarations**.

When the same operation must be exposed across HTTP, CLI, and AI agents, developers either duplicate logic or construct elaborate abstraction layers.

**Agnara inverts this: the Capability is the foundational building block.**

```
               ┌───────────────────────────────┐
               │    Application Transports     │
               │  REST │ MCP │ CLI │ Queue     │
               └───────────────┬───────────────┘
                               │ (Transports project outward)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     Capability Layer                        │
│                                                             │
│   Stable Logical ID:    "catalog.get_product"               │
│   Handler:              Callable[..., Any] (pure Python)    │
│   Agentic Metadata:     Effects, Risk, Confirmation, Scopes │
│   Registry State:       Frozen post-compilation             │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Invokes directly)
                               ▼
               ┌───────────────────────────────┐
               │         Domain Logic          │
               │   Entities, Invariants, Pure  │
               └───────────────────────────────┘
```

A capability:
- Represents an **atomic business operation**.
- Is **transport-neutral**: it knows nothing of HTTP status codes, JSON wire formats, or sockets.
- Carries **agentic metadata**: standardized descriptions of side effects, operational risk, authorization scopes, and idempotency.

---

## 2. Two-Phase Registry Lifecycle (ADR 0005)

Agnara enforces a structural separation between startup registration and runtime execution:

```
  [Startup / Authoring Phase]                  [Runtime Execution Phase]
  app = Agnara("catalog")
  @app.capability(...)
  def op1(): ...
  @app.capability(...)
  def op2(): ...
         │
         │  app.compile() (Freeze Event)
         ▼
  ┌───────────────────────────────────────────────────────────┐
  │                 FrozenCapabilityRegistry                  │
  │  - Read-only Mapping[CapabilityId, CapabilityDefinition]  │
  │  - Lock-free thread-safe lookups                         │
  │  - Deterministic iteration order                          │
  │  - Registration closed (RegistryFrozenError on write)     │
  └───────────────────────────────────────────────────────────┘
```

### Why Two Distinct Types?
Rather than a single class with a mutable `self._is_frozen` flag, Agnara uses two distinct types:
1. `CapabilityRegistry`: Mutable collection used during startup. `register()` is guarded by a mutex.
2. `FrozenCapabilityRegistry`: The compiled mapping proxy. Does **not** expose `register()`.

This guarantees that runtime capability mutation fails structurally. Under free-threaded CPython 3.14 (PEP 703), concurrent readers access the frozen registry without lock contention.

---

## 3. The Unwrapped Callable Guarantee

In many frameworks, decorators wrap functions in closures or proxy objects, introducing overhead and complicating direct testing.

In Agnara:
```python
def declare(func):
    self._registry.register(...)
    return func  # Original callable returned untouched!
```

Because `@app.capability` returns the callable unaltered:
- **Zero Overhead:** Calling `get_product(...)` directly pays zero framework penalty.
- **Direct Testing:** Unit tests call domain functions directly without initializing DI containers or mocking framework contexts.

---

## 4. Metadata Vocabularies

Agnara standardizes operational metadata in `agnara.capability.metadata`:
- **`StandardEffect`:** `READ`, `CACHE_WRITE`, `DATABASE_WRITE`, `EXTERNAL_WRITE`, `FINANCIAL_WRITE`, `DESTRUCTIVE`.
- **`Risk`:** `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
- **`Confirmation`:** `NEVER`, `POLICY`, `REQUIRED`.
- **`Idempotency`:** `YES`, `NO`, `UNKNOWN` (mapped from `idempotent=True/False/None`).