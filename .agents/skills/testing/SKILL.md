---
name: testing
description: Guide for verifying capabilities, metadata, lifecycle freeze, and error semantics.
---

# Testing Skill

Use this skill when authoring, running, or verifying tests in **Agnara Historical Reference Application #004 (`agnara-capability-basics`)**.

---

## 1. Testing Invariants for Capabilities

Every capability change must be verified against seven essential dimensions:

1. **Direct Callable Invocation:**
   - Assert that calling the handler directly (`get_product("SKU")`) executes the underlying business logic without framework wrappers.
   - Assert that return values match expected domain dataclasses (`Product`, `PriceBreakdown`, etc.).
2. **Registry Handler Parity:**
   - Assert that `registry["catalog.get_product"].handler("SKU")` returns identical results to direct callable invocation.
3. **Agentic Metadata Accuracy:**
   - Assert that declared `effects`, `risk`, `confirmation`, `idempotency`, and `scopes` match the specification.
   - Assert that `.has_effect(effect)` and `.requires_scope(scope)` return expected booleans.
4. **Registry Query Protocols:**
   - Assert that `registry.in_namespace("catalog")` filters correctly by namespace.
   - Assert that `registry.with_effect(StandardEffect.READ)` filters correctly by effect.
   - Assert standard `Mapping` protocol methods (`keys()`, `values()`, `items()`, `__len__`, `__contains__`).
5. **Compilation Freeze Lifecycle (ADR 0005):**
   - Assert `app.is_compiled` transitions from `False` to `True` upon `app.compile()`.
   - Assert that registering a capability post-freeze raises `RegistryFrozenError`.
6. **Error Path Verification:**
   - Domain errors: assert missing SKUs raise `ProductNotFoundError`, invalid quantities raise `InvalidQuantityError`.
   - Registry errors: assert missing keys raise `UnknownCapabilityError` (subclass of `KeyError`).
   - Definition errors: assert duplicate IDs raise `DuplicateCapabilityError`, malformed identifiers raise `DefinitionError`.
7. **Asynchronous Execution:**
   - Assert that `async def` capabilities execute cleanly with standard `asyncio.run()`.

---

## 2. Running Quality Gates

Always run the full quality gate sequence prior to submitting changes:

```powershell
# 1. Check code formatting
ruff format --check .

# 2. Check code linting
ruff check .

# 3. Run full test suite
pytest -v

# 4. Run interactive demonstration
python app.py

# 5. Verify packaging build
pip wheel . --no-deps -w dist
Remove-Item -Recurse -Force dist
```

All commands must exit with return code `0`.