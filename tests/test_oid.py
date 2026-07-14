"""Tests for Proliphix OID helpers."""

from custom_components.proliphix_plus.oid import normalize_oid


def test_normalize_oid() -> None:
    """Test OID normalization."""
    assert normalize_oid("4.1.13") == "4.1.13"
    assert normalize_oid("OID4.1.13") == "4.1.13"
    assert normalize_oid("oid4.1.13") == "4.1.13"
    assert normalize_oid("  OID6.1.3.2.0  ") == "6.1.3.2.0"
