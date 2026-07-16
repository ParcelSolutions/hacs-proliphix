"""Data update coordinator for Proliphix Plus."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    ProliphixAuthError,
    ProliphixClient,
    ProliphixConnectionError,
)
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, WEEKLY_SCHEDULE_OIDS
from .models import ProliphixData, oid_key

_LOGGER = logging.getLogger(__name__)


class ProliphixDataUpdateCoordinator(DataUpdateCoordinator[ProliphixData]):
    """Coordinator for Proliphix thermostat polling."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: ProliphixClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize coordinator."""
        self.client = client
        self.config_entry = entry
        options = getattr(entry, "options", None) or {}
        scan_interval = options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
        self.last_successful_sync: datetime | None = None
        self.last_error: str | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> ProliphixData:
        """Fetch data from thermostat."""
        try:
            data = await self.client.get_state()
        except ProliphixAuthError as err:
            self.last_error = str(err)
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except ProliphixConnectionError as err:
            self.last_error = str(err)
            raise UpdateFailed(f"Connection failed: {err}") from err
        except Exception as err:
            self.last_error = str(err)
            raise UpdateFailed(f"Unexpected error: {err}") from err

        self.last_successful_sync = datetime.now()
        self.last_error = None

        # Optional auto time sync if drift > 60 seconds
        options = getattr(self.config_entry, "options", None) or {}
        if options.get("auto_time_sync"):
            await self._maybe_sync_time(data)

        return data

    async def _maybe_sync_time(self, data: ProliphixData) -> None:
        """Sync clock if drift exceeds 60 seconds."""
        device_time = data.thermostat_time
        if device_time is None:
            return
        expected = self.client.clock_value()
        drift = abs(expected - device_time)
        if drift > 60:
            _LOGGER.info("Thermostat clock drifted by %d seconds, syncing", drift)
            try:
                await self.client.sync_time()
            except (ProliphixAuthError, ProliphixConnectionError) as err:
                _LOGGER.warning("Auto time sync failed: %s", err)

    def _apply_preset_locally(self, class_value: int) -> ProliphixData:
        """Update cached OID state so climate target updates without a full poll."""
        if self.data is None:
            return ProliphixData()
        raw = dict(self.data.raw)
        for oid in WEEKLY_SCHEDULE_OIDS:
            raw[oid_key(oid)] = str(class_value)
        raw[oid_key("4.1.11")] = str(class_value)
        # Resume schedule (not override) so target uses class period setpoints.
        raw[oid_key("4.1.9")] = "1"
        period_raw = raw.get(oid_key("4.1.12"), "0") or "0"
        try:
            period = int(period_raw)
        except ValueError:
            period = 0
        if period < 1 or period > 4:
            raw[oid_key("4.1.12")] = "1"
        return ProliphixData.from_raw(raw)

    async def async_set_preset(self, class_value: int) -> None:
        """Set day-class preset, update UI immediately, refresh in background."""
        await self.client.set_preset(class_value)
        self.async_set_updated_data(self._apply_preset_locally(class_value))
        self.hass.async_create_task(self.async_request_refresh())

    async def async_sync_time(self) -> None:
        """Sync thermostat time."""
        await self.client.sync_time()
        await self.async_request_refresh()

    async def async_write_oids(self, oids: dict[str, Any]) -> None:
        """Write OIDs and refresh."""
        await self.client.write_oids(oids)
        await self.async_request_refresh()

    async def async_read_oid(self, oid: str) -> str | None:
        """Read a single OID."""
        return await self.client.read_oid(oid)

    async def async_write_oid(self, oid: str, value: Any) -> None:
        """Write a single OID and refresh."""
        await self.client.write_oid(oid, value)
        await self.async_request_refresh()
