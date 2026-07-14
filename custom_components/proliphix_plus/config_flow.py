"""Config flow for Proliphix Plus."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ProliphixAuthError, ProliphixClient, ProliphixConnectionError
from .const import (
    CONF_AUTO_TIME_SYNC,
    CONF_HEAT_ONLY,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_SCAN_INTERVAL,
            default=DEFAULT_SCAN_INTERVAL,
        ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=600)),
        vol.Required(CONF_AUTO_TIME_SYNC, default=False): bool,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, str]:
    """Validate credentials by connecting to the thermostat."""
    session = async_get_clientsession(hass)
    client = ProliphixClient(
        data[CONF_HOST],
        data[CONF_USERNAME],
        data[CONF_PASSWORD],
        session,
    )
    try:
        state = await client.get_state()
    except ProliphixAuthError as err:
        raise InvalidAuth from err
    except (ProliphixConnectionError, aiohttp.ClientError) as err:
        raise CannotConnect from err

    return {"title": state.name}


class CannotConnect(Exception):
    """Unable to connect to thermostat."""


class InvalidAuth(Exception):
    """Invalid authentication."""


class ProliphixPlusConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Proliphix Plus."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._async_abort_entries_match(
                {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_USERNAME: user_input[CONF_USERNAME],
                }
            )
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> ProliphixPlusOptionsFlow:
        """Get the options flow."""
        return ProliphixPlusOptionsFlow()


class ProliphixPlusOptionsFlow(OptionsFlow):
    """Handle options flow."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL, max=600),
                    ),
                    vol.Required(
                        CONF_AUTO_TIME_SYNC,
                        default=options.get(CONF_AUTO_TIME_SYNC, False),
                    ): bool,
                    vol.Required(
                        CONF_HEAT_ONLY,
                        default=options.get(CONF_HEAT_ONLY, False),
                    ): bool,
                }
            ),
        )
