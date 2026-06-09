"""Noma iQ integration."""

from __future__ import annotations

from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NomaCantConnect, NomaInvalidAuth, NomaIQApi
from .const import CONF_APP_ID, CONF_APP_SECRET
from .coordinator import NomaIQConfigEntry, NomaIQCoordinator

PLATFORMS = [Platform.CLIMATE]


async def async_setup_entry(hass: HomeAssistant, entry: NomaIQConfigEntry) -> bool:
    """Set up Noma iQ from a config entry."""
    api = NomaIQApi(
        async_get_clientsession(hass),
        entry.data[CONF_EMAIL],
        entry.data[CONF_PASSWORD],
        entry.data[CONF_APP_ID],
        entry.data[CONF_APP_SECRET],
    )

    try:
        await api.authenticate()
    except NomaInvalidAuth as err:
        raise ConfigEntryAuthFailed from err
    except NomaCantConnect as err:
        raise ConfigEntryNotReady from err

    dsn = entry.data["dsn"]
    coordinator = NomaIQCoordinator(hass, entry, api, dsn)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: NomaIQConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
