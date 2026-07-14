"""Sensor platform for Proliphix Plus."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CLASS_TO_PRESET, DOMAIN
from .coordinator import ProliphixDataUpdateCoordinator
from .entity import ProliphixEntity
from .helpers import get_target_temperature, is_heat_only
from .models import ProliphixData


@dataclass(frozen=True)
class ProliphixSensorDescription:
    """Description for a Proliphix sensor."""

    key: str
    translation_key: str
    value_fn: Callable[[ProliphixData], str | int | float | None]
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    native_unit: str | None = None


SENSORS: tuple[ProliphixSensorDescription, ...] = (
    ProliphixSensorDescription(
        key="temperature",
        translation_key="temperature",
        value_fn=lambda d: d.average_temp,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit=UnitOfTemperature.FAHRENHEIT,
    ),
    ProliphixSensorDescription(
        key="target_temperature",
        translation_key="target_temperature",
        value_fn=lambda d: d.setback_heat,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit=UnitOfTemperature.FAHRENHEIT,
    ),
    ProliphixSensorDescription(
        key="heat_setpoint",
        translation_key="heat_setpoint",
        value_fn=lambda d: d.setback_heat,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit=UnitOfTemperature.FAHRENHEIT,
    ),
    ProliphixSensorDescription(
        key="cool_setpoint",
        translation_key="cool_setpoint",
        value_fn=lambda d: d.setback_cool,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit=UnitOfTemperature.FAHRENHEIT,
    ),
    ProliphixSensorDescription(
        key="indoor_temperature",
        translation_key="indoor_temperature",
        value_fn=lambda d: d.average_temp,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit=UnitOfTemperature.FAHRENHEIT,
    ),
    ProliphixSensorDescription(
        key="outdoor_temperature",
        translation_key="outdoor_temperature",
        value_fn=lambda d: d.outdoor_temp,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit=UnitOfTemperature.FAHRENHEIT,
    ),
    ProliphixSensorDescription(
        key="humidity",
        translation_key="humidity",
        value_fn=lambda d: d.humidity,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit=PERCENTAGE,
    ),
    ProliphixSensorDescription(
        key="firmware_version",
        translation_key="firmware_version",
        value_fn=lambda d: d.dev_app,
    ),
    ProliphixSensorDescription(
        key="hardware_revision",
        translation_key="hardware_revision",
        value_fn=lambda d: d.dev_rev,
    ),
    ProliphixSensorDescription(
        key="thermostat_model",
        translation_key="thermostat_model",
        value_fn=lambda d: d.model_name,
    ),
    ProliphixSensorDescription(
        key="current_schedule",
        translation_key="current_schedule",
        value_fn=lambda d: d.active_schedule,
    ),
    ProliphixSensorDescription(
        key="current_program",
        translation_key="current_program",
        value_fn=lambda d: (
            CLASS_TO_PRESET.get(d.current_class) if d.current_class else None
        ),
    ),
    ProliphixSensorDescription(
        key="heat_runtime",
        translation_key="heat_runtime",
        value_fn=lambda d: d.heat_usage,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit=UnitOfTime.MINUTES,
    ),
    ProliphixSensorDescription(
        key="cool_runtime",
        translation_key="cool_runtime",
        value_fn=lambda d: d.cool_usage,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit=UnitOfTime.MINUTES,
    ),
    ProliphixSensorDescription(
        key="fan_runtime",
        translation_key="fan_runtime",
        value_fn=lambda d: d.fan_usage,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit=UnitOfTime.MINUTES,
    ),
    ProliphixSensorDescription(
        key="filter_hours",
        translation_key="filter_hours",
        value_fn=lambda d: d.filter_hours,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit=UnitOfTime.HOURS,
    ),
    ProliphixSensorDescription(
        key="uptime",
        translation_key="uptime",
        value_fn=lambda d: d.uptime,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit=UnitOfTime.SECONDS,
    ),
)

HEAT_ONLY_EXCLUDED_SENSORS = frozenset({"cool_runtime", "fan_runtime", "cool_setpoint"})


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Proliphix sensors from config entry."""
    coordinator: ProliphixDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    heat_only = is_heat_only(entry)
    descriptions = [
        description
        for description in SENSORS
        if not (heat_only and description.key in HEAT_ONLY_EXCLUDED_SENSORS)
    ]
    async_add_entities(
        ProliphixSensorEntity(coordinator, description) for description in descriptions
    )
    async_add_entities([ProliphixLastSyncSensor(coordinator)])


class ProliphixSensorEntity(ProliphixEntity, SensorEntity):
    """Representation of a Proliphix sensor."""

    entity_description: ProliphixSensorDescription

    def __init__(
        self,
        coordinator: ProliphixDataUpdateCoordinator,
        description: ProliphixSensorDescription,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._entry_id}_{description.key}"
        self._attr_translation_key = description.translation_key
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_native_unit_of_measurement = description.native_unit

    @property
    def native_value(self) -> str | int | float | None:
        """Return sensor value."""
        if self.entity_description.key == "target_temperature":
            return get_target_temperature(self.data, heat_only=self.heat_only)
        return self.entity_description.value_fn(self.data)

    @property
    def available(self) -> bool:
        """Return availability based on whether value exists."""
        value = self.native_value
        if value is None:
            return False
        return super().available


class ProliphixLastSyncSensor(ProliphixEntity, SensorEntity):
    """Sensor for last successful synchronization."""

    _attr_translation_key = "last_synchronization"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator: ProliphixDataUpdateCoordinator) -> None:
        """Initialize last sync sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._entry_id}_last_sync"

    @property
    def native_value(self) -> datetime | None:
        """Return last sync time."""
        return self.coordinator.last_successful_sync
