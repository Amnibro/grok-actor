---
name: actor
description: Switch Grok Build actor/personality presets for default chats (not voice-chat). Use for /actor, /actor set, invent custom personas, tone, persona. Opens interactive picker when run with no args. Builds unknown personas on request. Supports scope: all sessions, this session, or this chat.
argument-hint: "[set PRESET [--scope global|session|chat]|invent NAME|list|show|intensity 0-1|clear [--scope all|global|session|chat]|validate]"
user-invocable: false
disable-model-invocation: false
allowed-tools: [Bash, Read, WebSearch, WebFetch]
metadata:
  short-description: Actor picker + invent + scope (global/session/chat)
  version: "1.5.0"
---
# /actor
Switch the active **actor** (persona) for default chats via grok-actor. **Not** voice-chat.
## Resolve plugin
```powershell
$PLUGIN = if ($env:GROK_PLUGIN_ROOT) { $env:GROK_PLUGIN_ROOT } else { "$env:USERPROFILE\.grok\plugins\grok-actor" }
$CLI = Join-Path $PLUGIN "scripts\actor_cli.py"
if (-not (Test-Path $CLI)) {
  $hit = Get-ChildItem "$env:USERPROFILE\.grok\installed-plugins" -Recurse -Filter actor_cli.py -EA SilentlyContinue | Select-Object -First 1
  if ($hit) { $CLI = $hit.FullName; $PLUGIN = $hit.Directory.Parent.FullName }
}
$env:GROK_PLUGIN_ROOT = $PLUGIN
```
## Scope (required choice after picking an actor)
| Scope | CLI flag | Meaning |
|-------|----------|---------|
| **all sessions** | `--scope global` (default) | Default for every new session. Writes `~/.grok/rules`. |
| **this session** | `--scope session` | Only this session_id. Does **not** change other sessions or global rules. Needs last-session from hooks or `--session-id`. |
| **this chat** | `--scope chat` | Until `/clear`, compact, or new session start. Highest priority. Does **not** rewrite global rules. |
Priority when several are set: **chat > session > global**.
## CRITICAL — interactive picker (empty args)
When `$ARGUMENTS` is empty or is `list` / `pick` / `menu`:
1. `python $CLI show` (context only — do not dump the full catalog as chat text).
2. **Immediately** call `ask_user_question` (popup). Options:
   - First: `keep` (Recommended if unsure)
   - Popular bundled ids (`neutral`, `concise`, `rikku`, `genz`, `unhinged`, `sherlock`, `trump`, …)
   - Custom presets from `python $CLI list` marked `[custom]`
   - **`custom`** — "Not listed — invent a new actor from a name/description"
   - Last: `clear`
3. Handle answer:
   - `keep` → show active, done
   - `clear` → second popup for clear scope (`all` / `global` / `session` / `chat`), then `python $CLI clear --scope <…>`
   - known id or invent result → **SCOPE PICKER** (below), then set/invent
   - **`custom`** → invent flow, then **SCOPE PICKER** before `--set`
## CRITICAL — scope picker (after preset chosen)
Unless user already passed `--scope` / `global` / `session` / `chat` in args, call `ask_user_question`:
1. **`all sessions`** (Recommended) — default for every session (`--scope global`)
2. **`this session only`** — `--scope session`
3. **`this chat only`** — `--scope chat` (cleared on /clear)
Then run:
```powershell
python $CLI set <id> --scope global|session|chat
```
If session scope fails with "session id", say: send any message first (hook records session) or pass `--session-id`, then retry.
## CRITICAL — invent unknown persona
Trigger invent when any of:
- User picks `custom` in the popup
- Args are `invent <name…>` or `set <name>` / bare `<name>` and `python $CLI has <slug>` returns no / exit 1
- `python $CLI set <name>` exits **3** with `UNKNOWN_PRESET`
### Invent steps (do all)
1. Parse the requested persona string (character, celebrity style, vibe, era, fictional role, etc.).
2. **Research** with tools when helpful: `web_search` / `web_fetch` for speech patterns, catchphrases, register, public persona traits. Prefer primary characterizations over parody extremes.
3. Build a **speech-style actor body** (not a biography dump). Include:
   - cadence / vocabulary / attitude
   - 4–8 concrete style rules
   - what to avoid (caricature spam, unsafe content)
   - hard line: still ship correct code, honest metrics; persona never overrides safety
4. Write a body-only markdown file (no need for frontmatter in body) to a temp path, e.g. `%TEMP%\grok-actor-invent.md`.
5. Run **SCOPE PICKER** (unless `--scope` already in args).
6. Save + activate:
```powershell
python $CLI invent --id <slug> --name "<Display Name>" --description "<one-line>" --body-file $bodyPath --intensity 0.85 --set --scope global|session|chat
```
   - `slug` = lowercase hyphenated (`doctor-who`, `snoop`, `victorian-nanny`)
7. Show active + path. Remind by scope:
   - global → **new session or `/clear`**
   - session → this session only; other sessions unchanged
   - chat → this chat only until `/clear`
Custom presets live under plugin data `custom-presets/` and appear in future pickers as `[custom]`.
### Invent quality bar
- Sound like the **person talking**, not a Wikipedia entry
- Specific beats over vague "be cool"
- No hate/harassment personas; refuse and offer a safe alternative
- No claiming private facts about living people; public speaking style only
## Direct args
| Args | Action |
|------|--------|
| `set PRESET` | activate; then scope picker if `--scope` missing |
| `set PRESET --scope global\|session\|chat` | activate with scope |
| `invent NAME…` | force invent for NAME |
| `show` | effective + global/session/chat layers |
| `intensity N` | 0–1 on effective layer (or `--scope`) |
| `clear` | clear all layers |
| `clear --scope global\|session\|chat` | clear one layer |
| `validate` | validate catalog |
| `list text` | plain-text catalog |
Never claim invent/set succeeded without running the CLI. Never skip the popup when args are empty. Never skip the **scope picker** when setting without an explicit `--scope`.
