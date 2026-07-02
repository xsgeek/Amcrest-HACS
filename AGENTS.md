# Codex Project Notes

## Local Home Assistant Environment

Unless the user says otherwise, assume Codex is running on the user's development machine on the same LAN as the Home Assistant system.

- Development machine: Windows desktop, described by the user as Windows 11. Windows compatibility APIs may report `Windows 10 Pro`, but the machine reports Windows build `26200` / kernel generation `10.0.26100`, which is Windows 11-era.
- Development machine LAN IP: `192.168.1.25` on adapter `Ethernet 2`; gateway `192.168.1.1`. The user says this IP is fixed.
- Synology NAS: DS220+, fixed IP `192.168.1.250`.
- Synology NAS username for file access: `BottleWasher`. This username is not secret; do not store the password.
- Docker host: the Synology NAS.
- Home Assistant: running in a Docker container on the Synology NAS.
- Home Assistant URL: `http://192.168.1.250:8123`.
- Home Assistant container host/config directory on the NAS filesystem: `/HA-Staging`.
- Active Home Assistant files are available over SMB at `\\192.168.1.250\HA-Staging`.

## Amcrest AD410 Doorbell

- Doorbell host: `192.168.1.179`.
- Doorbell username: `admin`. This username is not secret; do not store the password in tracked files.
- Store doorbell connection details in the project-local `.secrets.json` under `amcrestAd410` with `host`, `username`, `password`, `port`, and `rtspPort`. The tracked `.secrets.example.json` shows the expected shape with placeholders.
- Use HTTP port `80` for Amcrest/Dahua CGI calls with digest authentication.
- Use RTSP port `554` for camera streams.
- Verified on 2026-07-02: ports `80`, `554`, `5000`, and `37777` were reachable on `192.168.1.179`; HTTPS port `443` was closed.
- Verified on 2026-07-02 through `/cgi-bin/magicBox.cgi`: device type `AD410`, hardware version `1.00`, software version `1.000.00AC002.0.R,build:2023-10-12`.

## GitHub Project Access

- GitHub repository: `https://github.com/xsgeek/Amcrest-HACS`.
- Use the GitHub account `xsgeek` for this project only.
- Repo-local Git author identity should use `xsgeek <26286622+xsgeek@users.noreply.github.com>` unless the user says otherwise.
- Other local Codex/GitHub sessions should continue to use the work account `matthewacme` unless the user says otherwise.
- To keep this project scoped to the personal account, prefer the repo-local remote URL `https://xsgeek@github.com/xsgeek/Amcrest-HACS.git` instead of switching the globally active `gh` account.
- The account name `xsgeek` is not secret. Do not store GitHub tokens or passwords in this repository.

Verified on 2026-07-02 from the development machine:

- `192.168.1.250:8123` is reachable over TCP.
- `curl.exe -I --max-time 10 http://192.168.1.250:8123` returned HTTP `405 Method Not Allowed` with `Allow: GET`, confirming the Home Assistant HTTP endpoint is answering.
- SMB port `445` on `192.168.1.250` is reachable.
- SSH port `22` on `192.168.1.250` is not reachable.
- Authenticated SMB access to `\\192.168.1.250\docker\homeassistant` works after mapping `\\192.168.1.250\docker` with username `BottleWasher`.
- A temporary file write/read/delete test succeeded at `\\192.168.1.250\docker\homeassistant\.codex_access_test.txt`; the file was deleted after verification.
- `net use \\192.168.1.250\docker` reported `Status OK`.
- `\\192.168.1.250\docker\homeassistant` appears to be stale or not the active container config. Its `.HA_VERSION` reads `2025.12.5`, its `home-assistant.log` was last written on 2026-01-05, and live Home Assistant reports version `2026.2.2`.
- Authenticated SMB access to `\\192.168.1.250\HA-Staging` works and exposes the active Home Assistant config directory.
- `\\192.168.1.250\HA-Staging\.HA_VERSION` reads `2026.2.2`.
- `\\192.168.1.250\HA-Staging` contains active runtime files including `.storage`, `configuration.yaml`, `automations.yaml`, `custom_components`, `home-assistant.log`, `home-assistant_v2.db`, `secrets.yaml`, `themes`, and `www`.
- Live Home Assistant API at `http://192.168.1.250:8123/api/config` reports version `2026.2.2`, location `Toad Hall`, state `RUNNING`, time zone `America/New_York`, and `safe_mode: false`.
- Live Home Assistant WebSocket `system_health/info` reports `core-2026.2.2`, installation type `Home Assistant Container`, Docker `true`, container architecture `amd64`, config directory `/config`, and Python runtime `3.13.11`.
- Project dev dependencies intentionally pin Home Assistant to `homeassistant==2026.2.2` in `requirements-dev.txt` and the `pyproject.toml` dev extra so local editor analysis/tests match the deployed container version instead of the newer non-container package release.
- The repo-local VS Code workspace setting uses `python.defaultInterpreterPath: ".venv/Scripts/python.exe"`. Keep global VS Code Python settings pointed at a general system interpreter; this workspace setting should select the project `.venv` only when this repo is open.
- The project `.venv` was recreated on 2026-07-02 with local Python `3.13.14` via `py -3.13` to match the Home Assistant Container's Python 3.13 runtime family. The exact container patch version at verification time was Python `3.13.11`.
- Fresh Home Assistant automatic backups are visible on the NAS at `\\192.168.1.250\docker\ha_backup_toad_hall`.
- The latest inspected backup was `Automatic_backup_2026.2.2_2026-07-02_05.42_54001677.tar`. It contains `homeassistant.tar.gz`, whose config files are under `data/` inside the archive.
- That backup's `backup.json` reports backup slug `e03c14a9`, Home Assistant version `2026.2.2`, date `2026-07-02T05:42:54.001677-04:00`, type `partial`, `homeassistant_included: true`, and database excluded.
- Extracted backup config includes `data/.HA_VERSION`, `data/configuration.yaml`, `data/automations.yaml`, and `data/.storage/core.entity_registry`.
- Before the 2026-07-02 cleanup, `\\192.168.1.250\HA-Staging\configuration.yaml` and `automations.yaml` were byte-for-byte identical to the latest inspected 2026.2.2 backup.
- On 2026-07-02, Codex removed the legacy built-in Home Assistant `amcrest:` YAML block for `192.168.1.179` / `Front Portal`, removed the old `Someone is on the porch` automation that referenced `binary_sensor.front_portal_motion_detected_2`, and removed the no-longer-used Amcrest secret key from active `secrets.yaml`.
- The `Front Door Bell Pressed` automation was intentionally preserved for testing the new HACS integration event wiring. After cleanup it was present in active `automations.yaml` with `triggers: []`.
- Cleanup backup files were saved at `\\192.168.1.250\HA-Staging\tmp_backups\codex_amcrest_cleanup_20260702_091758`.
- Home Assistant was restarted through the API after cleanup. API status came back `RUNNING`, version `2026.2.2`, `safe_mode: false`.
- WebSocket entity registry cleanup removed stale Amcrest entities `camera.front_portal`, `binary_sensor.front_portal_online`, and `binary_sensor.front_portal_motion_detected`.
- Post-cleanup checks on 2026-07-02 found no `amcrest` or `front_portal` references in active `configuration.yaml` or `automations.yaml`, no matching live states, and no matching entity registry entries.
- Current active file hashes after cleanup: `\\192.168.1.250\HA-Staging\configuration.yaml` SHA256 `8AE2A3A0253A9B58EEC0A358E6414DE9C018CB3F00C8E9564442E8324EAFC04A`; `\\192.168.1.250\HA-Staging\automations.yaml` SHA256 `E23B40AB3B32FCA71E2352C85A0649C1DB40144680872F7FE1C1C1AED5B32E88`.
- Synology Drive is configured on the development machine with a local folder at `C:\Users\mh\Documents\SynologyDrive\HA-Staging`. The user says this syncs to a folder on the NAS filesystem.
- As of the 2026-07-02 cleanup, the local Synology Drive copies of `configuration.yaml` and `automations.yaml` match the active SMB files. Use the SMB path `\\192.168.1.250\HA-Staging` as the source of truth when files differ.

Available local command-line options checked on 2026-07-02:

- PowerShell
- Windows OpenSSH: `ssh.exe`, `scp.exe`, `sftp.exe`
- WSL/Bash: `wsl.exe`, `bash.exe`
- `curl.exe`

Preferred file access route:

1. Use the Home Assistant API token for live-system inspection, restarts, service calls, and entity/config-entry registry queries.
2. Use SMB path `\\192.168.1.250\HA-Staging` for active Home Assistant file reads/edits.
3. Use the local Synology Drive folder `C:\Users\mh\Documents\SynologyDrive\HA-Staging` only when it matches the active SMB file or when the user explicitly wants to edit the synced local copy.
4. Use `\\192.168.1.250\docker\ha_backup_toad_hall` to inspect recent Home Assistant backups. Extract the outer `.tar`, then inspect `homeassistant.tar.gz` and its `data/` directory for active configuration snapshots.
5. Treat `\\192.168.1.250\docker\homeassistant` as stale historical data, not the active Home Assistant config.
6. Avoid editing `.storage` while Home Assistant is running unless there is a fresh backup and no safer API/WebSocket path exists.
7. If SMB is not sufficient, enable SSH on the Synology and use OpenSSH commands such as `ssh <synology-user>@192.168.1.250 "ls -la /HA-Staging"`. As of the verification above, SSH is not currently reachable.

Home Assistant API access:

- Store the Home Assistant long-lived access token in the project-local `.secrets.json` file. This file is intentionally ignored by Git.
- Use `.secrets.example.json` as the template for the required shape.
- Use `scripts/ha_api.ps1` for API checks and service calls so the token stays out of command history and chat output.
- The token is secret. Do not commit it, print it, paste it into chat, or copy it into `AGENTS.md`.

Useful SMB commands:

- Test active HA config access: `Test-Path "\\192.168.1.250\HA-Staging"`.
- Map the Synology `docker` share from an interactive shell: `net use \\192.168.1.250\docker /user:BottleWasher * /persistent:yes`. The `*` makes Windows prompt for the password instead of putting it in command history.
- Map the Synology `HA-Staging` share from an interactive shell if needed: `net use \\192.168.1.250\HA-Staging /user:BottleWasher * /persistent:yes`.
- List active HA files with PowerShell: `Get-ChildItem "\\192.168.1.250\HA-Staging"`.
- List visible Docker share folders: `Get-ChildItem "\\192.168.1.250\docker"`.
- List available HA backup files: `Get-ChildItem "\\192.168.1.250\docker\ha_backup_toad_hall"`.

Do not store Synology passwords, Home Assistant long-lived access tokens, camera passwords, or other secrets in this repository. Ask the user before configuring persistent credentials or enabling new NAS services.
