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
- Home Assistant container files on the NAS: `/docker/homeassistant`.

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
- Home Assistant version file `\\192.168.1.250\docker\homeassistant\.HA_VERSION` reads `2025.12.5`.

Available local command-line options checked on 2026-07-02:

- PowerShell
- Windows OpenSSH: `ssh.exe`, `scp.exe`, `sftp.exe`
- WSL/Bash: `wsl.exe`, `bash.exe`
- `curl.exe`

Preferred file access route:

1. Use SMB through the mapped Synology `docker` share. Read and edit Home Assistant files through `\\192.168.1.250\docker\homeassistant`.
2. If SMB is not convenient, enable SSH on the Synology and use OpenSSH commands such as `ssh <synology-user>@192.168.1.250 "ls -la /docker/homeassistant"`. As of the verification above, SSH is not currently reachable.

Useful SMB commands:

- Test access: `Test-Path "\\192.168.1.250\docker\homeassistant"`.
- Map the Synology `docker` share from an interactive shell: `net use \\192.168.1.250\docker /user:BottleWasher * /persistent:yes`. The `*` makes Windows prompt for the password instead of putting it in command history.
- After mapping succeeds, list files with PowerShell: `Get-ChildItem "\\192.168.1.250\docker\homeassistant"`.

Do not store Synology passwords, Home Assistant long-lived access tokens, camera passwords, or other secrets in this repository. Ask the user before configuring persistent credentials or enabling new NAS services.
