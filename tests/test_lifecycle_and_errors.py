"""Tests for Agnara application lifecycle, registry immutability, and error handling."""

import pytest
from agnara import (
    Agnara,
    DefinitionError,
    DuplicateCapabilityError,
    FrozenCapabilityRegistry,
    RegistryFrozenError,
    UnknownCapabilityError,
)


def test_compile_lifecycle() -> None:
    """Application transitions from uncompiled to compiled, freezing the registry."""
    app = Agnara("store")
    assert app.is_compiled is False

    @app.capability
    def ping() -> str:
        return "pong"

    assert app.is_compiled is False
    assert len(app.capabilities) == 1

    registry = app.compile()
    assert app.is_compiled is True
    assert isinstance(registry, FrozenCapabilityRegistry)
    assert len(registry) == 1
    assert "store.ping" in registry


def test_post_compilation_registration_forbidden() -> None:
    """Attempting to register capabilities after compilation raises RegistryFrozenError."""
    app = Agnara("orders")

    @app.capability
    def create_order() -> str:
        return "order-1"

    app.compile()
    assert app.is_compiled is True

    with pytest.raises(RegistryFrozenError) as exc_info:

        @app.capability
        def cancel_order() -> str:
            return "cancelled"

    assert "after the registry was frozen" in str(exc_info.value)


def test_duplicate_capability_registration_forbidden() -> None:
    """Registering two capabilities with the same logical id raises DuplicateCapabilityError."""
    app = Agnara("billing")

    @app.capability(name="invoice")
    def generate_invoice() -> str:
        return "inv-1"

    with pytest.raises(DuplicateCapabilityError) as exc_info:

        @app.capability(name="invoice")
        def create_invoice() -> str:
            return "inv-2"

    assert "billing.invoice is already registered" in str(exc_info.value)


def test_unknown_capability_lookup() -> None:
    """Looking up unregistered capability in FrozenCapabilityRegistry raises error."""
    app = Agnara("inventory")

    @app.capability
    def stock() -> int:
        return 10

    registry = app.compile()

    with pytest.raises(UnknownCapabilityError) as exc_info:
        _ = registry["inventory.missing_capability"]

    assert "no capability registered as 'inventory.missing_capability'" in str(exc_info.value)
    # UnknownCapabilityError inherits from KeyError
    assert issubclass(UnknownCapabilityError, KeyError)


def test_invalid_application_namespace() -> None:
    """Agnara application namespace must be a non-empty valid Python identifier."""
    # Empty string
    with pytest.raises(DefinitionError):
        Agnara("")

    # Non-identifier
    with pytest.raises(DefinitionError) as exc_info:
        Agnara("invalid-namespace-with-dashes")
    assert "must be a single Python identifier" in str(exc_info.value)


def test_invalid_capability_name() -> None:
    """Capability name must be a valid Python identifier or dotted identifier."""
    app = Agnara("sample")

    with pytest.raises(DefinitionError) as exc_info:

        @app.capability(name="has invalid spaces")
        def bad_func() -> None:
            pass

    assert "is not a valid Python identifier" in str(exc_info.value)


def test_non_callable_handler() -> None:
    """Passing a non-callable to app.capability raises DefinitionError."""
    app = Agnara("sample")

    with pytest.raises(DefinitionError) as exc_info:
        app.capability("not_a_function")

    assert "expects a callable" in str(exc_info.value)


def test_invalid_metadata_values() -> None:
    """Passing invalid risk, confirmation, or effects raises DefinitionError."""
    app = Agnara("sample")

    with pytest.raises(DefinitionError) as exc_info:

        @app.capability(risk="extreme")  # valid: low, medium, high, critical
        def op_risk() -> None:
            pass

    assert "invalid risk 'extreme'" in str(exc_info.value)

    with pytest.raises(DefinitionError) as exc_info:

        @app.capability(confirmation="maybe")  # valid: never, policy, required
        def op_conf() -> None:
            pass

    assert "invalid confirmation 'maybe'" in str(exc_info.value)
