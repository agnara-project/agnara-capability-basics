"""Tests for catalog capabilities: execution, inputs, outputs, and domain errors."""

import asyncio

import pytest

import catalog
from domain import (
    InvalidDiscountError,
    InvalidQuantityError,
    PriceBreakdown,
    Product,
    ProductNotFoundError,
)


def test_get_product_success() -> None:
    """get_product returns the matching Product domain model."""
    product = catalog.get_product("KB-900")
    assert isinstance(product, Product)
    assert product.sku == "KB-900"
    assert product.name == "Mechanical Keyboard Pro"
    assert product.category == "peripherals"
    assert product.price == 129.99
    assert product.in_stock is True


def test_get_product_not_found() -> None:
    """get_product raises ProductNotFoundError for non-existent SKUs."""
    with pytest.raises(ProductNotFoundError) as exc_info:
        catalog.get_product("DOES-NOT-EXIST")
    assert exc_info.value.sku == "DOES-NOT-EXIST"
    assert "not found in catalog" in str(exc_info.value)


def test_list_products_no_filter() -> None:
    """list_products returns all products when no filters are supplied."""
    products = catalog.query_catalog_items()
    assert len(products) == 4
    skus = [p.sku for p in products]
    assert "KB-900" in skus
    assert "LP-100" in skus


def test_list_products_category_filter() -> None:
    """list_products filters by category case-insensitively."""
    peripherals = catalog.query_catalog_items(category="peripherals")
    assert len(peripherals) == 2
    assert all(p.category == "peripherals" for p in peripherals)

    computers = catalog.query_catalog_items(category="COMPUTERS")
    assert len(computers) == 1
    assert computers[0].sku == "LP-100"


def test_list_products_max_price_filter() -> None:
    """list_products filters by maximum price threshold."""
    budget = catalog.query_catalog_items(max_price=60.00)
    assert len(budget) == 2
    assert {p.sku for p in budget} == {"MO-450", "CA-010"}


def test_calculate_price_standard() -> None:
    """calculate_price calculates correct subtotal, tax, and total without discount."""
    result = catalog.calculate_price("KB-900", quantity=2)
    assert isinstance(result, PriceBreakdown)
    assert result.sku == "KB-900"
    assert result.quantity == 2
    assert result.unit_price == 129.99
    assert result.subtotal == 259.98
    assert result.discount_amount == 0.0
    assert result.tax_amount == 49.40
    assert result.total == 309.38
    assert result.discount_code is None


def test_calculate_price_with_discount() -> None:
    """calculate_price applies recognized discount codes correctly."""
    result = catalog.calculate_price("LP-100", quantity=1, discount_code="welcome10")
    assert result.discount_amount == 149.90
    assert result.total == 1605.43


def test_calculate_price_invalid_quantity() -> None:
    """calculate_price rejects non-positive quantities."""
    with pytest.raises(InvalidQuantityError) as exc_info:
        catalog.calculate_price("KB-900", quantity=0)
    assert exc_info.value.quantity == 0

    with pytest.raises(InvalidQuantityError):
        catalog.calculate_price("KB-900", quantity=-5)


def test_calculate_price_invalid_discount() -> None:
    """calculate_price rejects unrecognized discount codes."""
    with pytest.raises(InvalidDiscountError) as exc_info:
        catalog.calculate_price("KB-900", quantity=1, discount_code="FAKE_CODE")
    assert exc_info.value.code == "FAKE_CODE"


def test_async_warehouse_availability() -> None:
    """check_warehouse_availability runs asynchronously and returns inventory status."""

    async def _run() -> None:
        in_stock_res = await catalog.check_warehouse_availability("KB-900")
        assert in_stock_res.sku == "KB-900"
        assert in_stock_res.available is True
        assert in_stock_res.quantity_on_hand == 45
        assert in_stock_res.warehouse == "central-hub-eu"

        out_of_stock_res = await catalog.check_warehouse_availability("CA-010")
        assert out_of_stock_res.available is False
        assert out_of_stock_res.quantity_on_hand == 0

    asyncio.run(_run())


def test_direct_call_equals_registry_handler_call() -> None:
    """Direct callable invocation produces identical results to registry handler call."""
    registry = catalog.get_compiled_catalog()
    cap_def = registry["catalog.get_product"]

    direct_result = catalog.get_product("MO-450")
    handler_result = cap_def.handler("MO-450")

    assert direct_result == handler_result
    assert direct_result.sku == "MO-450"
