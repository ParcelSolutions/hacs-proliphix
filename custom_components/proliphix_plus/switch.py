"""Switch platform for Proliphix Plus."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    FAN_STATE_CIRCULATE,
    HOLD_OFF,
    HOLD_PERMANENT,
    HOLD_TEMPORARY,
)
from .coordinator import ProliphixDataUpdateCoordinator
from .entity import ProliphixEntity
from .helpers import is_heat_only
from .models import ProliphixData


@dataclass(frozen=True)
class ProliphixSwitchDescription:
    """Description for a Proliphix switch."""

    key: str
    translation_key: str
    is_on_fn: Callable[[ProliphixData], bool | None]
    turn_on_fn: Callable[[ProliphixDataUpdateCoordinator], Coroutine[Any, Any, None]]
    turn_off_fn: Callable[[ProliphixDataUpdateCoordinator], Coroutine[Any, Any, None]]


async def _turn_on_vacation(coordinator: ProliphixDataUpdateCoordinator) -> None:
    """Enable vacation with current preset temps or defaults."""
    data = coordinator.data
    heat = data.get_preset_temp("vacation", heat=True) or 60.0
    import time

    now = int(time.time())
    if is_heat_only(coordinator.config_entry):
        await coordinator.client.set_vacation(now, now + 86400 * 7, heat, cool=None)
    else:
        cool = data.get_preset_temp("vacation", heat=False) or 85.0
        await coordinator.client.set_vacation(now, now + 86400 * 7, heat, cool)
    await coordinator.async_request_refresh()


async def _turn_off_vacation(coordinator: ProliphixDataUpdateCoordinator) -> None:
    await coordinator.client.clear_vacation()
    await coordinator.async_request_refresh()


async def _turn_on_hold(coordinator: ProliphixDataUpdateCoordinator) -> None:
    await coordinator.client.set_hold(HOLD_PERMANENT)
    await coordinator.async_request_refresh()


async def _turn_off_hold(coordinator: ProliphixDataUpdateCoordinator) -> None:
    await coordinator.client.resume_schedule()
    await coordinator.async_request_refresh()


async def _turn_on_temp_hold(coordinator: ProliphixDataUpdateCoordinator) -> None:
    await coordinator.client.set_hold(HOLD_TEMPORARY)
    await coordinator.async_request_refresh()


async def _turn_off_temp_hold(coordinator: ProliphixDataUpdateCoordinator) -> None:
    await coordinator.client.resume_schedule()
    await coordinator.async_request_refresh()


async def _turn_on_fan_circulate(
    coordinator: ProliphixDataUpdateCoordinator,
) -> None:
    await coordinator.client.set_fan_mode(FAN_STATE_CIRCULATE)
    await coordinator.async_request_refresh()


async def _turn_off_fan_circulate(
    coordinator: ProliphixDataUpdateCoordinator,
) -> None:
    from .const import FAN_STATE_AUTO

    await coordinator.client.set_fan_mode(FAN_STATE_AUTO)
    await coordinator.async_request_refresh()


async def _turn_on_schedule(coordinator: ProliphixDataUpdateCoordinator) -> None:
    await coordinator.client.resume_schedule()
    await coordinator.async_request_refresh()


async def _turn_off_schedule(coordinator: ProliphixDataUpdateCoordinator) -> None:
    await coordinator.client.set_hold(HOLD_PERMANENT)
    await coordinator.async_request_refresh()


SWITCHES: tuple[ProliphixSwitchDescription, ...] = (
    ProliphixSwitchDescription(
        key="schedule_enabled",
        translation_key="schedule_enabled",
        is_on_fn=lambda d: (
            d.hold_state == HOLD_OFF if d.hold_state is not None else None
        ),
        turn_on_fn=_turn_on_schedule,
        turn_off_fn=_turn_off_schedule,
    ),
    ProliphixSwitchDescription(
        key="vacation_enabled",
        translation_key="vacation_enabled",
        is_on_fn=lambda d: (
            bool(d.vacation_state) if d.vacation_state is not None else None
        ),
        turn_on_fn=_turn_on_vacation,
        turn_off_fn=_turn_off_vacation,
    ),
    ProliphixSwitchDescription(
        key="hold_enabled",
        translation_key="hold_enabled",
        is_on_fn=lambda d: (
            d.hold_state == HOLD_PERMANENT if d.hold_state is not None else None
        ),
        turn_on_fn=_turn_on_hold,
        turn_off_fn=_turn_off_hold,
    ),
    ProliphixSwitchDescription(
        key="fan_circulate",
        translation_key="fan_circulate",
        is_on_fn=lambda d: (
            d.fan_state == FAN_STATE_CIRCULATE if d.fan_state is not None else None
        ),
        turn_on_fn=_turn_on_fan_circulate,
        turn_off_fn=_turn_off_fan_circulate,
    ),
    ProliphixSwitchDescription(
        key="temporary_hold",
        translation_key="temporary_hold",
        is_on_fn=lambda d: (
            d.hold_state == HOLD_TEMPORARY if d.hold_state is not None else None
        ),
        turn_on_fn=_turn_on_temp_hold,
        turn_off_fn=_turn_off_temp_hold,
    ),
)

HEAT_ONLY_EXCLUDED_SWITCHES = frozenset({"fan_circulate"})


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Proliphix switches from config entry."""
    coordinator: ProliphixDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    heat_only = is_heat_only(entry)
    descriptions = [
        description
        for description in SWITCHES
        if not (heat_only and description.key in HEAT_ONLY_EXCLUDED_SWITCHES)
    ]
    async_add_entities(
        ProliphixSwitchEntity(coordinator, description) for description in descriptions
    )


class ProliphixSwitchEntity(ProliphixEntity, SwitchEntity):
    """Representation of a Proliphix switch."""

    entity_description: ProliphixSwitchDescription

    def __init__(
        self,
        coordinator: ProliphixDataUpdateCoordinator,
        description: ProliphixSwitchDescription,
    ) -> None:
        """Initialize switch."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._entry_id}_{description.key}"
        self._attr_translation_key = description.translation_key

    @property
    def is_on(self) -> bool | None:
        """Return switch state."""
        return self.entity_description.is_on_fn(self.data)

    @property
    def available(self) -> bool:
        """Return availability."""
        state = self.is_on
        if state is None:
            return False
        return super().available

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn switch on."""
        await self.entity_description.turn_on_fn(self.coordinator)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn switch off."""
        await self.entity_description.turn_off_fn(self.coordinator)
