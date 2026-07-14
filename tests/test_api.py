"""Tests for Proliphix API client."""

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.proliphix_plus.api import (
    ProliphixAuthError,
    ProliphixClient,
    ProliphixConnectionError,
)
from custom_components.proliphix_plus.models import oid_key


@pytest.fixture
def mock_session() -> MagicMock:
    """Create a mock aiohttp session."""
    return MagicMock(spec=aiohttp.ClientSession)


@pytest.fixture
def client(mock_session: MagicMock) -> ProliphixClient:
    """Create a Proliphix client."""
    return ProliphixClient("192.168.1.10", "admin", "password", mock_session)


def test_client_host_normalization(mock_session: MagicMock) -> None:
    """Test host URL normalization."""
    c = ProliphixClient("192.168.1.10:8080", "admin", "pass", mock_session)
    assert c.host == "http://192.168.1.10:8080"

    c2 = ProliphixClient("http://10.0.0.1/", "admin", "pass", mock_session)
    assert c2.host == "http://10.0.0.1"


async def test_communicate_success(client: ProliphixClient) -> None:
    """Test successful communication."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text = AsyncMock(return_value="OID4.1.13=720&OID4.1.5=700")
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    client._session.post = MagicMock(return_value=mock_response)

    code, raw = await client.communicate("get", {"OID4.1.13": ""})
    assert code == 200
    assert raw[oid_key("4.1.13")] == "720"


async def test_communicate_auth_error(client: ProliphixClient) -> None:
    """Test authentication error."""
    mock_response = AsyncMock()
    mock_response.status = 401
    mock_response.text = AsyncMock(return_value="Unauthorized")
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    client._session.post = MagicMock(return_value=mock_response)

    with pytest.raises(ProliphixAuthError):
        await client.communicate("get", {"OID4.1.13": ""})


async def test_communicate_connection_error(client: ProliphixClient) -> None:
    """Test connection error after retries."""
    client._session.post = MagicMock(side_effect=aiohttp.ClientError("fail"))

    with pytest.raises(ProliphixConnectionError):
        await client.communicate("get", {"OID4.1.13": ""})


async def test_read_oid(client: ProliphixClient) -> None:
    """Test read single OID."""
    with patch.object(
        client,
        "communicate",
        return_value=(200, {oid_key("4.1.13"): "720"}),
    ):
        value = await client.read_oid("4.1.13")
        assert value == "720"
