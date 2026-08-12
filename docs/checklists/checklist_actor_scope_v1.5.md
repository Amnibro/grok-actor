# Checklist: actor scope global|session|chat v1.5

- [x] Backup CLI, inject, skills, tests, README, plugin.json
- [x] CLI: `--scope global|session|chat` (+ aliases all/default/this-session/this-chat)
- [x] Layered state: active.json / sessions/{id}.json / chat-override.json
- [x] last-session.json written by inject for mid-session `set --scope session`
- [x] Inject priority: chat > session > global; clear chat on SessionStart
- [x] `show` prints layers + effective; `clear --scope`
- [x] Skill: second popup for scope after preset pick
- [x] invent --set respects --scope
- [x] Tests for scopes + inject resolution
- [x] Version 1.5.0, architecture_map, changelog, README
- [x] Run unit tests + validate (17/17 + plugin validate)
- [x] Sync ~/.grok/skills actor + gactor + installed-plugins
- [ ] User confirms working
