"""Climate entity for Noma iQ AC."""

from __future__ import annotations

import asyncio
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MED,
    MODE_COOL,
    MODE_DRY,
    MODE_FAN,
    PROP_AMBIENT_TEMP,
    PROP_FAN_SPEED,
    PROP_FAN_SPEED_STATUS,
    PROP_MODE,
    PROP_MODE_STATUS,
    PROP_NIGHT_MODE,
    PROP_POWER,
    PROP_SWING,
    PROP_TARGET_TEMP,
    PROP_TEMP_UNIT,
)
from .coordinator import NomaIQConfigEntry, NomaIQCoordinator

HA_TO_NOMA_MODE = {
    HVACMode.COOL: MODE_COOL,
    HVACMode.DRY: MODE_DRY,
    HVACMode.FAN_ONLY: MODE_FAN,
}
NOMA_TO_HA_MODE = {v: k for k, v in HA_TO_NOMA_MODE.items()}

HA_TO_NOMA_FAN = {
    "auto": FAN_AUTO,
    "low": FAN_LOW,
    "medium": FAN_MED,
    "high": FAN_HIGH,
}
NOMA_TO_HA_FAN = {v: k for k, v in HA_TO_NOMA_FAN.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NomaIQConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: NomaIQCoordinator = entry.runtime_data
    async_add_entities([NomaIQClimate(coordinator, entry)])


class NomaIQClimate(CoordinatorEntity[NomaIQCoordinator], ClimateEntity):
    """Noma iQ climate entity."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.DRY, HVACMode.FAN_ONLY]
    _attr_fan_modes = ["auto", "low", "medium", "high"]
    _attr_swing_modes = ["off", "on"]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.SWING_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_min_temp = 16
    _attr_max_temp = 32
    _attr_target_temperature_step = 1

    def __init__(self, coordinator: NomaIQCoordinator, entry: NomaIQConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.dsn
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.dsn)},
            "name": entry.title,
            "manufacturer": "Noma / Canadian Tire",
            "model": entry.data.get("model", "AC"),
        }

    @property
    def _props(self) -> dict:
        return self.coordinator.data or {}

    @property
    def temperature_unit(self) -> str:
        unit = self._props.get(PROP_TEMP_UNIT, "C")
        return UnitOfTemperature.FAHRENHEIT if unit == "F" else UnitOfTemperature.CELSIUS

    @property
    def hvac_mode(self) -> HVACMode:
        # PROP_MODE_STATUS is device-reported actual state.
        # PROP_POWER/PROP_MODE are last commanded values — stale if command failed.
        mode_status = self._props.get(PROP_MODE_STATUS)
        if mode_status in NOMA_TO_HA_MODE:
            # Device reports an active mode → it is running regardless of commanded power.
            return NOMA_TO_HA_MODE[mode_status]
        # mode_status absent or unknown → fall back to commanded power state.
        if str(self._props.get(PROP_POWER, "0")) == "0":
            return HVACMode.OFF
        return NOMA_TO_HA_MODE.get(self._props.get(PROP_MODE, MODE_COOL), HVACMode.COOL)

    @property
    def current_temperature(self) -> float | None:
        val = self._props.get(PROP_AMBIENT_TEMP)
        return float(val) if val is not None else None

    @property
    def target_temperature(self) -> float | None:
        val = self._props.get(PROP_TARGET_TEMP)
        return float(val) if val is not None else None

    @property
    def fan_mode(self) -> str:
        # Prefer fan_speed_status (device-reported) over last commanded fan_speed.
        noma_fan = (
            self._props.get(PROP_FAN_SPEED_STATUS)
            or self._props.get(PROP_FAN_SPEED, FAN_AUTO)
        )
        return NOMA_TO_HA_FAN.get(noma_fan, "auto")

    @property
    def swing_mode(self) -> str:
        return "on" if str(self._props.get(PROP_SWING, "0")) == "1" else "off"

    def _schedule_confirm_refresh(self) -> None:
        """Schedule a follow-up poll 10 s after a command.

        Ayla may take a few seconds to relay the command to the device and
        receive the device's status report back.  The immediate refresh after
        set_property usually returns the optimistic commanded value; this
        delayed one captures the confirmed device state.
        """
        async def _delayed() -> None:
            await asyncio.sleep(10)
            await self.coordinator.async_request_refresh()

        self.hass.async_create_task(_delayed())

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.api.set_property(self.coordinator.dsn, PROP_POWER, "0")
        else:
            noma_mode = HA_TO_NOMA_MODE[hvac_mode]
            await self.coordinator.api.set_property(self.coordinator.dsn, PROP_POWER, "1")
            await self.coordinator.api.set_property(self.coordinator.dsn, PROP_MODE, noma_mode)
        await self.coordinator.async_request_refresh()
        self._schedule_confirm_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is not None:
            await self.coordinator.api.set_property(
                self.coordinator.dsn, PROP_TARGET_TEMP, int(temp)
            )
            await self.coordinator.async_request_refresh()
            self._schedule_confirm_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        noma_fan = HA_TO_NOMA_FAN.get(fan_mode, FAN_AUTO)
        await self.coordinator.api.set_property(self.coordinator.dsn, PROP_FAN_SPEED, noma_fan)
        await self.coordinator.async_request_refresh()
        self._schedule_confirm_refresh()

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        value = "1" if swing_mode == "on" else "0"
        await self.coordinator.api.set_property(self.coordinator.dsn, PROP_SWING, value)
        await self.coordinator.async_request_refresh()
        self._schedule_confirm_refresh()

    async def async_turn_on(self) -> None:
        await self.async_set_hvac_mode(HVACMode.COOL)

    async def async_turn_off(self) -> None:
        await self.async_set_hvac_mode(HVACMode.OFF)
