#!/usr/bin/env python3
from __future__ import annotations
import json,os,re,sys
from pathlib import Path
ROOT=Path(os.environ.get("GROK_PLUGIN_ROOT") or Path(__file__).resolve().parents[1])
PRESETS=ROOT/"presets"
FM_RE=re.compile(r"^---\s*\n(.*?)\n---",re.S)
def data_dir()->Path:
 d=os.environ.get("GROK_PLUGIN_DATA") or os.environ.get("CLAUDE_PLUGIN_DATA")
 return Path(d) if d else Path.home()/".grok"/"plugin-data"/"grok-actor"
def parse(path:Path)->dict:
 text=path.read_text(encoding="utf-8");m=FM_RE.match(text);meta={}
 if m:
  for line in m.group(1).splitlines():
   if ":" not in line:continue
   k,v=line.split(":",1);meta[k.strip()]=v.strip()
 pid=meta.get("id") or path.stem
 return {"id":pid,"name":meta.get("name",pid),"description":meta.get("description","")}
def main()->int:
 opts=[];seen=set()
 custom=data_dir()/"custom-presets"
 if custom.exists():
  for p in sorted(custom.glob("*.md")):
   try:pr=parse(p)
   except Exception:continue
   if pr["id"] in seen:continue
   opts.append({"label":pr["id"],"description":f"[custom] {pr['name']}: {pr['description']}"})
   seen.add(pr["id"])
 for p in sorted(PRESETS.glob("*.md")):
  try:pr=parse(p)
  except Exception:continue
  if pr["id"] in seen:continue
  opts.append({"label":pr["id"],"description":f"{pr['name']}: {pr['description']}"})
  seen.add(pr["id"])
 head=[{"label":"keep","description":"Keep current active actor (no change)"},{"label":"custom","description":"Not listed — invent a new actor from a name/description (research + build)"}]
 tail=[{"label":"clear","description":"Clear active actor (no persona overlay)"}]
 print(json.dumps({"presets":head+opts+tail,"count":len(head)+len(opts)+len(tail)},indent=2))
 return 0
if __name__=="__main__":sys.exit(main())
