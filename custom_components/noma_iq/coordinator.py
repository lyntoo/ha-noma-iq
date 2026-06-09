"""DataUpdateCoordinator for Noma iQ."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NomaCantConnect, NomaIQApi
from .const import DOMAIN, POLL_INTERVAL

_LOGGER = logging.getLogger(__name__)

type NomaIQConfigEntry = ConfigEntry[NomaIQCoordinator]


class NomaIQCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator polling Ayla API for AC state."""

    config_entry: NomaIQConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api: NomaIQApi, dsn: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=POLL_INTERVAL),
        )
        self.api = api
        self.dsn = dsn
        self.entry = entry

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.get_properties(self.dsn)
        except NomaCantConnect as err:
            raise UpdateFailed(f"Cannot connect to Ayla API: {err}") from err
