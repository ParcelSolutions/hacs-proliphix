"""Tests for Proliphix models."""

from custom_components.proliphix_plus.models import (
    ProliphixData,
    decidegrees_to_celsius,
    decidegrees_to_fahrenheit,
    fahrenheit_to_decidegrees,
    flatten_response,
    int_or_none,
    oid_key,
)


def test_oid_key() -> None:
    """Test OID key conversion."""
    assert oid_key("4.1.13") == "OID4_1_13"


def test_flatten_response() -> None:
    """Test response flattening."""
    parsed = {"OID4.1.13": ["720"], "OID4.1.5": ["700", "680"]}
    flat = flatten_response(parsed)
    assert flat["OID4_1_13"] == "720"
    assert flat["OID4_1_5"] == "680"


def test_decidegrees_to_fahrenheit() -> None:
    """Test temperature conversion from decidegrees."""
    # 720 decidegrees = 72.0 F
    assert decidegrees_to_fahrenheit("720") == 72.0


def test_decidegrees_to_celsius() -> None:
    """Test temperature conversion to Celsius."""
    # 720 decidegrees = 72F = 22.2C
    assert decidegrees_to_celsius("720") == 22.2


def test_fahrenheit_to_decidegrees() -> None:
    """Test Fahrenheit to decidegrees."""
    assert fahrenheit_to_decidegrees(72.0) == 720


def test_int_or_none() -> None:
    """Test int parsing."""
    assert int_or_none("3") == 3
    assert int_or_none("") is None
    assert int_or_none(None) is None


def test_proliphix_data_properties() -> None:
    """Test ProliphixData property accessors."""
    raw = {
        "OID1_2": "Living Room",
        "OID1_10_9": "Home",
        "OID2_7_1": "NT10e",
        "OID4_1_13": "720",
        "OID4_1_5": "700",
        "OID4_1_11": "1",
        "OID4_1_1": "2",
        "OID4_1_2": "3",
    }
    data = ProliphixData.from_raw(raw)
    assert data.name == "Home:Living Room"
    assert data.average_temp == 72.0
    assert data.setback_heat == 70.0
    assert data.current_class == 1
    assert data.hvac_mode == 2
    assert data.hvac_state == 3
