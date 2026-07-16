"""Constants for the Proliphix Plus integration."""

from homeassistant.const import Platform

DOMAIN = "proliphix_plus"

PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.NUMBER,
]

CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_AUTO_TIME_SYNC = "auto_time_sync"
CONF_HEAT_ONLY = "heat_only"

DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 30

TIMEOUT = 5
MAX_ATTEMPTS = 3
RETRY_DELAY = 1

# OID registry: short id -> human name
OIDS: dict[str, str] = {
    "1.1": "DevType",
    "1.2": "DevName",
    "1.3": "DevRev",
    "1.4": "DevSerial",
    "1.5": "DevBuild",
    "1.6": "DevBoot",
    "1.7": "DevApp",
    "1.8": "DevLib",
    "1.10.5": "SiteAddr",
    "1.10.9": "SiteName",
    "2.1.1": "Uptime",
    "2.5.1": "Time",
    "2.7.1": "ModelName",
    "4.1.1": "HvacMode",
    "4.1.2": "HvacState",
    "4.1.4": "FanState",
    "4.1.5": "SetbackHeat",
    "4.1.6": "SetbackCool",
    "4.1.9": "ScheduleCommit",
    "4.1.11": "CurrentClass",
    "4.1.12": "ActivePeriod",
    "4.1.13": "AverageTemp",
    "4.1.14": "RelHumidity",
    "4.3.2.1": "OutdoorTemp",
    "4.4.3.2.1": "SundayClass",
    "4.4.3.2.2": "MondayClass",
    "4.4.3.2.3": "TuesdayClass",
    "4.4.3.2.4": "WednesdayClass",
    "4.4.3.2.5": "ThursdayClass",
    "4.4.3.2.6": "FridayClass",
    "4.4.3.2.7": "SaturdayClass",
    "4.5.1": "Heat1Usage",
    "4.5.3": "Cool1Usage",
    "4.5.5": "FanUsage",
    "4.5.6": "LastUsageReset",
    # Hold and schedule control
    "4.1.7": "HoldState",
    "4.1.8": "HoldUntil",
    "4.1.10": "VacationState",
    # Schedule period start times (minutes from midnight): 4.4.1.3.{class}.{period}
    "4.4.1.3.1.1": "HomePeriod1Start",
    "4.4.1.3.1.2": "HomePeriod2Start",
    "4.4.1.3.1.3": "HomePeriod3Start",
    "4.4.1.3.1.4": "HomePeriod4Start",
    "4.4.1.3.2.1": "OutPeriod1Start",
    "4.4.1.3.2.2": "OutPeriod2Start",
    "4.4.1.3.2.3": "OutPeriod3Start",
    "4.4.1.3.2.4": "OutPeriod4Start",
    "4.4.1.3.3.1": "AwayPeriod1Start",
    "4.4.1.3.3.2": "AwayPeriod2Start",
    "4.4.1.3.3.3": "AwayPeriod3Start",
    "4.4.1.3.3.4": "AwayPeriod4Start",
    # Schedule period heat setbacks (decidegrees F): 4.4.1.4.{class}.{period}
    "4.4.1.4.1.1": "HomePeriod1Heat",
    "4.4.1.4.1.2": "HomePeriod2Heat",
    "4.4.1.4.1.3": "HomePeriod3Heat",
    "4.4.1.4.1.4": "HomePeriod4Heat",
    "4.4.1.4.2.1": "OutPeriod1Heat",
    "4.4.1.4.2.2": "OutPeriod2Heat",
    "4.4.1.4.2.3": "OutPeriod3Heat",
    "4.4.1.4.2.4": "OutPeriod4Heat",
    "4.4.1.4.3.1": "AwayPeriod1Heat",
    "4.4.1.4.3.2": "AwayPeriod2Heat",
    "4.4.1.4.3.3": "AwayPeriod3Heat",
    "4.4.1.4.3.4": "AwayPeriod4Heat",
    # Schedule period cool setbacks (decidegrees F): 4.4.1.5.{class}.{period}
    "4.4.1.5.1.1": "HomePeriod1Cool",
    "4.4.1.5.1.2": "HomePeriod2Cool",
    "4.4.1.5.1.3": "HomePeriod3Cool",
    "4.4.1.5.1.4": "HomePeriod4Cool",
    "4.4.1.5.2.1": "OutPeriod1Cool",
    "4.4.1.5.2.2": "OutPeriod2Cool",
    "4.4.1.5.2.3": "OutPeriod3Cool",
    "4.4.1.5.2.4": "OutPeriod4Cool",
    "4.4.1.5.3.1": "AwayPeriod1Cool",
    "4.4.1.5.3.2": "AwayPeriod2Cool",
    "4.4.1.5.3.3": "AwayPeriod3Cool",
    "4.4.1.5.3.4": "AwayPeriod4Cool",
    # Filter hours
    "4.6.1": "FilterHours",
    # Reboot
    "2.2.1": "Reboot",
}

# OIDs polled on every update
POLL_OIDS: list[str] = sorted(OIDS.keys())

WEEKLY_SCHEDULE_OIDS: list[str] = [
    "4.4.3.2.1",
    "4.4.3.2.2",
    "4.4.3.2.3",
    "4.4.3.2.4",
    "4.4.3.2.5",
    "4.4.3.2.6",
    "4.4.3.2.7",
]

# HVAC mode values from Proliphix API
HVAC_MODE_OFF = 1
HVAC_MODE_HEAT = 2
HVAC_MODE_COOL = 3
HVAC_MODE_AUTO = 4

# HVAC state (action) values
HVAC_STATE_IDLE = 1
HVAC_STATE_HEATING = 3
HVAC_STATE_HEATING_2 = 4
HVAC_STATE_HEATING_3 = 5
HVAC_STATE_COOLING = 6
HVAC_STATE_COOLING_2 = 7

# CurrentClass / day-class values (PDP API: In/Out/Away only)
CLASS_HOME = 1  # In / Occupied
CLASS_OUT = 2  # Out / Unoccupied
CLASS_AWAY = 3  # Away / Other
CLASS_SLEEP = CLASS_OUT  # Back-compat alias

# Fan state values
FAN_STATE_AUTO = 1
FAN_STATE_ON = 2
FAN_STATE_CIRCULATE = 3

# Hold state values
HOLD_OFF = 1
HOLD_TEMPORARY = 2
HOLD_PERMANENT = 3

# Climate presets map 1:1 to the three day classes
PRESET_TO_CLASS: dict[str, int] = {
    "home": CLASS_HOME,
    "out": CLASS_OUT,
    "away": CLASS_AWAY,
}

CLASS_TO_PRESET: dict[int, str] = {v: k for k, v in PRESET_TO_CLASS.items()}

CLIMATE_PRESET_MODES: list[str] = list(PRESET_TO_CLASS.keys())

# Schedule day-class setbacks use period tables, not a single preset OID.
# Heat: 4.4.1.4.{class}.{period}  Cool: 4.4.1.5.{class}.{period}
SCHEDULE_PERIODS: tuple[str, ...] = ("morn", "day", "eve", "night")
PRESET_TO_SCHEDULE_CLASS: dict[str, int] = {
    "home": CLASS_HOME,
    "out": CLASS_OUT,
    "away": CLASS_AWAY,
}


def schedule_heat_oid(class_index: int, period: int) -> str:
    """OID for period heat setback (1-based class and period)."""
    return f"4.4.1.4.{class_index}.{period}"


def schedule_cool_oid(class_index: int, period: int) -> str:
    """OID for period cool setback (1-based class and period)."""
    return f"4.4.1.5.{class_index}.{period}"

ATTR_FAN = "fan"
ATTR_RAW_OIDS = "raw_oids"

SERVICE_SYNC_TIME = "sync_time"
SERVICE_SET_TIME = "set_time"
SERVICE_SET_TIMEZONE = "set_timezone"
SERVICE_RESUME_SCHEDULE = "resume_schedule"
SERVICE_UPLOAD_SCHEDULE = "upload_schedule"
SERVICE_DOWNLOAD_SCHEDULE = "download_schedule"
SERVICE_SET_HOME = "set_home"
SERVICE_SET_AWAY = "set_away"
SERVICE_SET_OUT = "set_out"
SERVICE_SET_SLEEP = "set_sleep"  # Alias for set_out
SERVICE_SET_VACATION = "set_vacation"
SERVICE_CLEAR_VACATION = "clear_vacation"
SERVICE_REFRESH = "refresh"
SERVICE_REBOOT = "reboot"
SERVICE_READ_OID = "read_oid"
SERVICE_WRITE_OID = "write_oid"
