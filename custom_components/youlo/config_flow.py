"""Config flow for Joulo integration."""
from __future__ import annotations

import logging
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_API_KEY, API_CHARGERS

_LOGGER = logging.getLogger(__name__)

async def validate_input(hass: HomeAssistant, data: dict) -> dict:
    """Validate the user input by calling the chargers endpoint."""
    headers = {"Authorization": data[CONF_API_KEY]}
    async with aiohttp.ClientSession() as session:
        async with session.get(API_CHARGERS, headers=headers) as resp:
            if resp.status in (401, 403):
                raise ValueError("invalid_auth")
            if resp.status != 200:
                raise ValueError("cannot_connect")
    return {"title": "Joulo"}

class JouloConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Joulo."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except ValueError as err:
                errors["base"] = str(err)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): str,
            }),
            errors=errors,
        )