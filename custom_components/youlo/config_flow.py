"""Config flow for Joulo integration."""
from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_API_KEY, API_CHARGERS

_LOGGER = logging.getLogger(__name__)

async def validate_input(hass: HomeAssistant, data: dict) -> dict:
    """Validate the user input by calling the chargers endpoint."""
    api_key = data[CONF_API_KEY].strip()
    
    # Als de key niet al begint met 'Bearer ', voegen we het toe (indien nodig voor Joulo API)
    auth_header = api_key if api_key.lower().startswith("bearer ") else f"Bearer {api_key}"
    headers = {"Authorization": auth_header}
    
    session = async_get_clientsession(hass)
    
    try:
        async with session.get(API_CHARGERS, headers=headers, timeout=10) as resp:
            _LOGGER.debug("Joulo auth check status: %s", resp.status)
            if resp.status in (401, 403):
                raise ValueError("invalid_auth")
            if resp.status != 200:
                _LOGGER.error("Joulo API validation failed with status: %s", resp.status)
                raise ValueError("cannot_connect")
    except TimeoutError:
        raise ValueError("cannot_connect")
            
    return {"title": "Joulo", "api_key": auth_header}

class JouloConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Joulo."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                # Sla het werkende API header formaat op
                return self.async_create_entry(
                    title=info["title"], 
                    data={CONF_API_KEY: info["api_key"]}
                )
            except ValueError as err:
                errors["base"] = str(err)
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during Joulo auth: %s", err)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): str,
            }),
            errors=errors,
        )