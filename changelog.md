# Changelog — grok-actor

## 1.5.1 — 2026-08-12
- Listed in local marketplace `anthony-grok-plugins` (`marketplace/grok-remote-market`) with `plugin-index.json` catalog

## 1.5.0 — 2026-08-12
- **Scope:** `global` (all sessions), `session` (this session_id), `chat` (this chat until clear)
- CLI: `set/invent/intensity/clear --scope …` and `--session-id`
- State layers: `active.json`, `sessions/{id}.json`, `chat-override.json`, `last-session.json`
- Inject: priority chat > session > global; remember session_id; clear chat on SessionStart
- `/actor` skill: second popup for scope after preset pick
- Tests for layered resolve + chat clear on session start
- Version bump plugin.json + skills to 1.5.0

## 1.4.0 — prior
- Interactive picker, invent unknown personas, custom presets
