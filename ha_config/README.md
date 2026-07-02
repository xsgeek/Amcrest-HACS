# Home Assistant Config Snapshots

Versioned copies of Home Assistant automations, scenes, scripts, and
blueprints from the live `HA-Staging` config, so changes to them can be
tracked and restored alongside this repo's integration code.

These files are copies, not the live config. Home Assistant itself still
reads from `\\192.168.1.250\HA-Staging` (see [AGENTS.md](../AGENTS.md)).

## Syncing

Pull the latest live files into this folder:

```powershell
scripts/sync_ha_config.ps1
```

Push edits made here back to the live HA share:

```powershell
scripts/sync_ha_config.ps1 -Direction push
```

Run a pull after making changes in the HA UI, and a push after editing files
here directly, so this folder and the live config stay in sync. Commit
`ha_config/` changes to track history and enable rollback.

## Layout

- `automations.yaml`
- `scenes.yaml`
- `scripts.yaml`
- `blueprints/`
