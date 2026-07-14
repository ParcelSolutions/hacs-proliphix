"""Diagnostics support for Proliphix Plus."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import DOMAIN, OIDS
from .coordinator import ProliphixDataUpdateCoordinator

TO_REDACT = {CONF_PASSWORD, CONF_USERNAME}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: ProliphixDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data

    diagnostics: dict[str, Any] = {
        "config_entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "options": dict(entry.options),
        "heat_only": bool(entry.options.get("heat_only")),
        "last_successful_sync": (
            coordinator.last_successful_sync.isoformat()
            if coordinator.last_successful_sync
            else None
        ),
        "last_error": coordinator.last_error,
        "supported_oids": OIDS,
    }

    if data:
        diagnostics["device"] = {
            "name": data.name,
            "model": data.model_name,
            "firmware": data.dev_app,
            "hardware_revision": data.dev_rev,
        }
        diagnostics["state"] = {
            "hvac_mode": data.hvac_mode,
            "hvac_state": data.hvac_state,
            "current_class": data.current_class,
            "hold_state": data.hold_state,
            "vacation_state": data.vacation_state,
            "average_temp": data.average_temp,
            "setback_heat": data.setback_heat,
            "setback_cool": data.setback_cool,
            "active_schedule": data.active_schedule,
        }
        diagnostics["raw_oids"] = data.raw

    return diagnostics
