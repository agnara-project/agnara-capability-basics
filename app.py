"""Runnable demonstration for Agnara Historical Reference Application #004.

This script guides the user step-by-step through the core capability-first model
in Agnara 0.1.0a3:
  1. Declaration & Metadata (pre-compilation)
  2. Direct Invocation of raw Python callables
  3. Compilation (app.compile()) and Registry Freezing
  4. Registry Lookup, Filtering, and Handler Invocation
  5. Asynchronous Capability Execution
  6. Observable Error Handling (Domain, Registry, and Definition errors)

Usage:
    python app.py
"""

from __future__ import annotations

import asyncio
import sys

from agnara import (
    Agnara,
    DefinitionError,
    DuplicateCapabilityError,
    RegistryFrozenError,
    StandardEffect,
    UnknownCapabilityError,
)

import catalog
from domain import (
    InvalidDiscountError,
    InvalidQuantityError,
    ProductNotFoundError,
)


def print_banner(title: str) -> None:
    """Print formatted section separator."""
    print("\n" + "=" * 78)
    print(f"  {title}")
    print("=" * 78)


def step_1_declaration_and_metadata() -> None:
    """Demonstrate capability declaration and inspect uncompiled application state."""
    print_banner("1. DECLARATION & METADATA (Pre-Compilation State)")
    print(f"Application Name (Namespace): '{catalog.app.name}'")
    print(f"Is Compiled? {catalog.app.is_compiled}")
    print(f"Number of registered capabilities: {len(catalog.app.capabilities)}")

    print("\nRegistered Capabilities:")
    for cap_id in catalog.app.capabilities:
        definition = catalog.app.capabilities[cap_id]
        print(f"  - ID:           {cap_id}")
        print(f"    Description:  {definition.description}")
        print(f"    Risk:         {definition.risk.value}")
        print(f"    Effects:      {[e.value for e in definition.effects]}")
        print(f"    Scopes:       {sorted(list(definition.scopes))}")
        print(f"    Idempotency:  {definition.idempotency.value}")
        print()


def step_2_direct_invocation() -> None:
    """Demonstrate direct invocation of unwrapped Python callables."""
    print_banner("2. DIRECT INVOCATION (Zero Decorator Distortion)")
    print("In Agnara, '@app.capability' records the declaration but returns the function")
    print("completely unwrapped and unchanged. Capabilities remain plain Python callables")
    print("that can be called directly by unit tests without framework setup.\n")

    # Call get_product directly
    print(">> Calling catalog.get_product('KB-900') directly:")
    product = catalog.get_product("KB-900")
    print(f"   Result: {product.name} (SKU: {product.sku}) - Price: ${product.price:.2f}")

    # Call calculate_price directly
    print(
        "\n>> Calling catalog.calculate_price('LP-100', quantity=2, "
        "discount_code='SUMMER20') directly:"
    )
    breakdown = catalog.calculate_price("LP-100", quantity=2, discount_code="SUMMER20")
    print(f"   Subtotal:  ${breakdown.subtotal:.2f}")
    print(f"   Discount: -${breakdown.discount_amount:.2f} ({breakdown.discount_code})")
    print(f"   Tax (19%): +${breakdown.tax_amount:.2f}")
    print(f"   Total:     ${breakdown.total:.2f}")


def step_3_and_4_compilation_and_registry() -> catalog.FrozenCapabilityRegistry:
    """Demonstrate app.compile() and registry querying."""
    print_banner("3 & 4. COMPILATION & REGISTRY QUERYING")
    print("Calling 'app.compile()' freezes registration (ADR 0005) and yields an immutable,")
    print("thread-safe FrozenCapabilityRegistry with deterministic ordering.\n")

    registry = catalog.get_compiled_catalog()
    print(f"Is Compiled now? {catalog.app.is_compiled}")
    print(f"Registry Type:   {type(registry).__name__}")
    print(f"Total Entries:   {len(registry)}")

    print("\n>> Querying registry with namespace filter (.in_namespace('catalog')):")
    catalog_caps = list(registry.in_namespace("catalog"))
    print(f"   Found {len(catalog_caps)} capabilities in namespace 'catalog'")

    print("\n>> Querying registry with effect filter (.with_effect(StandardEffect.READ)):")
    read_caps = list(registry.with_effect(StandardEffect.READ))
    print(f"   Found {len(read_caps)} capabilities with effect 'read':")
    for cap in read_caps:
        print(f"   * {cap.id}")

    print("\n>> Invoking capability handler through registry lookup:")
    cap_def = registry["catalog.list_products"]
    items = cap_def.handler(category="peripherals", max_price=100.0)
    print(f"   Filtered peripherals <= $100 via {cap_def.id}:")
    for item in items:
        print(f"   - {item.name} (${item.price:.2f})")

    return registry


def step_5_async_capability(registry: catalog.FrozenCapabilityRegistry) -> None:
    """Demonstrate asynchronous capability execution."""
    print_banner("5. ASYNCHRONOUS CAPABILITY EXECUTION")
    print("Agnara treats asynchronous handlers as first-class citizens.")
    print("Async capabilities are ordinary coroutines executed with standard asyncio.\n")

    async def run_async_checks() -> None:
        cap_def = registry["catalog.check_warehouse_availability"]
        print(f">> Executing async capability: {cap_def.id}")

        # Direct call
        status_direct = await catalog.check_warehouse_availability("KB-900")
        print(
            f"   Direct Call Result: Available={status_direct.available} "
            f"in '{status_direct.warehouse}' (Stock: {status_direct.quantity_on_hand})"
        )

        # Handler invocation through registry
        status_registry = await cap_def.handler("CA-010")
        print(
            f"   Registry Call Result (CA-010): Available={status_registry.available} "
            f"in '{status_registry.warehouse}' (Stock: {status_registry.quantity_on_hand})"
        )

    asyncio.run(run_async_checks())


def step_6_observable_errors(registry: catalog.FrozenCapabilityRegistry) -> None:
    """Demonstrate observable domain, registry, and definition errors."""
    print_banner("6. OBSERVABLE ERROR BEHAVIORS")
    print("Agnara separates domain exceptions from framework lifecycle errors.\n")

    # 1. Domain Error: Product Not Found
    print(">> 1. Domain Error: ProductNotFoundError")
    try:
        catalog.get_product("NON-EXISTENT-SKU")
    except ProductNotFoundError as exc:
        print(f"   CAUGHT EXPECTED: {type(exc).__name__}: {exc}")

    # 2. Domain Error: Invalid Quantity
    print("\n>> 2. Domain Error: InvalidQuantityError")
    try:
        catalog.calculate_price("KB-900", quantity=0)
    except InvalidQuantityError as exc:
        print(f"   CAUGHT EXPECTED: {type(exc).__name__}: {exc}")

    # 3. Domain Error: Invalid Discount
    print("\n>> 3. Domain Error: InvalidDiscountError")
    try:
        catalog.calculate_price("KB-900", quantity=1, discount_code="INVALID_PROMO")
    except InvalidDiscountError as exc:
        print(f"   CAUGHT EXPECTED: {type(exc).__name__}: {exc}")

    # 4. Registry Error: Unknown capability lookup
    print("\n>> 4. Registry Error: UnknownCapabilityError")
    try:
        _ = registry["catalog.non_existent_capability"]
    except UnknownCapabilityError as exc:
        print(f"   CAUGHT EXPECTED: {type(exc).__name__}: {exc}")

    # 5. Registry Lifecycle Error: Registration after compilation
    print("\n>> 5. Lifecycle Error: RegistryFrozenError")
    try:

        @catalog.app.capability
        def late_addition() -> None:
            """Attempting registration after app.compile()."""
            pass
    except RegistryFrozenError as exc:
        print(f"   CAUGHT EXPECTED: {type(exc).__name__}: {exc}")

    # 6. Definition Error: Duplicate capability registration
    print("\n>> 6. Definition Error: DuplicateCapabilityError")
    fresh_app = Agnara("isolated")

    @fresh_app.capability(name="entry")
    def original_entry() -> str:
        return "first"

    try:

        @fresh_app.capability(name="entry")
        def duplicate_entry() -> str:
            return "duplicate"
    except DuplicateCapabilityError as exc:
        print(f"   CAUGHT EXPECTED: {type(exc).__name__}: {exc}")

    # 7. Definition Error: Invalid capability identifier
    print("\n>> 7. Definition Error: DefinitionError (Malformed Name)")
    try:

        @fresh_app.capability(name="invalid-dashed-name")
        def bad_named_entry() -> None:
            pass
    except DefinitionError as exc:
        print(f"   CAUGHT EXPECTED: {type(exc).__name__}: {exc}")


def main() -> None:
    """Run the complete pedagogical demonstration."""
    print("=" * 78)
    print("  Agnara Historical Reference Application #004: agnara-capability-basics")
    print("  Target: agnara==0.1.0a3 | Python: CPython >=3.14 | Status: Historical / Frozen")
    print("=" * 78)
    print(f"Python Version: {sys.version.split()[0]}")

    step_1_declaration_and_metadata()
    step_2_direct_invocation()
    registry = step_3_and_4_compilation_and_registry()
    step_5_async_capability(registry)
    step_6_observable_errors(registry)

    print_banner("DEMONSTRATION COMPLETED SUCCESSFULLY")
    print("You have observed the entire capability lifecycle: declaration, metadata,")
    print("direct invocation, compilation freeze, and error semantics in Agnara 0.1.0a3.\n")


if __name__ == "__main__":
    main()
