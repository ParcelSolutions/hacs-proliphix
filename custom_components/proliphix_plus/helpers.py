"""Shared helpers for Proliphix Plus."""

from __future__ import annotations

from homeassistant.components.climate import HVACMode
from homeassistant.config_entries import ConfigEntry

from .const import (
    CONF_HEAT_ONLY,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    HVAC_STATE_COOLING,
    HVAC_STATE_COOLING_2,
    HVAC_STATE_HEATING,
    HVAC_STATE_HEATING_2,
    HVAC_STATE_HEATING_3,
)
from .models import ProliphixData


def get_entry_options(entry: ConfigEntry) -> dict:
    """Return config entry options, defaulting to empty dict."""
    return getattr(entry, "options", None) or {}


def is_heat_only(entry: ConfigEntry) -> bool:
    """Return True when the install is configured for heat-only operation."""
    return bool(get_entry_options(entry).get(CONF_HEAT_ONLY, False))


def heat_only_hvac_modes() -> list[HVACMode]:
    """Return HVAC modes exposed in heat-only configuration."""
    return [HVACMode.OFF, HVACMode.HEAT]


def full_system_hvac_modes() -> list[HVACMode]:
    """Return HVAC modes exposed when cooling/fan are available."""
    return [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL, HVACMode.HEAT_COOL]


def map_hvac_mode(raw_mode: int | None, *, heat_only: bool) -> HVACMode:
    """Map Proliphix HVAC mode OID to Home Assistant climate mode."""
    if heat_only:
        if raw_mode in (HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_AUTO):
            return HVACMode.HEAT
        return HVACMode.OFF
    mapping = {
        HVAC_MODE_OFF: HVACMode.OFF,
        HVAC_MODE_HEAT: HVACMode.HEAT,
        HVAC_MODE_COOL: HVACMode.COOL,
        HVAC_MODE_AUTO: HVACMode.HEAT_COOL,
    }
    if raw_mode is None:
        return HVACMode.OFF
    return mapping.get(raw_mode, HVACMode.OFF)


def map_hvac_action(raw_state: int | None, *, heat_only: bool) -> str:
    """Map Proliphix HVAC state OID to a simplified action label."""
    if raw_state is None:
        return "idle"
    if heat_only:
        if raw_state in (
            HVAC_STATE_HEATING,
            HVAC_STATE_HEATING_2,
            HVAC_STATE_HEATING_3,
        ):
            return "heating"
        if raw_state == HVAC_MODE_OFF:
            return "off"
        return "idle"
    if raw_state in (HVAC_STATE_HEATING, HVAC_STATE_HEATING_2, HVAC_STATE_HEATING_3):
        return "heating"
    if raw_state in (HVAC_STATE_COOLING, HVAC_STATE_COOLING_2):
        return "cooling"
    if raw_state == HVAC_MODE_OFF:
        return "off"
    return "idle"


def get_target_temperature(data: ProliphixData, *, heat_only: bool) -> float | None:
    """Return the active target temperature based on HVAC mode."""
    if heat_only:
        return data.setback_heat
    mode = data.hvac_mode
    if mode == HVAC_MODE_COOL:
        return data.setback_cool
    if mode == HVAC_MODE_HEAT:
        return data.setback_heat
    return data.setback_heat or data.setback_cool
