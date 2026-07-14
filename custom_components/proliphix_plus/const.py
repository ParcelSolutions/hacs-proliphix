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
    "4.1.13": "AverageTemp",
    "4.1.14": "RelHumidity",
    "4.3.2.1": "OutdoorTemp",
    "4.4.1.3.1.1": "ActiveSchedule",
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
    # Preset setback temperatures (heat/cool per class)
    "4.4.1.1.1.1": "HomeHeatSetback",
    "4.4.1.1.1.2": "HomeCoolSetback",
    "4.4.1.1.2.1": "AwayHeatSetback",
    "4.4.1.1.2.2": "AwayCoolSetback",
    "4.4.1.1.3.1": "SleepHeatSetback",
    "4.4.1.1.3.2": "SleepCoolSetback",
    "4.4.1.1.4.1": "VacationHeatSetback",
    "4.4.1.1.4.2": "VacationCoolSetback",
    # Vacation dates (epoch timestamps)
    "4.4.1.2.1": "VacationStart",
    "4.4.1.2.2": "VacationEnd",
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

# CurrentClass / occupation values
CLASS_HOME = 1
CLASS_SLEEP = 2
CLASS_AWAY = 3
CLASS_VACATION = 4
CLASS_MANUAL = 5

# Fan state values
FAN_STATE_AUTO = 1
FAN_STATE_ON = 2
FAN_STATE_CIRCULATE = 3

# Hold state values
HOLD_OFF = 1
HOLD_TEMPORARY = 2
HOLD_PERMANENT = 3

# Preset mode mapping to CurrentClass value
PRESET_TO_CLASS: dict[str, int] = {
    "home": CLASS_HOME,
    "away": CLASS_AWAY,
    "sleep": CLASS_SLEEP,
    "vacation": CLASS_VACATION,
    "manual": CLASS_MANUAL,
}

CLASS_TO_PRESET: dict[int, str] = {v: k for k, v in PRESET_TO_CLASS.items()}

# Preset temperature OIDs (heat, cool)
PRESET_TEMP_OIDS: dict[str, tuple[str, str]] = {
    "home": ("4.4.1.1.1.1", "4.4.1.1.1.2"),
    "away": ("4.4.1.1.2.1", "4.4.1.1.2.2"),
    "sleep": ("4.4.1.1.3.1", "4.4.1.1.3.2"),
    "vacation": ("4.4.1.1.4.1", "4.4.1.1.4.2"),
}

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
SERVICE_SET_SLEEP = "set_sleep"
SERVICE_SET_VACATION = "set_vacation"
SERVICE_CLEAR_VACATION = "clear_vacation"
SERVICE_REFRESH = "refresh"
SERVICE_REBOOT = "reboot"
SERVICE_READ_OID = "read_oid"
SERVICE_WRITE_OID = "write_oid"
