# Public API Surface & Boundaries in Agnara 0.1.0a3

This document explicitly defines the permitted public API surface in `agnara==0.1.0a3` for **Agnara Historical Reference Application #004 (`agnara-capability-basics`)**, and lists all prohibited or speculative APIs.

---

## 1. Permitted Public Imports

### Core Types & Metadata (`agnara`)
- `Agnara`: Composition root and application namespace owner.
- `CapabilityDefinition`: Immutable declaration record.
- `CapabilityId`: Stable identifier composed of `namespace` and `name`.
- `FrozenCapabilityRegistry`: Read-only mapping returned by `app.compile()`.
- `StandardEffect`: Side-effect enum (`READ`, `CACHE_WRITE`, `DATABASE_WRITE`, `EXTERNAL_WRITE`, `FINANCIAL_WRITE`, `DESTRUCTIVE`).
- `Risk`: Operational damage potential enum (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- `Confirmation`: Human-in-the-loop requirement enum (`NEVER`, `POLICY`, `REQUIRED`).
- `Idempotency`: Honest retry state enum (`YES`, `NO`, `UNKNOWN`).

### Error Hierarchy (`agnara.errors`)
- `AgnaraError`: Base exception for all Agnara-originated errors.
- `DefinitionError`: Raised on invalid identifiers, non-callables, or invalid enum values.
- `DuplicateCapabilityError`: Raised when two capabilities share the same logical ID.
- `RegistryFrozenError`: Raised when attempting to register capabilities post-compilation.
- `UnknownCapabilityError`: Raised on missing key lookups in `FrozenCapabilityRegistry` (subclass of `KeyError`).

---

## 2. Real `@app.capability` Signature in 0.1.0a3

```python
def capability(
    self,
    handler: Any = None,
    /,
    *,
    name: str | None = None,
    description: str | None = None,
    scopes: Iterable[str] = (),
    effects: Iterable[str] = (),
    risk: Risk | str = Risk.LOW,
    confirmation: Confirmation | str = Confirmation.NEVER,
    idempotent: bool | None = None,
) -> Any: ...
```

---

## 3. Negative Boundaries: Prohibited Anti-Patterns

To preserve historical accuracy, the following APIs and anti-patterns must **never** be introduced:

| Prohibited Anti-Pattern | Why Prohibited in #004 / 0.1.0a3 |
|---|---|
| `@app.capability(policies=...)` | The authoring decorator in `0.1.0a3` does not accept a `policies` argument. Policies are evaluated in execution pipelines (see Reference App #003). |
| `@app.route`, `@app.endpoint`, `@app.tool` | Agnara Core is strictly transport-neutral (ADR 0002). Transports project onto capabilities, never the reverse. |
| External Infrastructure | No FastAPI, Flask, Starlette, SQL databases, or LLM SDKs. All data remains in-memory Python structures. |
| Synthetic Handlers | `@app.capability` must return the function unaltered. No proxy wrappers or interceptors. |
| Future / Speculative APIs | Do not backport or anticipate features from unreleased versions or unmerged PRs. |