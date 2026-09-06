# Capability Lifecycle in Agnara 0.1.0a3

This document details the exact execution and compilation lifecycle of a Capability in `agnara==0.1.0a3`.

---

## 1. Lifecycle State Diagram

```
       ┌───────────────────────────┐
       │   Agnara("<namespace>")   │ (Instantiation)
       └─────────────┬─────────────┘
                     │
                     ▼
       ┌───────────────────────────┐
       │     @app.capability       │ (Declaration Phase)
       │  - Unwrapped function     │
       │  - Validates identifiers  │
       │  - Extracts docstring     │
       │  - Appends to registry    │
       └─────────────┬─────────────┘
                     │
                     ▼
             app.compile()           (Freeze Transition - ADR 0005)
                     │
                     ▼
       ┌───────────────────────────┐
       │  FrozenCapabilityRegistry │ (Runtime Phase)
       │  - Read-only Mapping      │
       │  - Lock-free thread safe  │
       │  - Deterministic order    │
       │  - Registration closed    │
       └─────────────┬─────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
 Direct Invocation       Registry Handler Call
  get_product(sku)      reg[id].handler(sku)
```

---

## 2. Detailed Lifecycle Stages

### Stage 1: Application Instantiation
- Instantiating `Agnara(name)` establishes the namespace for all capabilities declared on it.
- `name` must be a valid Python identifier (validated via `CapabilityId(namespace=name, name="probe")`).
- `app.is_compiled` starts as `False`.

### Stage 2: Capability Declaration
- The `@app.capability` decorator accepts optional metadata: `name`, `description`, `scopes`, `effects`, `risk`, `confirmation`, `idempotent`.
- **Identity Formation:** The capability ID is constructed as `<namespace>.<name>`. If `name` is omitted, `func.__name__` is used.
- **Description Extraction:** If `description` is omitted, the first paragraph of `func.__doc__` is automatically captured.
- **Unwrapped Return:** The decorator returns the original callable without proxies or wrappers.
- Duplicate IDs raise `DuplicateCapabilityError`.

### Stage 3: Compilation Freeze (ADR 0005)
- Calling `app.compile()` calls `registry.freeze()`.
- The internal registry becomes read-only and is wrapped in a `FrozenCapabilityRegistry`.
- `app.is_compiled` becomes `True`.
- Any subsequent call to `@app.capability` immediately raises `RegistryFrozenError`.

### Stage 4: Registry Lookup & Querying
- The `FrozenCapabilityRegistry` implements `collections.abc.Mapping[CapabilityId, CapabilityDefinition]`.
- Lookups can use string IDs (`"catalog.get_product"`) or `CapabilityId` objects. Missing keys raise `UnknownCapabilityError`.
- Filtering methods:
  - `registry.in_namespace("catalog")`: Yields all capabilities belonging to that namespace.
  - `registry.with_effect(StandardEffect.READ)`: Yields all capabilities declaring the specified effect.

### Stage 5: Execution & Error Propagation
- Direct calls (`get_product(...)`) bypass the registry mapping and execute with zero framework overhead.
- Registry lookups (`registry[id].handler(...)`) invoke the exact same underlying function.
- Domain exceptions (`ProductNotFoundError`, `InvalidQuantityError`) propagate naturally through both invocation pathways.