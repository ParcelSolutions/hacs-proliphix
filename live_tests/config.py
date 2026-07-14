"""Configuration for live thermostat tests."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@dataclass(frozen=True)
class LiveConfig:
    """Thermostat connection settings for live integration tests."""

    host: str
    username: str
    password: str

    @property
    def is_configured(self) -> bool:
        """Return True when required connection settings are present."""
        return bool(self.host and self.username and self.password)


def load_live_config() -> LiveConfig:
    """Read live test configuration from environment variables."""
    return LiveConfig(
        host=os.getenv("PROLIPHIX_PLUS_HOST", "").strip(),
        username=os.getenv("PROLIPHIX_PLUS_USERNAME", "").strip(),
        password=os.getenv("PROLIPHIX_PLUS_PASSWORD", "").strip(),
    )
