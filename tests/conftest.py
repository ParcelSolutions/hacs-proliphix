"""Pytest configuration for Proliphix Plus unit tests."""

import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

_running_live = any("live_tests" in arg for arg in sys.argv)
if not _running_live:
    import pytest

    pytest_plugins = "pytest_homeassistant_custom_component"

    @pytest.fixture(autouse=True)
    def auto_enable_custom_integrations(enable_custom_integrations):
        """Enable loading custom integrations from custom_components/."""
        yield
