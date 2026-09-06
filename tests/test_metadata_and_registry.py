"""Tests for capability identity, agentic metadata, and FrozenCapabilityRegistry queries."""

from agnara import (
    CapabilityId,
    Confirmation,
    Idempotency,
    Risk,
    StandardEffect,
)

import catalog


def test_capability_identity_and_naming() -> None:
    """CapabilityId combines application namespace and declared name."""
    registry = catalog.get_compiled_catalog()

    # Implicit name from python function
    get_prod_def = registry["catalog.get_product"]
    assert isinstance(get_prod_def.id, CapabilityId)
    assert get_prod_def.id.namespace == "catalog"
    assert get_prod_def.id.name == "get_product"
    assert str(get_prod_def.id) == "catalog.get_product"

    # Explicit name override: python function is query_catalog_items,
    # but declared capability name is list_products.
    list_prod_def = registry["catalog.list_products"]
    assert list_prod_def.id.name == "list_products"
    assert list_prod_def.handler.__name__ == "query_catalog_items"


def test_description_handling() -> None:
    """Docstring first paragraph acts as default, while explicit description takes precedence."""
    registry = catalog.get_compiled_catalog()

    # get_product had no explicit description parameter: docstring summary was captured
    get_prod_def = registry["catalog.get_product"]
    assert (
        get_prod_def.description == "Retrieve product specifications by its unique SKU identifier."
    )

    # list_products had explicit description
    list_prod_def = registry["catalog.list_products"]
    assert list_prod_def.description == "Filter and retrieve matching products from the catalog."


def test_agentic_metadata_values() -> None:
    """Metadata correctly populates effects, risk, confirmation, idempotency, and scopes."""
    registry = catalog.get_compiled_catalog()
    calc_def = registry["catalog.calculate_price"]

    assert calc_def.risk == Risk.LOW
    assert calc_def.confirmation == Confirmation.NEVER
    assert calc_def.idempotency == Idempotency.YES
    assert StandardEffect.READ in calc_def.effects
    assert calc_def.has_effect(StandardEffect.READ) is True
    assert calc_def.has_effect(StandardEffect.DESTRUCTIVE) is False
    assert "catalog:read" in calc_def.scopes
    assert calc_def.requires_scope("catalog:read") is True
    assert calc_def.requires_scope("admin:write") is False


def test_registry_namespaces_and_in_namespace() -> None:
    """FrozenCapabilityRegistry reports active namespaces and filters by namespace."""
    registry = catalog.get_compiled_catalog()

    assert registry.namespaces == frozenset({"catalog"})

    catalog_caps = list(registry.in_namespace("catalog"))
    assert len(catalog_caps) == 4

    empty_caps = list(registry.in_namespace("nonexistent"))
    assert len(empty_caps) == 0


def test_registry_with_effect_filter() -> None:
    """FrozenCapabilityRegistry filters capabilities by declared effect."""
    registry = catalog.get_compiled_catalog()

    read_caps = list(registry.with_effect(StandardEffect.READ))
    assert len(read_caps) == 4

    # Test filtering with string effect
    read_caps_str = list(registry.with_effect("read"))
    assert len(read_caps_str) == 4

    destructive_caps = list(registry.with_effect(StandardEffect.DESTRUCTIVE))
    assert len(destructive_caps) == 0


def test_registry_mapping_protocol() -> None:
    """FrozenCapabilityRegistry satisfies collections.abc.Mapping protocol."""
    registry = catalog.get_compiled_catalog()

    assert len(registry) == 4
    assert "catalog.get_product" in registry
    assert CapabilityId("catalog", "get_product") in registry
    assert "catalog.fake" not in registry

    # get() behavior
    assert registry.get("catalog.get_product") is not None
    assert registry.get("catalog.fake") is None
    assert registry.get("catalog.fake", "fallback") == "fallback"

    # Keys, values, items
    keys = list(registry.keys())
    assert keys == [
        CapabilityId("catalog", "get_product"),
        CapabilityId("catalog", "list_products"),
        CapabilityId("catalog", "calculate_price"),
        CapabilityId("catalog", "check_warehouse_availability"),
    ]
    assert len(list(registry.values())) == 4
    assert len(list(registry.items())) == 4
