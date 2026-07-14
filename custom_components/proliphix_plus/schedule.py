"""Schedule management for Proliphix Plus (v1.1 stub).

This module will provide:
- Parse/serialize full weekly schedules from OID data
- Upload/download schedule via HA services
- Backup and restore schedule configurations

See PDP API R1.11 section 4.4 for schedule OID structure.
"""

from __future__ import annotations

from typing import Any

from homeassistant.exceptions import HomeAssistantError

from .coordinator import ProliphixDataUpdateCoordinator


async def async_upload_schedule(
    coordinator: ProliphixDataUpdateCoordinator,
    schedule_data: str | None,
) -> None:
    """Upload a schedule to the thermostat.

    Planned for v1.1 — raises until full schedule editor is implemented.
    """
    raise HomeAssistantError(
        "Schedule upload is not yet implemented (planned for v1.1)"
    )


async def async_download_schedule(
    coordinator: ProliphixDataUpdateCoordinator,
) -> dict[str, Any]:
    """Download the current schedule from the thermostat.

    Planned for v1.1 — raises until full schedule parser is implemented.
    """
    raise HomeAssistantError(
        "Schedule download is not yet implemented (planned for v1.1)"
    )
