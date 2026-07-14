"""Tests for Proliphix helpers."""

from unittest.mock import MagicMock

from homeassistant.components.climate import HVACMode
from homeassistant.config_entries import ConfigEntry

from custom_components.proliphix_plus.const import (
    CONF_HEAT_ONLY,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_OFF,
    HVAC_STATE_HEATING,
)
from custom_components.proliphix_plus.helpers import (
    get_target_temperature,
    heat_only_hvac_modes,
    is_heat_only,
    map_hvac_action,
    map_hvac_mode,
)
from custom_components.proliphix_plus.models import ProliphixData


def test_is_heat_only_default() -> None:
    """Heat-only is disabled by default."""
    entry = MagicMock(spec=ConfigEntry)
    entry.options = {}
    assert is_heat_only(entry) is False


def test_is_heat_only_enabled() -> None:
    """Heat-only reads from config entry options."""
    entry = MagicMock(spec=ConfigEntry)
    entry.options = {CONF_HEAT_ONLY: True}
    assert is_heat_only(entry) is True


def test_map_hvac_mode_heat_only() -> None:
    """Heat-only maps cool/auto device modes to heat."""
    assert map_hvac_mode(HVAC_MODE_COOL, heat_only=True) == HVACMode.HEAT
    assert map_hvac_mode(HVAC_MODE_AUTO, heat_only=True) == HVACMode.HEAT
    assert map_hvac_mode(HVAC_MODE_OFF, heat_only=True) == HVACMode.OFF


def test_map_hvac_mode_full_system() -> None:
    """Full-system mode preserves cool and auto."""
    assert map_hvac_mode(HVAC_MODE_COOL, heat_only=False) == HVACMode.COOL
    assert map_hvac_mode(HVAC_MODE_AUTO, heat_only=False) == HVACMode.HEAT_COOL


def test_map_hvac_action_heat_only_ignores_cooling() -> None:
    """Heat-only reports idle instead of cooling action."""
    assert map_hvac_action(HVAC_STATE_HEATING, heat_only=True) == "heating"
    assert map_hvac_action(HVAC_MODE_OFF, heat_only=True) == "off"


def test_heat_only_hvac_modes_list() -> None:
    """Heat-only exposes only off and heat."""
    assert heat_only_hvac_modes() == [HVACMode.OFF, HVACMode.HEAT]


def test_get_target_temperature_heat_only() -> None:
    """Heat-only returns the heat setback."""
    data = ProliphixData.from_raw(
        {
            "OID4_1_5": "700",
            "OID4_1_6": "780",
            "OID4_1_1": str(HVAC_MODE_COOL),
        }
    )
    assert get_target_temperature(data, heat_only=True) == 70.0


def test_get_target_temperature_cool_mode() -> None:
    """Cool mode returns the cool setback."""
    data = ProliphixData.from_raw(
        {
            "OID4_1_5": "700",
            "OID4_1_6": "780",
            "OID4_1_1": str(HVAC_MODE_COOL),
        }
    )
    assert get_target_temperature(data, heat_only=False) == 78.0


def test_get_target_temperature_auto_mode() -> None:
    """Auto mode falls back to whichever setback is available."""
    data = ProliphixData.from_raw(
        {
            "OID4_1_5": "700",
            "OID4_1_1": str(HVAC_MODE_AUTO),
        }
    )
    assert get_target_temperature(data, heat_only=False) == 70.0
