"""Domain entities, exceptions, and business logic for the product catalog.

This module is intentionally pure Python: it contains no transport bindings,
no serialization frameworks, and no web or CLI infrastructure. In Agnara,
capabilities wrap genuine business operations and domain logic rather than
framework plumbing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# -----------------------------------------------------------------------------
# Domain Exceptions
# -----------------------------------------------------------------------------


class CatalogDomainError(Exception):
    """Base exception for all catalog domain errors."""


class ProductNotFoundError(CatalogDomainError):
    """Raised when a requested product SKU does not exist in the catalog."""

    def __init__(self, sku: str) -> None:
        self.sku = sku
        super().__init__(f"Product with SKU '{sku}' not found in catalog")


class InvalidQuantityError(CatalogDomainError):
    """Raised when an order or pricing calculation specifies an invalid quantity."""

    def __init__(self, quantity: int) -> None:
        self.quantity = quantity
        super().__init__(f"Quantity must be a positive integer, got: {quantity}")


class InvalidDiscountError(CatalogDomainError):
    """Raised when an unrecognized or expired discount code is provided."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"Invalid or unrecognized discount code: '{code}'")


# -----------------------------------------------------------------------------
# Domain Models
# -----------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Product:
    """Represents a product in the catalog."""

    sku: str
    name: str
    category: str
    price: float
    in_stock: bool


@dataclass(frozen=True, slots=True)
class PriceBreakdown:
    """Detailed price calculation breakdown for a purchase."""

    sku: str
    quantity: int
    unit_price: float
    subtotal: float
    discount_amount: float
    tax_amount: float
    total: float
    discount_code: str | None


@dataclass(frozen=True, slots=True)
class InventoryStatus:
    """Physical inventory status from warehouse logistics."""

    sku: str
    available: bool
    quantity_on_hand: int
    warehouse: str
    estimated_delivery_days: int


# -----------------------------------------------------------------------------
# Seed Data & Domain Rules
# -----------------------------------------------------------------------------

TAX_RATE: Final[float] = 0.19  # 19% standard VAT

AVAILABLE_DISCOUNTS: Final[dict[str, float]] = {
    "WELCOME10": 0.10,
    "SUMMER20": 0.20,
    "DEV5": 0.05,
}

CATALOG_DATABASE: Final[dict[str, Product]] = {
    "KB-900": Product(
        sku="KB-900",
        name="Mechanical Keyboard Pro",
        category="peripherals",
        price=129.99,
        in_stock=True,
    ),
    "MO-450": Product(
        sku="MO-450",
        name="Ergonomic Wireless Mouse",
        category="peripherals",
        price=59.99,
        in_stock=True,
    ),
    "LP-100": Product(
        sku="LP-100",
        name="Ultra Developer Laptop 16",
        category="computers",
        price=1499.00,
        in_stock=True,
    ),
    "CA-010": Product(
        sku="CA-010",
        name="USB-C Fast Charging Cable 2m",
        category="accessories",
        price=19.99,
        in_stock=False,
    ),
}

WAREHOUSE_DATABASE: Final[dict[str, tuple[int, str, int]]] = {
    "KB-900": (45, "central-hub-eu", 2),
    "MO-450": (120, "central-hub-eu", 2),
    "LP-100": (12, "express-hub-us", 1),
    "CA-010": (0, "central-hub-eu", 7),
}


# -----------------------------------------------------------------------------
# Domain Service Functions
# -----------------------------------------------------------------------------


def find_product_by_sku(sku: str) -> Product:
    """Retrieve a product by SKU, raising ProductNotFoundError if missing."""
    product = CATALOG_DATABASE.get(sku)
    if product is None:
        raise ProductNotFoundError(sku)
    return product


def search_products(
    category: str | None = None,
    max_price: float | None = None,
) -> list[Product]:
    """Filter catalog products by optional category and maximum price criteria."""
    results: list[Product] = []
    for product in CATALOG_DATABASE.values():
        if category is not None and product.category.lower() != category.lower():
            continue
        if max_price is not None and product.price > max_price:
            continue
        results.append(product)
    return results


def compute_pricing(
    sku: str,
    quantity: int,
    discount_code: str | None = None,
) -> PriceBreakdown:
    """Compute full pricing breakdown for a product quantity with optional discount."""
    if quantity <= 0:
        raise InvalidQuantityError(quantity)

    product = find_product_by_sku(sku)

    discount_rate = 0.0
    if discount_code is not None:
        normalized_code = discount_code.strip().upper()
        if normalized_code not in AVAILABLE_DISCOUNTS:
            raise InvalidDiscountError(discount_code)
        discount_rate = AVAILABLE_DISCOUNTS[normalized_code]

    unit_price = round(product.price, 2)
    subtotal = round(unit_price * quantity, 2)
    discount_amount = round(subtotal * discount_rate, 2)
    taxable_amount = round(subtotal - discount_amount, 2)
    tax_amount = round(taxable_amount * TAX_RATE, 2)
    total = round(taxable_amount + tax_amount, 2)

    return PriceBreakdown(
        sku=sku,
        quantity=quantity,
        unit_price=unit_price,
        subtotal=subtotal,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        total=total,
        discount_code=discount_code,
    )


def lookup_warehouse_inventory(sku: str) -> InventoryStatus:
    """Check physical warehouse availability and lead time for a given SKU."""
    product = find_product_by_sku(sku)
    wh_info = WAREHOUSE_DATABASE.get(sku)
    if wh_info is None:
        return InventoryStatus(
            sku=product.sku,
            available=False,
            quantity_on_hand=0,
            warehouse="unknown",
            estimated_delivery_days=14,
        )

    qty, warehouse_name, delivery_days = wh_info
    return InventoryStatus(
        sku=product.sku,
        available=qty > 0,
        quantity_on_hand=qty,
        warehouse=warehouse_name,
        estimated_delivery_days=delivery_days,
    )
