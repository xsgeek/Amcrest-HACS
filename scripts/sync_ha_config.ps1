<#
.SYNOPSIS
    Copies Home Assistant automations, scenes, scripts, and blueprints from the
    live HA-Staging SMB share into this repo for versioning, and can push edits
    back the other direction.

.PARAMETER Direction
    "pull" copies live HA files into the repo (default). "push" copies the
    repo's copies back to the live HA share.

.PARAMETER HaSharePath
    Path to the active Home Assistant config share. Defaults to the verified
    live share from AGENTS.md.

.EXAMPLE
    scripts/sync_ha_config.ps1
    scripts/sync_ha_config.ps1 -Direction push
#>
param(
    [ValidateSet("pull", "push")]
    [string]$Direction = "pull",

    [string]$HaSharePath = "\\192.168.1.250\HA-Staging",

    [string]$RepoConfigPath = (Join-Path $PSScriptRoot "..\ha_config")
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $HaSharePath)) {
    throw "Cannot reach Home Assistant config share: $HaSharePath"
}

$targets = @(
    @{ Name = "automations.yaml"; RelativePath = "automations.yaml" },
    @{ Name = "scenes.yaml"; RelativePath = "scenes.yaml" },
    @{ Name = "scripts.yaml"; RelativePath = "scripts.yaml" },
    @{ Name = "blueprints"; RelativePath = "blueprints" }
)

foreach ($target in $targets) {
    $liveItem = Join-Path $HaSharePath $target.RelativePath
    $repoItem = Join-Path $RepoConfigPath $target.RelativePath

    if ($Direction -eq "pull") {
        if (-not (Test-Path -LiteralPath $liveItem)) {
            Write-Warning "Skipping $($target.Name): not found at $liveItem"
            continue
        }

        $repoParent = Split-Path -Parent $repoItem
        if (-not (Test-Path -LiteralPath $repoParent)) {
            New-Item -ItemType Directory -Path $repoParent -Force | Out-Null
        }

        if ((Get-Item -LiteralPath $liveItem).PSIsContainer) {
            Copy-Item -LiteralPath $liveItem -Destination $repoItem -Recurse -Force
        } else {
            Copy-Item -LiteralPath $liveItem -Destination $repoItem -Force
        }
        Write-Host "Pulled $($target.Name)"
    } else {
        if (-not (Test-Path -LiteralPath $repoItem)) {
            Write-Warning "Skipping $($target.Name): not found at $repoItem"
            continue
        }

        if ((Get-Item -LiteralPath $repoItem).PSIsContainer) {
            Copy-Item -LiteralPath $repoItem -Destination $liveItem -Recurse -Force
        } else {
            Copy-Item -LiteralPath $repoItem -Destination $liveItem -Force
        }
        Write-Host "Pushed $($target.Name)"
    }
}
