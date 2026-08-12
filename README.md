# grok-actor

Switchable **actor / personality / tonality** presets for Grok Build.

**Not** the Grok voice-chat feature. This plugin only changes how the agent *acts* (persona, delivery, intensity).

## Why this exists

Grok already has:

- **Project rules** (`AGENTS.md` / `Claude.md`) — powerful but sticky and hard to A/B
- **Subagent personas** (`/personas`) — great for children, not the main session
- **Skills** — on-demand, not always sticky

`grok-actor` makes voice a first-class, testable plugin surface:

1. **Presets** in `presets/*.md`
2. **Active state** in plugin data + `~/.grok/rules/grok-actor-active.md`
3. **Hooks** re-inject on SessionStart / UserPromptSubmit
4. **Subagent persona** mirror at `~/.grok/personas/grok-actor-active.toml`
5. **`grok plugin validate` + unit tests** so changes stay honest

## Install

### From GitHub (recommended)

```powershell
grok plugin install Amnibro/grok-actor --trust
grok plugin enable grok-actor
```

Pin a release:

```powershell
grok plugin install Amnibro/grok-actor@v1.5.0 --trust
```

### Local (dev)

```powershell
cd C:\Users\antho\Documents\ai\grok-actor
.\install-local.ps1
```

Or:

```powershell
grok plugin install C:\Users\antho\Documents\ai\grok-actor --trust
grok plugin enable grok-actor
```

Reload the TUI (`/plugins` → `r`) or start a new session. Then: `/actor` or `/gactor`.
## Usage

```powershell
# list presets
python $env:USERPROFILE\.grok\plugins\grok-actor\scripts\actor_cli.py list

# activate (default scope = all sessions / global)
python $env:USERPROFILE\.grok\plugins\grok-actor\scripts\actor_cli.py set concise
python $env:USERPROFILE\.grok\plugins\grok-actor\scripts\actor_cli.py set mentor --intensity 0.6
python $env:USERPROFILE\.grok\plugins\grok-actor\scripts\actor_cli.py set --file .\my-voice.md

# scopes
python ...\actor_cli.py set trump --scope global    # all sessions (writes ~/.grok/rules)
python ...\actor_cli.py set pirate --scope session --session-id <id>  # this session only
python ...\actor_cli.py set yoda --scope chat       # this chat only (cleared on /clear)

# knobs
python $env:USERPROFILE\.grok\plugins\grok-actor\scripts\actor_cli.py intensity 0.3
python $env:USERPROFILE\.grok\plugins\grok-actor\scripts\actor_cli.py show
python $env:USERPROFILE\.grok\plugins\grok-actor\scripts\actor_cli.py clear
python $env:USERPROFILE\.grok\plugins\grok-actor\scripts\actor_cli.py clear --scope chat

# validate
python $env:USERPROFILE\.grok\plugins\grok-actor\scripts\actor_cli.py validate
```

### Scope

| Scope | Flag | Applies to | Touches global rules? |
|-------|------|------------|----------------------|
| **all sessions** | `--scope global` (default) | Every new session | Yes |
| **this session** | `--scope session` | Current `session_id` only | No |
| **this chat** | `--scope chat` | Until `/clear` / compact / new start | No |

Resolve order: **chat > session > global**.

In the TUI:

- `/actor` — picker, then **scope** popup (all sessions / this session / this chat)
- `/actor set concise --scope chat`
- `/actor intensity 0.4`
- Skill auto-triggers on “change tone / personality / voice”

After **global** `set`, start a **new session** or `/clear` so rules reload cleanly. Session/chat scopes inject via hooks without rewriting global rules.

## Built-in presets

| id | description |
|----|-------------|
| `neutral` | clear professional default |
| `concise` | minimal words |
| `mentor` | patient teacher |
| `formal` | documentation-grade |
| `playful` | light humor |
| `drill` | blunt high standards |
| `rikku` | FF X Rikku + Al Bhed + research-swing |
| `trump` | big punchy superlatives |
| `sherlock` | Holmesian deduction |
| `peasant` | 1400s muddy-boots commoner |
| `lord` | 1400s courtly noble |
| `noir` | 1940s private eye |
| `pirate` | seadog swagger |
| `shakespeare` | theatrical Elizabethan color |
| `cowboy` | dry Western drawl |
| `valley` | bright SoCal casual |
| `yoda` | inverted-syntax wisdom |
| `unhinged` | feral internet chaos (still correct) |
| `silentgen` | spare duty-first formal |
| `boomer` | classic boomer / dad energy |
| `genx` | dry Gen X sarcasm |
| `geny` | Gen Y classic millennial |
| `millennial` | elder-millennial Slack fluency |
| `genz` | Gen Z slang-forward |
| `gena` | Gen Alpha brainrot-lite |
| `corporate` | LinkedIn-core jargon |
| `surfer` | laid-back stoked |
| `sports` | play-by-play announcer |
| `professor` | warm lecture-hall |
| `hype` | launch-day hype beast |

## Intensity

| range | meaning |
|------:|---------|
| 0.0–0.49 | soft style guide |
| 0.5–0.79 | strong preference |
| 0.8–1.0 | mandatory unless user overrides |

Voice never beats safety, honesty, or explicit user instructions.

## Validate

```powershell
powershell -NoProfile -File $env:USERPROFILE\.grok\plugins\grok-actor\tests\run_tests.ps1
```

This runs:

1. unit tests (presets, CLI roundtrip, hook JSON shapes)
2. `actor_cli.py validate`
3. `grok plugin validate`

## Custom presets

Drop a markdown file in `presets/`:

```markdown
---
id: my-voice
name: My Voice
description: one-line summary
intensity_default: 0.7
---
# Voice: My Voice
Your instructions here.
```

Or activate any file without installing it:

```powershell
python ...\actor_cli.py set --file .\voices\customer-success.md
```

## Migration tip

If you hard-coded a persona in `~/.claude/Claude.md`, move that block into a preset (see `presets/rikku.md`), `set` it via this plugin, then remove or slim the global file so you can switch tones without editing home instructions.
