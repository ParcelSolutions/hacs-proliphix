"""Data models for Proliphix Plus."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def oid_key(oid: str) -> str:
    """Convert OID short id to response key (dots to underscores)."""
    return f"OID{oid.replace('.', '_')}"


def oid_form_key(oid: str) -> str:
    """Convert OID short id to form POST key."""
    return f"OID{oid}"


def flatten_response(parsed: dict[str, list[str]]) -> dict[str, str]:
    """Flatten parse_qs result; dots in keys become underscores."""
    return {
        key.replace(".", "_"): values[-1] if values else ""
        for key, values in parsed.items()
    }


def int_or_none(raw: Any) -> int | None:
    """Parse int or return None."""
    if raw is None or raw == "":
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def float_or_none(raw: Any) -> float | None:
    """Parse float or return None."""
    if raw is None or raw == "":
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def decidegrees_to_fahrenheit(raw: Any) -> float | None:
    """Convert Proliphix decidegrees Fahrenheit to float Fahrenheit."""
    value = float_or_none(raw)
    if value is None:
        return None
    return round(value / 10, 1)


def fahrenheit_to_decidegrees(value: float) -> int:
    """Convert Fahrenheit float to Proliphix decidegrees."""
    return int(round(value * 10))


def decidegrees_to_celsius(raw: Any) -> float | None:
    """Convert Proliphix decidegrees Fahrenheit to Celsius."""
    fahrenheit = decidegrees_to_fahrenheit(raw)
    if fahrenheit is None:
        return None
    return round((fahrenheit - 32) * 5 / 9, 1)


@dataclass
class ProliphixData:
    """Typed thermostat state from OID poll."""

    raw: dict[str, str] = field(default_factory=dict)

    @property
    def dev_name(self) -> str | None:
        return self.raw.get(oid_key("1.2")) or None

    @property
    def site_name(self) -> str | None:
        return self.raw.get(oid_key("1.10.9")) or None

    @property
    def model_name(self) -> str | None:
        return self.raw.get(oid_key("2.7.1")) or None

    @property
    def dev_rev(self) -> str | None:
        return self.raw.get(oid_key("1.3")) or None

    @property
    def dev_app(self) -> str | None:
        return self.raw.get(oid_key("1.7")) or None

    @property
    def name(self) -> str:
        """Device display name."""
        site = self.site_name or ""
        dev = self.dev_name or "Thermostat"
        if site:
            return f"{site}:{dev}"
        return dev

    @property
    def average_temp(self) -> float | None:
        return decidegrees_to_fahrenheit(self.raw.get(oid_key("4.1.13")))

    @property
    def outdoor_temp(self) -> float | None:
        return decidegrees_to_fahrenheit(self.raw.get(oid_key("4.3.2.1")))

    @property
    def setback_heat(self) -> float | None:
        return decidegrees_to_fahrenheit(self.raw.get(oid_key("4.1.5")))

    @property
    def setback_cool(self) -> float | None:
        return decidegrees_to_fahrenheit(self.raw.get(oid_key("4.1.6")))

    @property
    def humidity(self) -> int | None:
        return int_or_none(self.raw.get(oid_key("4.1.14")))

    @property
    def hvac_mode(self) -> int | None:
        return int_or_none(self.raw.get(oid_key("4.1.1")))

    @property
    def hvac_state(self) -> int | None:
        return int_or_none(self.raw.get(oid_key("4.1.2")))

    @property
    def fan_state(self) -> int | None:
        return int_or_none(self.raw.get(oid_key("4.1.4")))

    @property
    def current_class(self) -> int | None:
        return int_or_none(self.raw.get(oid_key("4.1.11")))

    @property
    def hold_state(self) -> int | None:
        return int_or_none(self.raw.get(oid_key("4.1.7")))

    @property
    def vacation_state(self) -> int | None:
        return int_or_none(self.raw.get(oid_key("4.1.10")))

    @property
    def heat_usage(self) -> int | None:
        return int_or_none(self.raw.get(oid_key("4.5.1")))

    @property
    def cool_usage(self) -> int | None:
        return int_or_none(self.raw.get(oid_key("4.5.3")))

    @property
    def fan_usage(self) -> int | None:
        return int_or_none(self.raw.get(oid_key("4.5.5")))

    @property
    def uptime(self) -> int | None:
        return int_or_none(self.raw.get(oid_key("2.1.1")))

    @property
    def thermostat_time(self) -> int | None:
        return int_or_none(self.raw.get(oid_key("2.5.1")))

    @property
    def active_schedule(self) -> str | None:
        return self.raw.get(oid_key("4.4.1.3.1.1")) or None

    @property
    def filter_hours(self) -> int | None:
        return int_or_none(self.raw.get(oid_key("4.6.1")))

    @property
    def vacation_start(self) -> int | None:
        return int_or_none(self.raw.get(oid_key("4.4.1.2.1")))

    @property
    def vacation_end(self) -> int | None:
        return int_or_none(self.raw.get(oid_key("4.4.1.2.2")))

    def get_oid_value(self, oid: str) -> str | None:
        """Get raw OID value by short id."""
        return self.raw.get(oid_key(oid))

    def get_preset_temp(self, preset: str, heat: bool = True) -> float | None:
        """Get preset temperature in Fahrenheit."""
        oids = {
            "home": ("4.4.1.1.1.1", "4.4.1.1.1.2"),
            "away": ("4.4.1.1.2.1", "4.4.1.1.2.2"),
            "sleep": ("4.4.1.1.3.1", "4.4.1.1.3.2"),
            "vacation": ("4.4.1.1.4.1", "4.4.1.1.4.2"),
        }
        if preset not in oids:
            return None
        oid = oids[preset][0 if heat else 1]
        return decidegrees_to_fahrenheit(self.raw.get(oid_key(oid)))

    @classmethod
    def from_raw(cls, raw: dict[str, str]) -> ProliphixData:
        """Build ProliphixData from flat response dict."""
        return cls(raw=raw)
