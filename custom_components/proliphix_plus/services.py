"""Services for Proliphix Plus."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er

from .const import (
    DOMAIN,
    SERVICE_CLEAR_VACATION,
    SERVICE_DOWNLOAD_SCHEDULE,
    SERVICE_READ_OID,
    SERVICE_REBOOT,
    SERVICE_REFRESH,
    SERVICE_RESUME_SCHEDULE,
    SERVICE_SET_AWAY,
    SERVICE_SET_HOME,
    SERVICE_SET_SLEEP,
    SERVICE_SET_TIME,
    SERVICE_SET_TIMEZONE,
    SERVICE_SET_VACATION,
    SERVICE_SYNC_TIME,
    SERVICE_UPLOAD_SCHEDULE,
    SERVICE_WRITE_OID,
)
from .coordinator import ProliphixDataUpdateCoordinator
from .helpers import is_heat_only
from .oid import async_read_oid, async_write_oid
from .schedule import async_download_schedule, async_upload_schedule

_LOGGER = logging.getLogger(__name__)

SERVICES_REGISTERED = False


def _get_coordinator(call: ServiceCall) -> ProliphixDataUpdateCoordinator:
    """Resolve coordinator from service call entity or single entry."""
    hass = call.hass
    entity_ids = call.data.get("entity_id")
    coordinators: dict[str, ProliphixDataUpdateCoordinator] = hass.data.get(DOMAIN, {})

    if entity_ids:
        if isinstance(entity_ids, str):
            entity_ids = [entity_ids]
        entity_registry = er.async_get(hass)
        for entity_id in entity_ids:
            if (
                (entity_entry := entity_registry.async_get(entity_id))
                and entity_entry.config_entry_id
            ):
                return _get_coordinator_for_entry(
                    hass, entity_entry.config_entry_id
                )
        raise HomeAssistantError(f"No coordinator found for entity {entity_ids}")

    if len(coordinators) == 1:
        return next(iter(coordinators.values()))
    if not coordinators:
        raise HomeAssistantError("No Proliphix Plus devices configured")
    raise HomeAssistantError(
        "entity_id is required when multiple thermostats are configured"
    )


def _get_coordinator_for_entry(
    hass: HomeAssistant, entry_id: str
) -> ProliphixDataUpdateCoordinator:
    """Get coordinator by config entry id."""
    coordinator = hass.data.get(DOMAIN, {}).get(entry_id)
    if coordinator is None:
        raise HomeAssistantError(f"No device for entry {entry_id}")
    return coordinator


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register Proliphix Plus services."""
    global SERVICES_REGISTERED  # noqa: PLW0603
    if SERVICES_REGISTERED:
        return

    async def handle_sync_time(call: ServiceCall) -> None:
        coordinator = _get_coordinator(call)
        await coordinator.async_sync_time()

    async def handle_set_time(call: ServiceCall) -> None:
        coordinator = _get_coordinator(call)
        timestamp = call.data["timestamp"]
        await coordinator.client.set_time(timestamp)
        await coordinator.async_request_refresh()

    async def handle_set_timezone(call: ServiceCall) -> None:
        coordinator = _get_coordinator(call)
        # Proliphix uses clock OID; sync applies HA timezone offset
        await coordinator.async_sync_time()

    async def handle_resume_schedule(call: ServiceCall) -> None:
        coordinator = _get_coordinator(call)
        await coordinator.client.resume_schedule()
        await coordinator.async_request_refresh()

    async def handle_set_home(call: ServiceCall) -> None:
        coordinator = _get_coordinator(call)
        await coordinator.client.set_home()
        await coordinator.async_request_refresh()

    async def handle_set_away(call: ServiceCall) -> None:
        coordinator = _get_coordinator(call)
        await coordinator.client.set_away()
        await coordinator.async_request_refresh()

    async def handle_set_sleep(call: ServiceCall) -> None:
        coordinator = _get_coordinator(call)
        await coordinator.client.set_sleep()
        await coordinator.async_request_refresh()

    async def handle_set_vacation(call: ServiceCall) -> None:
        coordinator = _get_coordinator(call)
        start = call.data["start"]
        end = call.data["end"]
        heat = call.data.get("heat", 60.0)
        if is_heat_only(coordinator.config_entry):
            cool = None
        else:
            cool = call.data.get("cool", 85.0)
        await coordinator.client.set_vacation(start, end, heat, cool)
        await coordinator.async_request_refresh()

    async def handle_clear_vacation(call: ServiceCall) -> None:
        coordinator = _get_coordinator(call)
        await coordinator.client.clear_vacation()
        await coordinator.async_request_refresh()

    async def handle_refresh(call: ServiceCall) -> None:
        coordinator = _get_coordinator(call)
        await coordinator.async_request_refresh()

    async def handle_reboot(call: ServiceCall) -> None:
        coordinator = _get_coordinator(call)
        await coordinator.client.reboot()

    async def handle_read_oid(call: ServiceCall) -> None:
        coordinator = _get_coordinator(call)
        oid = call.data["oid"]
        result = await async_read_oid(coordinator.client, oid)
        _LOGGER.info("OID %s = %s", oid, result)

    async def handle_write_oid(call: ServiceCall) -> None:
        coordinator = _get_coordinator(call)
        oid = call.data["oid"]
        value = call.data["value"]
        await async_write_oid(coordinator, oid, value)

    async def handle_upload_schedule(call: ServiceCall) -> None:
        coordinator = _get_coordinator(call)
        schedule_data = call.data.get("schedule")
        await async_upload_schedule(coordinator, schedule_data)

    async def handle_download_schedule(call: ServiceCall) -> None:
        coordinator = _get_coordinator(call)
        await async_download_schedule(coordinator)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SYNC_TIME,
        handle_sync_time,
        schema=vol.Schema({vol.Optional("entity_id"): cv.entity_ids}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_TIME,
        handle_set_time,
        schema=vol.Schema(
            {
                vol.Required("timestamp"): cv.positive_int,
                vol.Optional("entity_id"): cv.entity_ids,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_TIMEZONE,
        handle_set_timezone,
        schema=vol.Schema({vol.Optional("entity_id"): cv.entity_ids}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_RESUME_SCHEDULE,
        handle_resume_schedule,
        schema=vol.Schema({vol.Optional("entity_id"): cv.entity_ids}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_HOME,
        handle_set_home,
        schema=vol.Schema({vol.Optional("entity_id"): cv.entity_ids}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_AWAY,
        handle_set_away,
        schema=vol.Schema({vol.Optional("entity_id"): cv.entity_ids}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_SLEEP,
        handle_set_sleep,
        schema=vol.Schema({vol.Optional("entity_id"): cv.entity_ids}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_VACATION,
        handle_set_vacation,
        schema=vol.Schema(
            {
                vol.Required("start"): cv.positive_int,
                vol.Required("end"): cv.positive_int,
                vol.Optional("heat"): cv.positive_float,
                vol.Optional("cool"): cv.positive_float,
                vol.Optional("entity_id"): cv.entity_ids,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CLEAR_VACATION,
        handle_clear_vacation,
        schema=vol.Schema({vol.Optional("entity_id"): cv.entity_ids}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REFRESH,
        handle_refresh,
        schema=vol.Schema({vol.Optional("entity_id"): cv.entity_ids}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REBOOT,
        handle_reboot,
        schema=vol.Schema({vol.Optional("entity_id"): cv.entity_ids}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_READ_OID,
        handle_read_oid,
        schema=vol.Schema(
            {
                vol.Required("oid"): cv.string,
                vol.Optional("entity_id"): cv.entity_ids,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_WRITE_OID,
        handle_write_oid,
        schema=vol.Schema(
            {
                vol.Required("oid"): cv.string,
                vol.Required("value"): cv.string,
                vol.Optional("entity_id"): cv.entity_ids,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_UPLOAD_SCHEDULE,
        handle_upload_schedule,
        schema=vol.Schema(
            {
                vol.Optional("schedule"): cv.string,
                vol.Optional("entity_id"): cv.entity_ids,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_DOWNLOAD_SCHEDULE,
        handle_download_schedule,
        schema=vol.Schema({vol.Optional("entity_id"): cv.entity_ids}),
    )

    SERVICES_REGISTERED = True
