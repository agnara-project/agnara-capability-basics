---
name: agnara-capabilities
description: Guide for authoring, compiling, and validating Agnara 0.1.0a3 capabilities.
---

# Agnara Capabilities Skill

Use this skill when inspecting, authoring, or verifying capabilities in **Agnara Historical Reference Application #004 (`agnara-capability-basics`)**.

---

## 1. Permitted Public Capability APIs

Import application, definitions, metadata, and registries exclusively from `agnara`:

```python
from agnara import (
    Agnara,
    CapabilityDefinition,
    CapabilityId,
    Confirmation,
    FrozenCapabilityRegistry,
    Idempotency,
    Risk,
    StandardEffect,
)
```

Import canonical exception classes from `agnara.errors` or `agnara`:

```python
from agnara.errors import (
    AgnaraError,
    DefinitionError,
    DuplicateCapabilityError,
    RegistryFrozenError,
    UnknownCapabilityError,
)
```

---

## 2. Capability Declaration Rules

Declare capabilities using an instantiated `Agnara("<namespace>")` instance:

```python
app = Agnara("catalog")


@app.capability(
    name="list_products",  # Optional ID override
    description="Filter and retrieve catalog items.",  # Optional; defaults to docstring
    scopes=["catalog:read"],  # frozenset of permission strings
    effects=[StandardEffect.READ],  # frozenset of side-effects
    risk=Risk.LOW,  # LOW | MEDIUM | HIGH | CRITICAL
    confirmation=Confirmation.NEVER,  # NEVER | POLICY | REQUIRED
    idempotent=True,  # True -> YES, False -> NO, None -> UNKNOWN
)
def list_products(category: str | None = None) -> list[Product]:
    """First paragraph is used as description when description=None."""
    ...
```

### Supported Metadata Values:
- **`effects`:** `StandardEffect.READ`, `CACHE_WRITE`, `DATABASE_WRITE`, `EXTERNAL_WRITE`, `FINANCIAL_WRITE`, `DESTRUCTIVE`.
- **`risk`:** `Risk.LOW`, `MEDIUM`, `HIGH`, `CRITICAL` (or lowercase strings).
- **`confirmation`:** `Confirmation.NEVER`, `POLICY`, `REQUIRED` (or lowercase strings).
- **`idempotency`:** Boolean passed to decorator (`idempotent=True/False/None`) maps to `Idempotency.YES/NO/UNKNOWN`.
- **`scopes`:** Iterable of strings (e.g. `["catalog:read"]`).

---

## 3. Core Architectural Invariants

1. **Unwrapped Handlers:** `@app.capability` must return the handler callable unaltered. Never attach interceptors, wrappers, or closures. Handlers must remain directly testable and directly callable.
2. **Docstring Fallback:** When `description` is omitted, the first paragraph of the function docstring becomes the capability description.
3. **Decoupled Naming:** When `name` is passed, the capability ID is `<app.name>.<name>`, independent of `func.__name__`.
4. **Lifecycle Freeze (ADR 0005):** Calling `app.compile()` transitions the registry from `CapabilityRegistry` to `FrozenCapabilityRegistry`. Any subsequent registration must raise `RegistryFrozenError`.
5. **Lock-free Thread Safety:** `FrozenCapabilityRegistry` is a read-only mapping safe to share across threads under free-threaded CPython 3.14 without mutexes.

---

## 4. Negative Constraints (APIs That Must NOT Be Invented)

- **No `policies` parameter on `@app.capability`:** In `0.1.0a3`, the authoring decorator does not take `policies=...`.
- **No transport routing decorators:** Agnara Core does not provide `@app.route`, `@app.endpoint`, or `@app.tool`.
- **No DI container on direct calls:** Direct calls are raw Python calls without runtime DI resolution.
- **No synthetic async wrapping:** Do not wrap synchronous handlers in async stubs. Sync handlers run synchronously; `async def` handlers run as native coroutines.

---

## 5. Capability Validation Checklist

When authoring or modifying capabilities, verify:
- [ ] Handler executes directly as a plain Python function (`handler(*args)`).
- [ ] Handler executes through the frozen registry (`registry[id].handler(*args)`).
- [ ] Metadata attributes match business intent (`effects`, `risk`, `scopes`, `idempotent`).
- [ ] Registration order and ID uniqueness are preserved.
- [ ] Missing lookups in frozen registry raise `UnknownCapabilityError`.