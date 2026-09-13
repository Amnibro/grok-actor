## 2026-08-20 — Windows silent-death fix + washington preset
- inject_actor.py: emit() used ensure_ascii=False; on a cp1252 stdout (any non-UTF-8 hook runner, e.g. Claude Code on Windows) json.dumps raised UnicodeEncodeError inside the bare except and the hook emitted NOTHING, silently. ensure_ascii=True — JSON-escaped, safe on every codepage. Backup: hooks/inject_actor.py.pre-utf8.bak.
- New preset presets/washington.md — George Washington: measured, composed, plainly decisive; candor over comfort.
- Wired into Claude Code (~/.claude/settings.json hooks: SessionStart + UserPromptSubmit, exec-form argv) so every Claude session gets the cadence ban + active actor by default.

# Changelog — grok-actor

## 1.5.1 — 2026-08-12
- Published like grok-remote: `https://github.com/Amnibro/grok-actor` (public), tag `v1.5.0`, `install-local.ps1`, `PUBLISH.md`, MIT LICENSE
- Marketplace catalog points at GitHub URL (same pattern as grok-remote)
- Canonical source tree: `Documents/ai/grok-actor`

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
