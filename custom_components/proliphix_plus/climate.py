"""Climate platform for Proliphix Plus."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_TENTHS, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CLASS_TO_PRESET,
    CLIMATE_PRESET_MODES,
    DOMAIN,
    FAN_STATE_AUTO,
    FAN_STATE_CIRCULATE,
    FAN_STATE_ON,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    HVAC_STATE_COOLING,
    HVAC_STATE_COOLING_2,
    HVAC_STATE_HEATING,
    HVAC_STATE_HEATING_2,
    HVAC_STATE_HEATING_3,
    HVAC_STATE_IDLE,
    PRESET_TO_CLASS,
)
from .coordinator import ProliphixDataUpdateCoordinator
from .entity import ProliphixEntity
from .helpers import (
    full_system_hvac_modes,
    get_target_temperature,
    heat_only_hvac_modes,
    map_hvac_mode,
)

PRESET_NONE = "none"

HA_TO_FAN = {
    "auto": FAN_STATE_AUTO,
    "on": FAN_STATE_ON,
    "circulate": FAN_STATE_CIRCULATE,
}

FAN_TO_HA = {v: k for k, v in HA_TO_FAN.items()}

HA_TO_HVAC = {
    HVACMode.OFF: HVAC_MODE_OFF,
    HVACMode.HEAT: HVAC_MODE_HEAT,
    HVACMode.COOL: HVAC_MODE_COOL,
    HVACMode.HEAT_COOL: HVAC_MODE_AUTO,
}

HVAC_TO_HA = {
    HVAC_MODE_OFF: HVACMode.OFF,
    HVAC_MODE_HEAT: HVACMode.HEAT,
    HVAC_MODE_COOL: HVACMode.COOL,
    HVAC_MODE_AUTO: HVACMode.HEAT_COOL,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Proliphix climate from config entry."""
    coordinator: ProliphixDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ProliphixClimateEntity(coordinator)])


class ProliphixClimateEntity(ProliphixEntity, ClimateEntity):
    """Representation of a Proliphix thermostat."""

    _attr_temperature_unit = UnitOfTemperature.FAHRENHEIT
    _attr_precision = PRECISION_TENTHS
    _attr_translation_key = "thermostat"

    def __init__(self, coordinator: ProliphixDataUpdateCoordinator) -> None:
        """Initialize climate entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._entry_id}_climate"

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Return supported features, omitting fan when heat-only."""
        features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.TURN_OFF
        )
        if not self.heat_only:
            features |= ClimateEntityFeature.FAN_MODE
        return features

    @property
    def current_temperature(self) -> float | None:
        """Return current temperature."""
        return self.data.average_temp

    @property
    def target_temperature(self) -> float | None:
        """Return target temperature based on active mode."""
        return get_target_temperature(self.data, heat_only=self.heat_only)

    @property
    def hvac_action(self) -> HVACAction:
        """Return current HVAC action."""
        state = self.data.hvac_state
        if self.heat_only:
            if state in (
                HVAC_STATE_HEATING,
                HVAC_STATE_HEATING_2,
                HVAC_STATE_HEATING_3,
            ):
                return HVACAction.HEATING
            if state == HVAC_MODE_OFF:
                return HVACAction.OFF
            return HVACAction.IDLE
        if state == HVAC_STATE_IDLE:
            return HVACAction.IDLE
        if state in (HVAC_STATE_HEATING, HVAC_STATE_HEATING_2, HVAC_STATE_HEATING_3):
            return HVACAction.HEATING
        if state in (HVAC_STATE_COOLING, HVAC_STATE_COOLING_2):
            return HVACAction.COOLING
        if state == HVAC_MODE_OFF:
            return HVACAction.OFF
        return HVACAction.IDLE

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        return map_hvac_mode(self.data.hvac_mode, heat_only=self.heat_only)

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return available HVAC modes."""
        if self.heat_only:
            return heat_only_hvac_modes()
        return full_system_hvac_modes()

    @property
    def fan_mode(self) -> str | None:
        """Return current fan mode."""
        if self.heat_only:
            return None
        state = self.data.fan_state
        if state is not None:
            return FAN_TO_HA.get(state)
        return None

    @property
    def fan_modes(self) -> list[str] | None:
        """Return available fan modes."""
        if self.heat_only:
            return None
        return list(HA_TO_FAN.keys())

    @property
    def preset_mode(self) -> str | None:
        """Return active day-class preset from weekly schedule or CurrentClass."""
        weekly = self.data.weekly_schedule_class
        if weekly is not None and weekly in CLASS_TO_PRESET:
            return CLASS_TO_PRESET[weekly]
        current = self.data.current_class
        if current is not None and current in CLASS_TO_PRESET:
            return CLASS_TO_PRESET[current]
        return PRESET_NONE

    @property
    def preset_modes(self) -> list[str] | None:
        """Return In/Out/Away day-class presets."""
        return list(CLIMATE_PRESET_MODES)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        attrs: dict[str, Any] = {"heat_only": self.heat_only}
        if not self.heat_only and self.data.fan_state is not None:
            attrs["fan_state_raw"] = self.data.fan_state
        if self.data.hold_state is not None:
            attrs["hold_state"] = self.data.hold_state
        if self.data.current_class is not None:
            attrs["current_class"] = self.data.current_class
        if self.data.setback_heat is not None:
            attrs["schedule_heat"] = self.data.setback_heat
        if not self.heat_only and self.data.setback_cool is not None:
            attrs["schedule_cool"] = self.data.setback_cool
        return attrs

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        if self.heat_only:
            await self.coordinator.client.set_temperature(temperature, None)
        else:
            mode = self.data.hvac_mode
            if mode == HVAC_MODE_COOL:
                await self.coordinator.client.set_temperature(None, temperature)
            elif mode == HVAC_MODE_HEAT:
                await self.coordinator.client.set_temperature(temperature, None)
            else:
                await self.coordinator.client.set_temperature(temperature, temperature)
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode."""
        if self.heat_only:
            if hvac_mode == HVACMode.OFF:
                await self.coordinator.client.set_hvac_mode(HVAC_MODE_OFF)
            elif hvac_mode == HVACMode.HEAT:
                await self.coordinator.client.set_hvac_mode(HVAC_MODE_HEAT)
            await self.coordinator.async_request_refresh()
            return
        mode = HA_TO_HVAC.get(hvac_mode)
        if mode is not None:
            await self.coordinator.client.set_hvac_mode(mode)
            await self.coordinator.async_request_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set fan mode."""
        if self.heat_only:
            return
        mode = HA_TO_FAN.get(fan_mode)
        if mode is not None:
            await self.coordinator.client.set_fan_mode(mode)
            await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set day class for the whole week, then refresh thermostat setpoints."""
        if preset_mode not in PRESET_TO_CLASS:
            return
        await self.coordinator.client.set_preset(PRESET_TO_CLASS[preset_mode])
        # Re-read OIDs so target temperature reflects the applied schedule.
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Turn on HVAC; heat-only uses heat, otherwise auto."""
        if self.heat_only:
            await self.coordinator.client.set_hvac_mode(HVAC_MODE_HEAT)
        else:
            await self.coordinator.client.set_hvac_mode(HVAC_MODE_AUTO)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn off HVAC."""
        await self.coordinator.client.set_hvac_mode(HVAC_MODE_OFF)
        await self.coordinator.async_request_refresh()
