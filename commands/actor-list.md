---
description: List Grok Build actors and show the active one (grok-actor). Not voice-chat.
argument-hint: ""
user-invocable: true
allowed-tools: [Bash]
---
# /actor-list
```powershell
$PLUGIN = if ($env:GROK_PLUGIN_ROOT) { $env:GROK_PLUGIN_ROOT } else { "$env:USERPROFILE\.grok\plugins\grok-actor" }
$env:GROK_PLUGIN_ROOT = $PLUGIN
python (Join-Path $PLUGIN "scripts\actor_cli.py") list
python (Join-Path $PLUGIN "scripts\actor_cli.py") show
```
