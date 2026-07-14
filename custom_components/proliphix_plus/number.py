"""Number platform for Proliphix Plus."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, PRESET_TEMP_OIDS
from .coordinator import ProliphixDataUpdateCoordinator
from .entity import ProliphixEntity
from .helpers import is_heat_only
from .models import ProliphixData


@dataclass(frozen=True)
class ProliphixNumberDescription:
    """Description for a Proliphix number entity."""

    key: str
    translation_key: str
    preset: str
    heat: bool
    value_fn: Callable[[ProliphixData], float | None]
    oid: str


def _make_numbers() -> tuple[ProliphixNumberDescription, ...]:
    """Build number descriptions for all preset heat/cool setpoints."""
    numbers: list[ProliphixNumberDescription] = []
    for preset, (heat_oid, cool_oid) in PRESET_TEMP_OIDS.items():
        numbers.append(
            ProliphixNumberDescription(
                key=f"{preset}_heat",
                translation_key=f"{preset}_heat",
                preset=preset,
                heat=True,
                value_fn=lambda d, p=preset: d.get_preset_temp(p, heat=True),
                oid=heat_oid,
            )
        )
        numbers.append(
            ProliphixNumberDescription(
                key=f"{preset}_cool",
                translation_key=f"{preset}_cool",
                preset=preset,
                heat=False,
                value_fn=lambda d, p=preset: d.get_preset_temp(p, heat=False),
                oid=cool_oid,
            )
        )
    return tuple(numbers)


NUMBERS = _make_numbers()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Proliphix number entities from config entry."""
    coordinator: ProliphixDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    heat_only = is_heat_only(entry)
    descriptions = [
        description
        for description in NUMBERS
        if not (heat_only and not description.heat)
    ]
    async_add_entities(
        ProliphixNumberEntity(coordinator, description) for description in descriptions
    )


class ProliphixNumberEntity(ProliphixEntity, NumberEntity):
    """Representation of a Proliphix preset temperature number."""

    entity_description: ProliphixNumberDescription

    _attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 40.0
    _attr_native_max_value = 99.0
    _attr_native_step = 0.5

    def __init__(
        self,
        coordinator: ProliphixDataUpdateCoordinator,
        description: ProliphixNumberDescription,
    ) -> None:
        """Initialize number entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._entry_id}_{description.key}"
        self._attr_translation_key = description.translation_key

    @property
    def native_value(self) -> float | None:
        """Return current value."""
        return self.entity_description.value_fn(self.data)

    @property
    def available(self) -> bool:
        """Return availability."""
        if self.native_value is None:
            return False
        return super().available

    async def async_set_native_value(self, value: float) -> None:
        """Set preset temperature."""
        desc = self.entity_description
        if desc.heat:
            await self.coordinator.client.set_preset_temperature(
                desc.preset, heat=value, cool=None
            )
        else:
            await self.coordinator.client.set_preset_temperature(
                desc.preset, heat=None, cool=value
            )
        await self.coordinator.async_request_refresh()
