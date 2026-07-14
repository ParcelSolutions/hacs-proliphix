#!/usr/bin/env python3
"""Run read-only live checks against a configured Proliphix thermostat."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import aiohttp
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from custom_components.proliphix_plus.api import ProliphixClient  # noqa: E402
from custom_components.proliphix_plus.models import oid_key  # noqa: E402
from live_tests.config import load_live_config  # noqa: E402


async def run_checks() -> None:
    """Execute live read-only thermostat checks."""
    config = load_live_config()
    if not config.is_configured:
        raise SystemExit("Missing PROLIPHIX_PLUS_HOST, USERNAME, or PASSWORD in .env")

    async with aiohttp.ClientSession() as session:
        client = ProliphixClient(
            config.host,
            config.username,
            config.password,
            session,
        )

        print(f"Connecting to {client.host} ...")

        state = await client.get_state()
        print(f"Device: {state.name}")
        print(f"Room temp: {state.average_temp} F")
        print(f"HVAC mode OID: {state.hvac_mode}")
        assert state.name
        assert state.average_temp is not None

        temp_oid = await client.read_oid("4.1.13")
        print(f"OID 4.1.13 raw: {temp_oid}")
        assert temp_oid is not None and temp_oid.isdigit()

        name_oid = await client.read_oid("1.2")
        print(f"OID 1.2 raw: {name_oid}")
        assert name_oid

        code, raw = await client.communicate(
            "get", {"OID4.1.13": "", "submit": "Submit"}
        )
        assert code == 200
        assert oid_key("4.1.13") in raw

    print("All live checks passed.")


def main() -> None:
    """Entry point."""
    asyncio.run(run_checks())


if __name__ == "__main__":
    main()
