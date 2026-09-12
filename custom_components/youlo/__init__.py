"""The Joulo integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_API_KEY, API_CHARGERS, API_ENERGY, API_ERE_POSITION

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Joulo from a config entry."""
    api_key = entry.data[CONF_API_KEY].strip()
    
    # Altijd op de achtergrond 'Bearer ' toevoegen als het er niet staat
    auth_header = api_key if api_key.lower().startswith("bearer ") else f"Bearer {api_key}"
    headers = {"Authorization": auth_header}
    
    session = async_get_clientsession(hass)

    async def async_update_data():
        """Fetch data from Joulo REST API safely."""
        data = {}
        try:
            async with session.get(API_CHARGERS, headers=headers) as resp:
                if resp.status == 200:
                    data["chargers"] = await resp.json()
                else:
                    _LOGGER.warning("Joulo Chargers API returned status %s", resp.status)

            # 2. Energy Endpoint
            async with session.get(API_ENERGY, headers=headers) as resp:
                if resp.status == 200:
                    data["energy"] = await resp.json()
                else:
                    _LOGGER.warning("Joulo Energy API returned status %s", resp.status)

            # 3. ERE Position Endpoint
            async with session.get(API_ERE_POSITION, headers=headers) as resp:
                if resp.status == 200:
                    data["ere"] = await resp.json()
                else:
                    _LOGGER.warning("Joulo ERE Position API returned status %s", resp.status)

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

    # Voer de eerste verversing uit zonder de startup te blokkeren bij een fout
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok