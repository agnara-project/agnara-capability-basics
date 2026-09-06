# Architectural Guide — Agnara Capability Fundamentals

This document details the architectural principles and design patterns implemented in **Agnara Historical Reference Application #004: `agnara-capability-basics`**, based on `agnara==0.1.0a3` and CPython >= 3.14.

---

## 1. The Capability-First Mental Model

Most modern application frameworks organize around **transports**:
- Web frameworks organize around **HTTP endpoints** (URLs, query parameters, headers, HTTP methods).
- RPC frameworks organize around **protocol buffers or service interfaces** (gRPC stubs, Thrift).
- Agentic tool frameworks organize around **LLM function declarations** (OpenAI tool schemas, MCP servers).

When the same business capability must be exposed over multiple transports (e.g. an e-commerce catalog query accessible via REST API, CLI, background cron, and an AI chat assistant), developers usually:
1. Couple logic directly into controller functions, making multi-channel reuse impossible; or
2. Build artificial layered abstractions (Services, UseCases, Interactors, DTOs, Adapters) that introduce heavy boilerplate and mental overhead.

**Agnara solves this by making the Capability the primary unit of software construction.**

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
│   Registry State:       Frozen post-startup                 │
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
- Is **transport-neutral**: it has no knowledge of JSON, query strings, headers, or sockets.
- Carries **agentic metadata**: metadata describing operational risk, side effects, authorization scopes, and idempotency in standardized vocabularies.

---

## 2. Two-Phase Registry Lifecycle (ADR 0005)

A critical architectural guarantee in Agnara is the strict separation between the **authoring/assembly phase** and the **runtime/execution phase**.

```
  [Authoring Phase]                            [Runtime Phase]
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
Rather than using a single `CapabilityRegistry` class with an internal boolean flag (`self.is_frozen = True`), Agnara establishes two distinct types:
1. `CapabilityRegistry`: Used only during setup. Has a `register()` method protected by a mutex.
2. `FrozenCapabilityRegistry`: The compiled product. Does **not** expose a `register()` method at all.

This structural separation means misuse (such as attempting dynamic capability registration during request execution) is fundamentally invalid. Under free-threaded CPython 3.14 (PEP 703), the frozen registry requires no locks for read operations across thousands of concurrent threads.

---

## 3. The Unwrapped Callable Guarantee

In many Python frameworks, decorators wrap functions in closures or proxy objects (`functools.wraps`). While convenient for injecting behavior, wrapping introduces subtle issues:
- Signature reflection becomes complicated.
- Unit testing requires initializing framework contexts or mocking decorator dependencies.
- Overhead accumulates on hot paths.

In Agnara:
```python
# Inside agnara.application:
def declare(func):
    self._registry.register(CapabilityDefinition.declare(...))
    return func  # The exact same function is returned!
```

Because the function is returned unaltered:
1. **Direct Unit Testing:** You can test your business logic by calling `get_product("SKU-1")` directly, with zero Agnara runtime setup.
2. **Zero Runtime Interception Overhead:** If you call the function directly, you pay zero framework tax.
3. **Purity:** The function remains a standard Python callable. Registration is an observational side effect at startup, not a functional mutation.

---

## 4. Metadata Vocabularies & Agentic Introspection

Agnara defines standardized agentic metadata attributes in `agnara.capability.metadata`:

### StandardEffect
Side-effects tell discovery systems, audit systems, and transactional wrappers what kind of impact a capability will have:
- `StandardEffect.READ`: Read-only operation; causes no persistent state mutations.
- `StandardEffect.CACHE_WRITE`: Mutates transient cache state.
- `StandardEffect.DATABASE_WRITE`: Mutates persistent application storage.
- `StandardEffect.EXTERNAL_WRITE`: Interacts mutably with third-party external services.
- `StandardEffect.FINANCIAL_WRITE`: Executes monetary transactions.
- `StandardEffect.DESTRUCTIVE`: Irreversibly alters or deletes domain data.

### Risk
Expresses the potential blast radius of an unauthorized or buggy invocation:
- `Risk.LOW`: Safe, localized read operations or non-sensitive modifications.
- `Risk.MEDIUM`: Standard business modifications (updating profile, placing standard order).
- `Risk.HIGH`: Administrative mutations, privilege escalation, or sensitive data exports.
- `Risk.CRITICAL`: Account deletion, infrastructure modification, bulk data deletion.

### Confirmation
Declares human-in-the-loop requirements:
- `Confirmation.NEVER`: Can run autonomously without human authorization.
- `Confirmation.POLICY`: An external authorization policy evaluates context to decide.
- `Confirmation.REQUIRED`: Requires explicit human verification before execution.

### Idempotency
- `Idempotency.YES`: Retrying the operation with identical inputs is safe and produces identical state.
- `Idempotency.NO`: Retrying modifies state further (e.g. charging a credit card).
- `Idempotency.UNKNOWN`: Default. Agnara explicitly avoids assuming idempotency unless stated.

---

## 5. Domain Design & Error Architecture

This application maintains clean separation between domain logic and framework lifecycle:

```
                  ┌──────────────────────┐
                  │      Exception       │
                  └──────────┬───────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   ┌─────────────────┐               ┌─────────────────┐
   │   AgnaraError   │               │CatalogDomainErr │
   └────────┬────────┘               └────────┬────────┘
            │                                 │
     ┌──────┴──────┐                   ┌──────┴──────┐
     ▼             ▼                   ▼             ▼
DefinitionErr  RegistryErr       ProductNotFound  InvalidQuantity
                   │
            ┌──────┴──────┐
            ▼             ▼
       UnknownCap   RegistryFrozen
```

- **Domain Errors (`ProductNotFoundError`, `InvalidQuantityError`):** Represent business rule violations. They are raised directly by domain functions and propagate naturally without being swallowed by Agnara.
- **Framework Errors (`DefinitionError`, `RegistryFrozenError`, `UnknownCapabilityError`):** Represent architectural violations (e.g., malformed capability naming, post-compilation registration, missing capability keys).