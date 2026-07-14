"""Generic OID read/write helpers for Proliphix Plus (v1.2 foundation).

Provides thin wrappers around the API client for advanced OID access.
A full OID explorer UI is planned for v1.2.
"""

from __future__ import annotations

from typing import Any

from .api import ProliphixClient
from .coordinator import ProliphixDataUpdateCoordinator


def normalize_oid(oid: str) -> str:
    """Normalize OID string by stripping optional OID prefix."""
    oid = oid.strip()
    if oid.upper().startswith("OID"):
        oid = oid[3:]
    return oid.lstrip(".")


async def async_read_oid(client: ProliphixClient, oid: str) -> str | None:
    """Read a single OID value."""
    return await client.read_oid(normalize_oid(oid))


async def async_write_oid(
    coordinator: ProliphixDataUpdateCoordinator,
    oid: str,
    value: Any,
) -> None:
    """Write a single OID value and refresh coordinator."""
    await coordinator.async_write_oid(normalize_oid(oid), value)
