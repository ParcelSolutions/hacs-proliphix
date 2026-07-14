# Proliphix Plus for Home Assistant

A modern Home Assistant HACS integration for **Proliphix thermostats**, providing complete local control over the thermostat, schedules, presets, vacation mode, diagnostics, and advanced API access.

## Features

- **Climate control** — temperature, HVAC mode, fan mode, hold, presets
- **Preset modes** — Home, Away, Sleep, Vacation, Manual, Schedule
- **Time synchronization** — sync thermostat clock with Home Assistant
- **Vacation & Away mode** — configure and toggle from HA
- **Sensors** — indoor/outdoor temp, humidity, runtime, uptime, model, and more
- **Switches, buttons, numbers** — full thermostat control from the UI
- **Services** — time sync, presets, schedule resume, refresh, reboot
- **Diagnostics** — download device and integration diagnostics
- **100% local** — no cloud required

## Installation

### HACS

1. Open HACS → Custom repositories
2. Add this repository, category: **Integration**
3. Install **Proliphix Plus**
4. Restart Home Assistant
5. Add the integration from **Settings → Devices & Services**

### Manual

Copy `custom_components/proliphix_plus/` to your Home Assistant `custom_components/` directory and restart.

## Configuration

Add the integration via the UI. You will need:

- Thermostat IP address (optionally with port, e.g. `192.168.1.10:8080`)
- Username and password (from the thermostat web interface)

### Options

- **Poll interval** — how often to refresh data (default: 60 seconds)
- **Automatic time sync** — daily clock synchronization with Home Assistant
- **Heat only** — enable when no cooling or fan is connected; hides cool/fan controls and only uses heat setpoints

## Supported Devices

- NT10e, NT20e, NT100e, NT120e (and other models exposing the standard Proliphix local API)

## Services

| Service | Description |
|---------|-------------|
| `proliphix_plus.sync_time` | Sync thermostat clock with HA |
| `proliphix_plus.set_time` | Set thermostat date/time |
| `proliphix_plus.set_timezone` | Set thermostat timezone |
| `proliphix_plus.resume_schedule` | Resume programmed schedule |
| `proliphix_plus.set_home` | Activate Home preset |
| `proliphix_plus.set_away` | Activate Away preset |
| `proliphix_plus.set_sleep` | Activate Sleep preset |
| `proliphix_plus.set_vacation` | Enable vacation mode |
| `proliphix_plus.clear_vacation` | Disable vacation mode |
| `proliphix_plus.refresh` | Force data refresh |
| `proliphix_plus.reboot` | Reboot thermostat |
| `proliphix_plus.read_oid` | Read a raw OID value |
| `proliphix_plus.write_oid` | Write a raw OID value |

## Migration from built-in Proliphix

Remove any YAML `climate: platform: proliphix` configuration before adding this integration.

## Development

Copy [`.env.example`](.env.example) to `.env` and set your thermostat credentials for local testing:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `PROLIPHIX_PLUS_HOST` | Thermostat IP or `ip:port` |
| `PROLIPHIX_PLUS_USERNAME` | Thermostat web UI username |
| `PROLIPHIX_PLUS_PASSWORD` | Thermostat web UI password |
| `PROLIPHIX_PLUS_SCAN_INTERVAL` | Poll interval in seconds (default: 60) |
| `PROLIPHIX_PLUS_AUTO_TIME_SYNC` | `true` / `false` |
| `PROLIPHIX_PLUS_HEAT_ONLY` | `true` when no cooling or fan is connected |

Run tests and lint:

```bash
pip install -r requirements_test.txt
pytest tests -v                              # unit tests
python3 -m live_tests.run_live            # live thermostat checks (uses .env)
ruff check custom_components tests live_tests
```

Live checks connect to the thermostat configured in `.env` and perform read-only API calls (no writes).

## License

MIT License — see [LICENSE](LICENSE).
