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

### HACS (recommended)

**Does the repo need to be public?** No. HACS works with **private GitHub repositories** too, as long as HACS can access them:

| Repo visibility | What you need |
|-----------------|---------------|
| **Public** | Add the repo URL in HACS → nothing else |
| **Private** | A [GitHub personal access token](https://github.com/settings/tokens) with `repo` scope, added in **HACS → Settings → GitHub** (or during HACS setup) |

You do **not** need to publish to the default HACS store. A **custom repository** is enough for personal use.

#### GitHub repository settings (for HACS)

CI sets the repository **description** and **topics** automatically. You can also edit them under **Settings → General** on GitHub:

- **Description:** `Home Assistant integration for Proliphix Plus network thermostats`
- **Topics:** `homeassistant`, `hacs`, `hacs-integration`, `proliphix`, `thermostat`, `climate`

**Private repositories:** HACS install in Home Assistant works with a GitHub token, but the upstream `hacs/action` validator downloads files from `raw.githubusercontent.com` and cannot read private repos. This project validates HACS structure from the CI checkout instead. To use the official HACS action, make the repository **public**.

#### 1. Push this project to GitHub

```bash
# Create an empty repo on GitHub (public or private), then:
git remote add origin https://github.com/ParcelSolutions/hacs-proliphix.git
git push -u origin main
```

Update `documentation` and `issue_tracker` in [`custom_components/proliphix_plus/manifest.json`](custom_components/proliphix_plus/manifest.json) if you fork or rename the repo.

#### 2. Add the custom repository in Home Assistant

1. **HACS** → **Integrations** → **⋮** (top right) → **Custom repositories**
2. Repository URL: `https://github.com/ParcelSolutions/hacs-proliphix`
3. Category: **Integration** → **Add**
4. Search **Proliphix Plus** → **Download**
5. **Restart Home Assistant**

#### 3. Add the integration

1. **Settings** → **Devices & Services** → **Add Integration**
2. Search **Proliphix Plus**
3. Enter host (e.g. `192.168.1.10:8080` or `http://duinbergen.duckdns.org:8888`), username, and password

For your setup, use the same URL as in `.env`. Home Assistant must be able to reach the thermostat (local IP or DNS).

### Manual (no HACS)

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
