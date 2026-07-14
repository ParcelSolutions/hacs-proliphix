"""Tests for Proliphix coordinator."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.proliphix_plus.api import ProliphixConnectionError
from custom_components.proliphix_plus.coordinator import ProliphixDataUpdateCoordinator
from custom_components.proliphix_plus.models import ProliphixData


@pytest.fixture
def mock_entry(hass: HomeAssistant) -> ConfigEntry:
    """Create a mock config entry."""
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry"
    entry.options = {}
    entry.data = {}
    return entry


@pytest.fixture
def mock_client() -> MagicMock:
    """Create a mock API client."""
    client = MagicMock()
    client.get_state = AsyncMock(
        return_value=ProliphixData.from_raw({"OID1_2": "Thermostat"})
    )
    client.clock_value = MagicMock(return_value=1000000)
    return client


async def test_coordinator_update_success(
    hass: HomeAssistant, mock_entry: ConfigEntry, mock_client: MagicMock
) -> None:
    """Test successful coordinator update."""
    coordinator = ProliphixDataUpdateCoordinator(hass, mock_client, mock_entry)
    data = await coordinator._async_update_data()
    assert data.dev_name == "Thermostat"
    assert coordinator.last_successful_sync is not None
    assert coordinator.last_error is None


async def test_coordinator_update_connection_error(
    hass: HomeAssistant, mock_entry: ConfigEntry, mock_client: MagicMock
) -> None:
    """Test coordinator update with connection error."""
    mock_client.get_state = AsyncMock(side_effect=ProliphixConnectionError("fail"))
    coordinator = ProliphixDataUpdateCoordinator(hass, mock_client, mock_entry)
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
    assert coordinator.last_error is not None
