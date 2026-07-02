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
- Fresh Home Assistant automatic backups are visible on the NAS at `\\192.168.1.250\docker\ha_backup_toad_hall`.
- The latest inspected backup was `Automatic_backup_2026.2.2_2026-07-02_05.42_54001677.tar`. It contains `homeassistant.tar.gz`, whose config files are under `data/` inside the archive.
- That backup's `backup.json` reports backup slug `e03c14a9`, Home Assistant version `2026.2.2`, date `2026-07-02T05:42:54.001677-04:00`, type `partial`, `homeassistant_included: true`, and database excluded.
- Extracted backup config includes `data/.HA_VERSION`, `data/configuration.yaml`, `data/automations.yaml`, and `data/.storage/core.entity_registry`.
- `\\192.168.1.250\HA-Staging\configuration.yaml` is byte-for-byte identical to the latest inspected 2026.2.2 backup's `data/configuration.yaml` (`SHA256 B59582CC9C4332959FBC87D9E81B4E41069EEE0BE5CD2076394DA973631FF9CE`).
- `\\192.168.1.250\HA-Staging\automations.yaml` is byte-for-byte identical to the latest inspected 2026.2.2 backup's `data/automations.yaml` (`SHA256 44C4FF65D30895FD667438C90482AD5A7F6738179AC9CC7490AF8A4AB40A5D99`).
- The active `configuration.yaml` still has the built-in `amcrest:` YAML block for host `192.168.1.179`, username `admin`, secret-backed password `!secret amcrest_ad410_password`, name `Front Portal`, `stream_source: rtsp`, and binary sensors `online` and `motion_detected`.
- The active entity registry contains Amcrest entities `camera.front_portal`, `binary_sensor.front_portal_online`, and `binary_sensor.front_portal_motion_detected`, all with platform `amcrest` and no config entry. It also contains automation entity `automation.front_door_bell_pressed`.
- The active `automations.yaml` references `binary_sensor.front_portal_motion_detected_2` in automation `Someone is on the porch` and listens for event type `amcrest` in automation `Front Door Bell Pressed`.
- Home Assistant API/WebSocket verification on 2026-07-02 showed live state entities `camera.front_portal`, `binary_sensor.front_portal_online`, `binary_sensor.front_portal_motion_detected`, and `automation.front_door_bell_pressed`.
- Home Assistant error log from the API on 2026-07-02 showed the built-in `homeassistant.components.amcrest` integration loading at startup.
- Synology Drive is configured on the development machine with a local folder at `C:\Users\mh\Documents\SynologyDrive\HA-Staging`. The user says this syncs to a folder on the NAS filesystem.
- `C:\Users\mh\Documents\SynologyDrive\HA-Staging\configuration.yaml` is byte-for-byte identical to the active NAS file and the latest inspected backup.
- `C:\Users\mh\Documents\SynologyDrive\HA-Staging\automations.yaml` is not identical to the active NAS file; use the SMB path `\\192.168.1.250\HA-Staging` as the source of truth when files differ.

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
