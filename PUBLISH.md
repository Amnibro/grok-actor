# Publishing grok-actor as a Grok marketplace / plugin item

## What "publish" means on Grok

Grok does **not** currently push community plugins to a single global xAI store from this CLI. Distribution works like this:

| Goal | How |
|------|-----|
| **You** get `/actor` on this machine | Local install (done via `install-local.ps1`) |
| **Teammates** install it | GitHub repo + `grok plugin install Amnibro/grok-actor --trust` |
| **Browseable marketplace** | Your own marketplace git repo with `marketplace.json` + `grok plugin marketplace add …` |
| Official Anthropic/xAI catalog | Separate process (PR to their public plugin repos if accepted) — not automatic |

## 1. Local install (slash commands on your PC)

```powershell
cd C:\Users\antho\Documents\ai\grok-actor
.\install-local.ps1
```

Or:

```powershell
grok plugin install C:\Users\antho\Documents\ai\grok-actor --trust
grok plugin enable grok-actor
```

User plugins live under `~/.grok/plugins/` and are trusted. Restart the TUI or run `/plugins` → reload (`r`).

Then:

```
/actor
/gactor
/actor-list
/actor-set trump --scope global
```

## 2. Publish for others (GitHub)

1. Create a public repo: `Amnibro/grok-actor`.
2. Push **this directory** as the repo root (includes `.claude-plugin/plugin.json`, `skills/`, `commands/`, `hooks/`, `presets/`, `scripts/`).
3. `.claude-plugin/plugin.json` → `homepage`: `https://github.com/Amnibro/grok-actor`.
4. Tag a release:

```powershell
cd C:\Users\antho\Documents\ai\grok-actor
git init   # if needed
git add .
git commit -m "grok-actor v1.5.0"
git tag v1.5.0
git remote add origin https://github.com/Amnibro/grok-actor.git
git push -u origin main --tags
```

Others install:

```bash
grok plugin install Amnibro/grok-actor --trust
grok plugin enable grok-actor
```

Or pin a version:

```bash
grok plugin install Amnibro/grok-actor@v1.5.0 --trust
```

Validate before push:

```bash
grok plugin validate .
powershell -NoProfile -File .\tests\run_tests.ps1
```

## 3. Personal marketplace catalog

Repo: `C:\Users\antho\Documents\ai\marketplace\grok-remote-market` (catalog name: **anthony-grok-plugins**).

```json
{
  "name": "grok-actor",
  "version": "1.5.0",
  "description": "Switchable actor/personality presets for Grok Build…",
  "source": {
    "source": "url",
    "url": "https://github.com/Amnibro/grok-actor.git"
  },
  "homepage": "https://github.com/Amnibro/grok-actor"
}
```

Users:

```bash
grok plugin marketplace add C:\Users\antho\Documents\ai\marketplace\grok-remote-market
# or when the marketplace is on GitHub:
# grok plugin marketplace add Amnibro/anthony-grok-plugins
grok plugin install grok-actor --trust
```

Then install from the Marketplace tab (`/marketplace`) or CLI.

## 4. After install — how people use it

1. In Grok TUI: `/actor` (or `/gactor`)
2. Pick a persona from the popup
3. Pick **scope**: all sessions / this session / this chat
4. New session or `/clear` if you chose global (rules reload)

## Checklist

- [x] `plugin.json` name `grok-actor`
- [x] Skills `skills/actor`, `skills/gactor`
- [x] Commands `commands/actor-list.md`, `actor-set.md`
- [x] Hooks SessionStart + UserPromptSubmit
- [x] Presets + CLI `scripts/actor_cli.py`
- [x] Scope: global | session | chat
- [x] Push to GitHub `Amnibro/grok-actor`
- [x] Marketplace entry (url source)
- [x] `grok plugin validate` clean
- [ ] Fresh TUI: `/actor` works (user confirm)
