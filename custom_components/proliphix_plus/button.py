"""Button platform for Proliphix Plus."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ProliphixDataUpdateCoordinator
from .entity import ProliphixEntity


@dataclass(frozen=True)
class ProliphixButtonDescription:
    """Description for a Proliphix button."""

    key: str
    translation_key: str
    press_fn: Callable[[ProliphixDataUpdateCoordinator], Coroutine[Any, Any, None]]


async def _press_sync_time(coordinator: ProliphixDataUpdateCoordinator) -> None:
    await coordinator.async_sync_time()


async def _press_resume_schedule(coordinator: ProliphixDataUpdateCoordinator) -> None:
    await coordinator.client.resume_schedule()
    await coordinator.async_request_refresh()


async def _press_refresh(coordinator: ProliphixDataUpdateCoordinator) -> None:
    await coordinator.async_request_refresh()


async def _press_reboot(coordinator: ProliphixDataUpdateCoordinator) -> None:
    await coordinator.client.reboot()


async def _press_download_diagnostics(
    coordinator: ProliphixDataUpdateCoordinator,
) -> None:
    """Trigger refresh to update diagnostics data."""
    await coordinator.async_request_refresh()


BUTTONS: tuple[ProliphixButtonDescription, ...] = (
    ProliphixButtonDescription(
        key="sync_time",
        translation_key="sync_time",
        press_fn=_press_sync_time,
    ),
    ProliphixButtonDescription(
        key="resume_schedule",
        translation_key="resume_schedule",
        press_fn=_press_resume_schedule,
    ),
    ProliphixButtonDescription(
        key="refresh_data",
        translation_key="refresh_data",
        press_fn=_press_refresh,
    ),
    ProliphixButtonDescription(
        key="reboot_thermostat",
        translation_key="reboot_thermostat",
        press_fn=_press_reboot,
    ),
    ProliphixButtonDescription(
        key="download_diagnostics",
        translation_key="download_diagnostics",
        press_fn=_press_download_diagnostics,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Proliphix buttons from config entry."""
    coordinator: ProliphixDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ProliphixButtonEntity(coordinator, description) for description in BUTTONS
    )


class ProliphixButtonEntity(ProliphixEntity, ButtonEntity):
    """Representation of a Proliphix button."""

    entity_description: ProliphixButtonDescription

    def __init__(
        self,
        coordinator: ProliphixDataUpdateCoordinator,
        description: ProliphixButtonDescription,
    ) -> None:
        """Initialize button."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._entry_id}_{description.key}"
        self._attr_translation_key = description.translation_key

    async def async_press(self) -> None:
        """Handle button press."""
        await self.entity_description.press_fn(self.coordinator)
