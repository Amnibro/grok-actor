from pathlib import Path
home=Path.home()
actor_skill=home/".grok"/"skills"/"actor"/"SKILL.md"
actor_skill.parent.mkdir(parents=True,exist_ok=True)
actor_skill.write_text("""---
name: actor
description: Switch Grok Build actor/personality presets for default chats (not voice-chat). Use for /actor set genz, /actor list, tone, persona.
argument-hint: \"[list|show|set PRESET|intensity 0-1|clear|validate]\"
user-invocable: true
disable-model-invocation: false
allowed-tools: [Bash, Read]
metadata:
  short-description: Switch actor/personality presets
  version: \"1.2.1\"
---
# /actor
Switch the active **actor** (persona) for default chats via the grok-actor plugin. Not voice-chat.
## Arguments
- empty or list: list presets
- show: active actor
- set PRESET: activate (e.g. set genz, set trump, set unhinged)
- intensity 0-1: scale active actor
- clear: remove active actor
- validate: validate catalog
## Run
```powershell
$PLUGIN = if ($env:GROK_PLUGIN_ROOT) { $env:GROK_PLUGIN_ROOT } else { \"$env:USERPROFILE\\.grok\\plugins\\grok-actor\" }
$CLI = Join-Path $PLUGIN \"scripts\\actor_cli.py\"
if (-not (Test-Path $CLI)) {
  $hit = Get-ChildItem \"$env:USERPROFILE\\.grok\\installed-plugins\" -Recurse -Filter actor_cli.py -EA SilentlyContinue | Select-Object -First 1
  if ($hit) { $CLI = $hit.FullName; $PLUGIN = $hit.Directory.Parent.FullName }
}
$env:GROK_PLUGIN_ROOT = $PLUGIN
$ARGS = \"$ARGUMENTS\".Trim()
if (-not $ARGS) { python $CLI list; python $CLI show; return }
python $CLI ($ARGS -split '\\s+')
```
After set: new session or /clear. End with active preset + intensity.
""",encoding="utf-8",newline="\n")
cmds=home/".grok"/"commands"
cmds.mkdir(parents=True,exist_ok=True)
(cmds/"actor-list.md").write_text("""---
description: List Grok Build actors and show the active one (grok-actor). Not voice-chat.
argument-hint: \"\"
user-invocable: true
allowed-tools: [Bash]
---
# /actor-list
```powershell
$PLUGIN = if ($env:GROK_PLUGIN_ROOT) { $env:GROK_PLUGIN_ROOT } else { \"$env:USERPROFILE\\.grok\\plugins\\grok-actor\" }
$env:GROK_PLUGIN_ROOT = $PLUGIN
python (Join-Path $PLUGIN \"scripts\\actor_cli.py\") list
python (Join-Path $PLUGIN \"scripts\\actor_cli.py\") show
```
""",encoding="utf-8",newline="\n")
(cmds/"actor-set.md").write_text("""---
description: Set Grok Build default-chat actor. Example /actor-set genz or /actor-set trump. Not voice-chat.
argument-hint: \"PRESET [--intensity 0-1]\"
user-invocable: true
allowed-tools: [Bash]
---
# /actor-set
```powershell
$PLUGIN = if ($env:GROK_PLUGIN_ROOT) { $env:GROK_PLUGIN_ROOT } else { \"$env:USERPROFILE\\.grok\\plugins\\grok-actor\" }
$env:GROK_PLUGIN_ROOT = $PLUGIN
$ARGS = \"$ARGUMENTS\".Trim()
if (-not $ARGS) { Write-Output \"Usage: /actor-set PRESET\"; python (Join-Path $PLUGIN \"scripts\\actor_cli.py\") list; return }
python (Join-Path $PLUGIN \"scripts\\actor_cli.py\") set ($ARGS -split '\\s+')
python (Join-Path $PLUGIN \"scripts\\actor_cli.py\") show
```
""",encoding="utf-8",newline="\n")
g=home/".grok"/"skills"/"gactor"/"SKILL.md"
g.parent.mkdir(parents=True,exist_ok=True)
g.write_text("""---
name: gactor
description: Alias for /actor — switch Grok Build personality presets when /actor is hard to find.
argument-hint: \"[list|show|set PRESET|clear]\"
user-invocable: true
metadata:
  short-description: Alias for /actor
---
# /gactor
Same as /actor. Arguments: $ARGUMENTS
```powershell
$PLUGIN = if ($env:GROK_PLUGIN_ROOT) { $env:GROK_PLUGIN_ROOT } else { \"$env:USERPROFILE\\.grok\\plugins\\grok-actor\" }
$CLI = Join-Path $PLUGIN \"scripts\\actor_cli.py\"
$ARGS = \"$ARGUMENTS\".Trim()
if (-not $ARGS) { python $CLI list; python $CLI show } else { python $CLI ($ARGS -split '\\s+') }
```
""",encoding="utf-8",newline="\n")
ps=home/".grok"/"plugins"/"grok-actor"/"skills"/"actor"/"SKILL.md"
if ps.exists():
 t=ps.read_text(encoding="utf-8")
 t=t.replace("user-invocable: true","user-invocable: false")
 ps.write_text(t,encoding="utf-8",newline="\n")
 print("plugin actor skill user-invocable=false")
pc=home/".grok"/"plugins"/"grok-actor"/"commands"
for name in ("actor-list.md","actor-set.md"):
 (pc/name).write_text((cmds/name).read_text(encoding="utf-8"),encoding="utf-8",newline="\n")
pa=pc/"actor.md"
if pa.exists():
 pa.unlink();print("removed plugin commands/actor.md")
pg=home/".grok"/"plugins"/"grok-actor"/"skills"/"gactor"/"SKILL.md"
if pg.exists():
 t=pg.read_text(encoding="utf-8")
 t=t.replace("user-invocable: true","user-invocable: false")
 pg.write_text(t,encoding="utf-8",newline="\n")
print("ok",actor_skill,"bom",actor_skill.read_bytes()[:3])
