"""Base entity for Proliphix Plus."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ProliphixDataUpdateCoordinator
from .helpers import is_heat_only
from .models import ProliphixData


class ProliphixEntity(CoordinatorEntity[ProliphixDataUpdateCoordinator]):
    """Base class for Proliphix entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ProliphixDataUpdateCoordinator,
    ) -> None:
        """Initialize entity."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._entry_id = coordinator.config_entry.entry_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        data = self.coordinator.data
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name=data.name if data else "Proliphix Thermostat",
            manufacturer="Proliphix",
            model=data.model_name if data else None,
            sw_version=data.dev_app if data else None,
            hw_version=data.dev_rev if data else None,
        )

    @property
    def heat_only(self) -> bool:
        """Return True when cool and fan controls should be ignored."""
        return is_heat_only(self.coordinator.config_entry)

    @property
    def data(self) -> ProliphixData:
        """Return current thermostat data."""
        assert self.coordinator.data is not None
        return self.coordinator.data
