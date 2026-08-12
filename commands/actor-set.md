---
description: Set Grok Build actor. Example /actor-set genz or /actor-set trump --scope chat. Not voice-chat.
argument-hint: "PRESET [--intensity 0-1] [--scope global|session|chat]"
user-invocable: true
allowed-tools: [Bash]
---
# /actor-set
```powershell
$PLUGIN = if ($env:GROK_PLUGIN_ROOT) { $env:GROK_PLUGIN_ROOT } else { "$env:USERPROFILE\.grok\plugins\grok-actor" }
$env:GROK_PLUGIN_ROOT = $PLUGIN
$ARGS = "$ARGUMENTS".Trim()
if (-not $ARGS) { Write-Output "Usage: /actor-set PRESET [--scope global|session|chat]"; python (Join-Path $PLUGIN "scripts\actor_cli.py") list; return }
python (Join-Path $PLUGIN "scripts\actor_cli.py") set ($ARGS -split '\s+')
python (Join-Path $PLUGIN "scripts\actor_cli.py") show
```
