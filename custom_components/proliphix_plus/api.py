"""Async Proliphix API client."""

from __future__ import annotations

import asyncio
import logging
from typing import Any
from urllib.parse import parse_qs, urlencode

import aiohttp
from homeassistant.util import dt as dt_util

from .const import (
    CLASS_AWAY,
    CLASS_HOME,
    CLASS_SLEEP,
    HOLD_OFF,
    MAX_ATTEMPTS,
    POLL_OIDS,
    RETRY_DELAY,
    TIMEOUT,
    WEEKLY_SCHEDULE_OIDS,
)
from .models import (
    ProliphixData,
    fahrenheit_to_decidegrees,
    flatten_response,
    oid_form_key,
)

_LOGGER = logging.getLogger(__name__)


class ProliphixAuthError(Exception):
    """Authentication failed."""


class ProliphixConnectionError(Exception):
    """Connection to thermostat failed."""


class ProliphixClient:
    """Async HTTP client for Proliphix OID API."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize client."""
        self._host = host.rstrip("/")
        if not self._host.startswith("http"):
            self._host = f"http://{self._host}"
        self._username = username
        self._password = password
        self._session = session
        self._auth = aiohttp.BasicAuth(username, password)

    @property
    def host(self) -> str:
        """Return configured host."""
        return self._host

    async def communicate(
        self,
        endpoint: str,
        oids: dict[str, Any],
    ) -> tuple[int, dict[str, str]]:
        """POST form data to /get or /pdp. Returns (http_code, parsed response)."""
        url = f"{self._host}/{endpoint}"
        body = urlencode(oids)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        last_code = 0
        response_text = ""

        for attempt in range(1, MAX_ATTEMPTS + 1):
            if attempt > 1:
                await asyncio.sleep(RETRY_DELAY)
            try:
                timeout = aiohttp.ClientTimeout(total=TIMEOUT)
                async with self._session.post(
                    url,
                    data=body,
                    headers=headers,
                    auth=self._auth,
                    timeout=timeout,
                ) as response:
                    last_code = response.status
                    response_text = await response.text()
            except (TimeoutError, aiohttp.ClientError) as err:
                _LOGGER.debug("Attempt %d failed: %s", attempt, err)
                last_code = 0
                response_text = ""
                continue

            if last_code == 200:
                break

        if last_code == 401:
            raise ProliphixAuthError("Invalid username or password")
        if last_code == 0:
            raise ProliphixConnectionError("Could not connect to thermostat")

        parsed = parse_qs(response_text, keep_blank_values=True)
        flat = flatten_response(parsed)
        return last_code, flat

    async def read_oids(self, oids: list[str]) -> dict[str, str]:
        """Read one or more OIDs."""
        payload = {oid_form_key(oid): "" for oid in oids}
        payload["submit"] = "Submit"
        _code, raw = await self.communicate("get", payload)
        return raw

    async def write_oids(self, oids: dict[str, Any]) -> dict[str, str]:
        """Write one or more OIDs."""
        payload = {oid_form_key(k): v for k, v in oids.items()}
        payload["submit"] = "Submit"
        _code, raw = await self.communicate("pdp", payload)
        return raw

    async def get_state(self) -> ProliphixData:
        """Poll all standard OIDs and return typed state."""
        raw = await self.read_oids(POLL_OIDS)
        return ProliphixData.from_raw(raw)

    def clock_value(self) -> int:
        """Compute OID 2.5.1 clock value for current HA timezone."""
        now = dt_util.now()
        offset = now.utcoffset()
        if offset is None:
            return int(now.timestamp())
        # Proliphix stores local time as UTC epoch + UTC offset
        return int(now.timestamp()) + int(offset.total_seconds())

    async def sync_time(self) -> None:
        """Sync thermostat clock with Home Assistant."""
        await self.write_oids({"2.5.1": self.clock_value()})

    async def set_time(self, timestamp: int) -> None:
        """Set thermostat clock to a specific epoch timestamp."""
        await self.write_oids({"2.5.1": timestamp})

    async def set_preset(self, class_value: int) -> None:
        """Set weekly schedule class and current class."""
        payload: dict[str, Any] = {
            oid: str(class_value) for oid in WEEKLY_SCHEDULE_OIDS
        }
        payload["2.5.1"] = self.clock_value()
        payload["4.1.11"] = class_value
        payload["4.1.9"] = "1"
        await self.write_oids(payload)
        # Brief pause then verify
        await asyncio.sleep(1)

    async def set_home(self) -> None:
        """Activate home preset."""
        await self.set_preset(CLASS_HOME)

    async def set_away(self) -> None:
        """Activate away preset."""
        await self.set_preset(CLASS_AWAY)

    async def set_sleep(self) -> None:
        """Activate sleep preset."""
        await self.set_preset(CLASS_SLEEP)

    async def resume_schedule(self) -> None:
        """Resume programmed schedule (clear hold)."""
        await self.write_oids({"4.1.7": HOLD_OFF, "4.1.9": "1"})

    async def set_hold(self, hold_type: int) -> None:
        """Set hold state (temporary or permanent)."""
        await self.write_oids({"4.1.7": hold_type, "4.1.9": "1"})

    async def set_temperature(self, heat: float | None, cool: float | None) -> None:
        """Set heat and/or cool setback temperatures."""
        oids: dict[str, Any] = {}
        if heat is not None:
            oids["4.1.5"] = fahrenheit_to_decidegrees(heat)
        if cool is not None:
            oids["4.1.6"] = fahrenheit_to_decidegrees(cool)
        if oids:
            oids["4.1.9"] = "1"
            await self.write_oids(oids)

    async def set_hvac_mode(self, mode: int) -> None:
        """Set HVAC mode."""
        await self.write_oids({"4.1.1": mode, "4.1.9": "1"})

    async def set_fan_mode(self, mode: int) -> None:
        """Set fan mode."""
        await self.write_oids({"4.1.4": mode, "4.1.9": "1"})

    async def set_vacation(
        self,
        start: int,
        end: int,
        heat: float,
        cool: float | None = None,
    ) -> None:
        """Enable vacation mode with dates and setpoints."""
        oids: dict[str, Any] = {
            "4.4.1.2.1": start,
            "4.4.1.2.2": end,
            "4.4.1.1.4.1": fahrenheit_to_decidegrees(heat),
            "4.1.10": 1,
            "4.1.9": "1",
        }
        if cool is not None:
            oids["4.4.1.1.4.2"] = fahrenheit_to_decidegrees(cool)
        await self.write_oids(oids)

    async def clear_vacation(self) -> None:
        """Disable vacation mode."""
        await self.write_oids({"4.1.10": 0, "4.1.9": "1"})

    async def set_preset_temperature(
        self, preset: str, heat: float | None, cool: float | None
    ) -> None:
        """Set preset heat/cool setback temperatures."""
        from .const import PRESET_TEMP_OIDS

        if preset not in PRESET_TEMP_OIDS:
            raise ValueError(f"Unknown preset: {preset}")
        heat_oid, cool_oid = PRESET_TEMP_OIDS[preset]
        oids: dict[str, Any] = {"4.1.9": "1"}
        if heat is not None:
            oids[heat_oid] = fahrenheit_to_decidegrees(heat)
        if cool is not None:
            oids[cool_oid] = fahrenheit_to_decidegrees(cool)
        await self.write_oids(oids)

    async def reboot(self) -> None:
        """Reboot the thermostat."""
        await self.write_oids({"2.2.1": 1})

    async def read_oid(self, oid: str) -> str | None:
        """Read a single OID by short id."""
        raw = await self.read_oids([oid])
        from .models import oid_key

        return raw.get(oid_key(oid))

    async def write_oid(self, oid: str, value: Any) -> None:
        """Write a single OID by short id."""
        await self.write_oids({oid: value})

    async def async_close(self) -> None:
        """Close is a no-op; session owned by HA."""
        return
