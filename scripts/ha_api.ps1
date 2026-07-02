param(
    [ValidateSet("status", "restart", "get", "post")]
    [string]$Action = "status",

    [string]$Path = "/api/",

    [string]$SecretsPath = (Join-Path $PSScriptRoot "..\.secrets.json")
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $SecretsPath)) {
    throw "Missing secrets file: $SecretsPath. Copy .secrets.example.json to .secrets.json and add a Home Assistant long-lived access token."
}

$secrets = Get-Content -LiteralPath $SecretsPath -Raw | ConvertFrom-Json
$baseUrl = [string]$secrets.homeAssistant.baseUrl
$token = [string]$secrets.homeAssistant.token

if ([string]::IsNullOrWhiteSpace($baseUrl)) {
    throw "homeAssistant.baseUrl is missing in $SecretsPath."
}

if ([string]::IsNullOrWhiteSpace($token) -or $token -eq "paste-long-lived-access-token-here") {
    throw "homeAssistant.token is missing in $SecretsPath."
}

$baseUrl = $baseUrl.TrimEnd("/")
$headers = @{
    Authorization = "Bearer $token"
}

switch ($Action) {
    "status" {
        Invoke-RestMethod -Method Get -Uri "$baseUrl/api/" -Headers $headers
    }
    "restart" {
        Invoke-RestMethod -Method Post -Uri "$baseUrl/api/services/homeassistant/restart" -Headers $headers
    }
    "get" {
        if (-not $Path.StartsWith("/")) { $Path = "/$Path" }
        Invoke-RestMethod -Method Get -Uri "$baseUrl$Path" -Headers $headers
    }
    "post" {
        if (-not $Path.StartsWith("/")) { $Path = "/$Path" }
        Invoke-RestMethod -Method Post -Uri "$baseUrl$Path" -Headers $headers
    }
}
