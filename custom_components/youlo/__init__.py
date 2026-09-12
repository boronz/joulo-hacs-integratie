"""The Joulo integration."""
from __future__ import annotations

import logging
from datetime import timedelta
import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_API_KEY, API_CHARGERS, API_ENERGY, API_ERE_POSITION

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Joulo from a config entry."""
    api_key = entry.data[CONF_API_KEY]

    async def async_update_data():
        """Fetch data from Joulo REST API."""
        headers = {"Authorization": api_key}
        data = {}
        async with aiohttp.ClientSession() as session:
            try:
                # 1. Chargers
                async with session.get(API_CHARGERS, headers=headers) as resp:
                    if resp.status == 200:
                        data["chargers"] = await resp.json()
                # 2. Energy
                async with session.get(API_ENERGY, headers=headers) as resp:
                    if resp.status == 200:
                        data["energy"] = await resp.json()
                # 3. ERE Position
                async with session.get(API_ERE_POSITION, headers=headers) as resp:
                    if resp.status == 200:
                        data["ere"] = await resp.json()
            except Exception as err:
                raise UpdateFailed(f"Error communicating with Joulo API: {err}") from err
        return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Joulo API",
        update_method=async_update_data,
        update_interval=timedelta(seconds=120),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok