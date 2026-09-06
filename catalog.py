"""Agnara Capability Declarations for the Product Catalog.

This module demonstrates the capability-first authoring model in Agnara 0.1.0a3.
Here, business operations are declared as Capabilities using ``Agnara("catalog")``.

Key Principles Demonstrated:
1. Operations represent business capabilities, not transport endpoints.
2. The ``@app.capability`` decorator records declarations without wrapping or altering
   the underlying callable.
3. Capabilities carry agentic metadata (effects, risks, scopes, confirmation, idempotency).
4. Synchronous and asynchronous capabilities share identical declaration ergonomics.
5. Compilation produces an immutable, thread-safe ``FrozenCapabilityRegistry``.
"""

from __future__ import annotations

import asyncio

from agnara import Agnara, Confirmation, FrozenCapabilityRegistry, Risk, StandardEffect

from domain import (
    InventoryStatus,
    PriceBreakdown,
    Product,
    compute_pricing,
    find_product_by_sku,
    lookup_warehouse_inventory,
    search_products,
)

# Initialize the Agnara application.
# The application name defines the logical namespace for all its capabilities:
# e.g., 'catalog' -> 'catalog.get_product'.
app = Agnara("catalog")


# -----------------------------------------------------------------------------
# 1. Single Entity Lookup: Docstring Description & Implicit Naming
# -----------------------------------------------------------------------------
@app.capability(
    scopes=["catalog:read"],
    effects=[StandardEffect.READ],
    risk=Risk.LOW,
    confirmation=Confirmation.NEVER,
    idempotent=True,
)
def get_product(sku: str) -> Product:
    """Retrieve product specifications by its unique SKU identifier.

    This docstring's first paragraph is automatically captured as the capability's
    description metadata because no explicit 'description' parameter was passed.
    This prevents documentation drift between code comments and agent manifests.
    """
    return find_product_by_sku(sku)


# -----------------------------------------------------------------------------
# 2. Collection Query: Explicit Naming Decoupling & Optional Parameters
# -----------------------------------------------------------------------------
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
    """Internal implementation for listing products.

    Notice that the capability ID is explicitly declared as 'list_products',
    so the public ID is 'catalog.list_products', despite the Python function
    being named 'query_catalog_items'. This protects policy rules and client
    manifests from breaking during internal code refactors.
    """
    return search_products(category=category, max_price=max_price)


# -----------------------------------------------------------------------------
# 3. Calculation & Business Rule Validation: Structured Return Type
# -----------------------------------------------------------------------------
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
    """Calculate price breakdown for a purchase.

    Capabilities are not restricted to database CRUD; pure business algorithms
    and domain calculations are first-class capabilities.
    """
    return compute_pricing(sku=sku, quantity=quantity, discount_code=discount_code)


# -----------------------------------------------------------------------------
# 4. Asynchronous Capability: Non-blocking Logistics Check
# -----------------------------------------------------------------------------
@app.capability(
    description="Asynchronously query real-time warehouse logistics for stock availability.",
    scopes=["inventory:read"],
    effects=[StandardEffect.READ],
    risk=Risk.LOW,
    confirmation=Confirmation.NEVER,
    idempotent=True,
)
async def check_warehouse_availability(sku: str) -> InventoryStatus:
    """Asynchronously check warehouse inventory with non-blocking I/O simulation.

    Agnara supports asynchronous handlers transparently. The decorator preserves
    the async callable without synthetic wrappers.
    """
    # Simulate non-blocking network I/O to a remote warehouse management system
    await asyncio.sleep(0.01)
    return lookup_warehouse_inventory(sku)


# -----------------------------------------------------------------------------
# Application Compilation Helper
# -----------------------------------------------------------------------------
def get_compiled_catalog() -> FrozenCapabilityRegistry:
    """Compile the Agnara application and return the immutable FrozenCapabilityRegistry.

    Compilation freezes the registry (ADR 0005): no further capabilities can be
    registered, ensuring deterministic order and thread-safety under free-threaded
    CPython without locks.
    """
    if not app.is_compiled:
        return app.compile()
    return app.capabilities.freeze()
