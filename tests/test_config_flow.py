"""Tests for Proliphix config flow."""

from unittest.mock import patch

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.proliphix_plus.const import DOMAIN


async def test_user_form(hass: HomeAssistant) -> None:
    """Test config flow shows user form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_user_form_invalid_auth(hass: HomeAssistant) -> None:
    """Test config flow with invalid auth."""
    from custom_components.proliphix_plus.config_flow import InvalidAuth

    with patch(
        "custom_components.proliphix_plus.config_flow.validate_input",
        side_effect=InvalidAuth,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data={
                CONF_HOST: "192.168.1.10",
                CONF_USERNAME: "admin",
                CONF_PASSWORD: "wrong",
            },
        )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "invalid_auth"


async def test_user_form_success(hass: HomeAssistant) -> None:
    """Test successful config flow."""
    with (
        patch(
            "custom_components.proliphix_plus.config_flow.validate_input",
            return_value={"title": "Home:Thermostat"},
        ),
        patch(
            "custom_components.proliphix_plus.async_setup_entry",
            return_value=True,
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data={
                CONF_HOST: "192.168.1.10",
                CONF_USERNAME: "admin",
                CONF_PASSWORD: "secret",
            },
        )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Home:Thermostat"
    assert result["data"][CONF_HOST] == "192.168.1.10"
