---
name: gactor
description: "Alias for /actor — switch Grok Build personality presets (grok-actor plugin). Use when /actor is hard to find."
argument-hint: "[list|show|set <preset> [--scope global|session|chat]|intensity <0-1>|clear|validate]"
user-invocable: false
disable-model-invocation: false
metadata:
  short-description: Alias for /actor personality switcher
  version: "1.5.0"
---
# /gactor
Same as `/actor`. Follow the **actor** skill exactly (popup picker; invent; **scope picker** global/session/chat; `invent --set --scope …`).
Arguments: $ARGUMENTS
