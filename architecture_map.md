# grok-actor architecture_map

## Version
1.5.0 — 2026-08-12

## Purpose
Switchable actor/personality presets for Grok Build default chats (not voice-chat).

## Surfaces
| Surface | Path | Role |
|---------|------|------|
| CLI | `scripts/actor_cli.py` | list/show/set/invent/intensity/clear/validate |
| Inject hook | `hooks/inject_actor.py` | SessionStart + UserPromptSubmit context |
| Hook runner | `hooks/run-hook.cmd` | Windows python launcher |
| Hooks config | `hooks/hooks.json` | event wiring |
| Presets | `presets/*.md` | bundled actors |
| Custom presets | `~/.grok/plugin-data/grok-actor/custom-presets/` | invent output |
| Skills | `skills/actor`, `skills/gactor` + `~/.grok/skills/*` | `/actor` `/gactor` |
| Commands | `commands/actor-list.md`, `actor-set.md` | thin wrappers |

## Scope model (v1.5)
| Scope | Persist | Storage | Cleared when |
|-------|---------|---------|--------------|
| `global` (all sessions) | Yes | `active.json` + `~/.grok/rules/grok-actor-active.md` + persona toml | `clear` / new global set |
| `session` | This session_id | `sessions/{session_id}.json` | session ends / clear --scope session |
| `chat` | Until clear | `chat-override.json` | SessionStart (startup\|clear\|compact) / clear --scope chat |

### Resolve order (inject)
1. chat-override.json
2. sessions/{session_id}.json (session_id from hook stdin or last-session.json)
3. active.json (global)
4. rules file fallback (legacy)

### last-session.json
Hook writes `{session_id, conversation_id?, ts}` so CLI can `set --scope session` mid-chat without the user pasting an id.

## Data dir
`GROK_PLUGIN_DATA` / `CLAUDE_PLUGIN_DATA` or `~/.grok/plugin-data/grok-actor/`

## Intensity
0–0.49 soft · 0.5–0.79 strong · 0.8–1.0 mandatory (still never beats safety/honesty/user overrides)
