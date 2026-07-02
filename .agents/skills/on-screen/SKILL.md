---
name: on-screen
description: Open the most recent working file in Visual Studio Code when the user says "On Screen", "on screen", "put it on screen", "open it in VS Code", or asks to show the current/last working file in Visual Code or Visual Studio Code.
---

# On Screen

## Workflow

When the user asks for "On Screen", open the best current working file in Visual Studio Code.

1. Choose the target file from the current conversation context:
   - Prefer a file the user explicitly names in the request.
   - Otherwise use the most recently created, edited, or discussed project file.
   - If the IDE context names an active file and it matches the recent work, use that.
   - If there is no clear target, make a reasonable guess from the last repo change; ask only when multiple choices would be risky.
2. Open the file without printing its contents. This matters for files such as `.secrets.json`.
3. Use the VS Code CLI when available:

```powershell
$path = Resolve-Path -LiteralPath "relative\or\absolute\file"
if (Get-Command code.cmd -ErrorAction SilentlyContinue) {
    & code.cmd -r $path
} elseif (Get-Command code -ErrorAction SilentlyContinue) {
    & code -r $path
} else {
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe",
        "$env:ProgramFiles\Microsoft VS Code\Code.exe",
        "${env:ProgramFiles(x86)}\Microsoft VS Code\Code.exe"
    )
    $exe = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if ($null -eq $exe) {
        throw "VS Code executable was not found."
    }
    Start-Process -FilePath $exe -ArgumentList @("-r", $path)
}
```

4. Briefly tell the user which file was opened, or that VS Code could not be found.
