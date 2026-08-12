# Checklist: grok-actor plugin v1.1

- [x] Rename plugin grok-voice → grok-actor (no voice-chat collision)
- [x] Manifest name `grok-actor` v1.1.0
- [x] CLI `scripts/actor_cli.py`
- [x] Skill `/actor`, command `commands/actor.md`
- [x] Rules `grok-actor-active.md`, persona `grok-actor-active.toml`
- [x] Hooks inject_actor.py + tags GROK_ACTOR_ACTIVE
- [x] Uninstall old grok-voice; remove source tree
- [x] Install+enable grok-actor
- [x] Strip persona from `~/.claude/CLAUDE.md`
- [x] Grok `[compat.claude] agents=false rules=false`
- [x] Engineering rules in `~/.grok/rules/amni-engineering.md`
- [x] Rikku preset = copilot cipher + research hard override
- [x] Activate rikku @ 0.95
- [x] 11/11 tests + grok plugin validate
- [x] architecture_map + changelog
