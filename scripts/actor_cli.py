#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,re,sys,tempfile,time
from pathlib import Path
ROOT=Path(os.environ.get("GROK_PLUGIN_ROOT") or Path(__file__).resolve().parents[1])
PRESETS=ROOT/"presets"
FM_RE=re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$",re.S)
ID_RE=re.compile(r"^[a-z0-9][a-z0-9-]{0,62}[a-z0-9]$|^[a-z0-9]$")
SCOPE_ALIASES={"all":"global","default":"global","global":"global","session":"session","this-session":"session","this_session":"session","chat":"chat","this-chat":"chat","this_chat":"chat","conversation":"chat"}
def data_dir()->Path:
 d=os.environ.get("GROK_PLUGIN_DATA") or os.environ.get("CLAUDE_PLUGIN_DATA")
 p=Path(d) if d else Path.home()/".grok"/"plugin-data"/"grok-actor"
 p.mkdir(parents=True,exist_ok=True);return p
def custom_dir()->Path:
 p=data_dir()/"custom-presets";p.mkdir(parents=True,exist_ok=True);return p
def rules_path()->Path:
 p=Path.home()/".grok"/"rules";p.mkdir(parents=True,exist_ok=True);return p/"grok-actor-active.md"
def persona_path()->Path:
 p=Path.home()/".grok"/"personas";p.mkdir(parents=True,exist_ok=True);return p/"grok-actor-active.toml"
def active_path()->Path:return data_dir()/"active.json"
def chat_path()->Path:return data_dir()/"chat-override.json"
def last_session_path()->Path:return data_dir()/"last-session.json"
def sessions_dir()->Path:
 p=data_dir()/"sessions";p.mkdir(parents=True,exist_ok=True);return p
def session_path(sid:str)->Path:
 safe=re.sub(r"[^a-zA-Z0-9._-]+","_",sid.strip())[:128] or "unknown"
 return sessions_dir()/f"{safe}.json"
def slugify(name:str)->str:
 s=re.sub(r"[^a-z0-9]+","-",name.strip().lower());s=re.sub(r"-+","-",s).strip("-")
 return s[:64] or "custom"
def normalize_scope(s:str|None)->str:
 if not s:return "global"
 k=s.strip().lower()
 return SCOPE_ALIASES.get(k) or (k if k in ("global","session","chat") else "global")
def parse_preset(path:Path,scope:str="bundled")->dict:
 text=path.read_text(encoding="utf-8");m=FM_RE.match(text)
 if not m:raise ValueError(f"missing frontmatter: {path.name}")
 meta,body={},m.group(2).strip()
 for line in m.group(1).splitlines():
  if ":" not in line:continue
  k,v=line.split(":",1);meta[k.strip()]=v.strip()
 pid=meta.get("id") or path.stem
 return {"id":pid,"name":meta.get("name",pid),"description":meta.get("description",""),"intensity_default":float(meta.get("intensity_default","0.7")),"body":body,"path":str(path),"raw":text,"scope":scope}
def list_presets()->list[dict]:
 out=[];seen=set()
 for p in sorted(custom_dir().glob("*.md")):
  try:pr=parse_preset(p,"custom")
  except ValueError:continue
  if pr["id"] in seen:continue
  out.append(pr);seen.add(pr["id"])
 for p in sorted(PRESETS.glob("*.md")):
  try:pr=parse_preset(p,"bundled")
  except ValueError:continue
  if pr["id"] in seen:continue
  out.append(pr);seen.add(pr["id"])
 return sorted(out,key=lambda x:x["id"])
def load_preset(name:str)->dict:
 key=name.strip().lower()
 for p in list_presets():
  if p["id"]==key or p["name"].lower()==key:return p
 raise FileNotFoundError(f"unknown preset: {name}")
def has_preset(name:str)->bool:
 try:load_preset(name);return True
 except FileNotFoundError:return False
def read_json(path:Path)->dict|None:
 return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
def load_global()->dict|None:return read_json(active_path())
def load_chat()->dict|None:return read_json(chat_path())
def load_session(sid:str|None)->dict|None:
 return read_json(session_path(sid)) if sid else None
def load_last_session()->dict|None:return read_json(last_session_path())
def resolve_session_id(explicit:str|None=None)->str|None:
 if explicit and explicit.strip():return explicit.strip()
 env=os.environ.get("GROK_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID")
 if env and env.strip():return env.strip()
 last=load_last_session()
 return str(last["session_id"]) if last and last.get("session_id") else None
def load_active()->dict|None:
 sid=resolve_session_id()
 chat=load_chat()
 if chat:return {**chat,"_layer":"chat","_effective":True}
 sess=load_session(sid)
 if sess:return {**sess,"_layer":"session","_effective":True,"session_id":sid}
 g=load_global()
 return {**g,"_layer":"global","_effective":True} if g else None
def intensity_banner(level:float)->str:
 return "MANDATORY — follow for every response." if level>=0.8 else ("STRONG preference — follow unless the user overrides." if level>=0.5 else "Soft style guide — prefer this tone when it does not conflict with clearer instructions.")
def render_block(preset_id:str,name:str,body:str,level:float,source:str,scope:str="global")->str:
 return "\n".join(["# Grok Actor (active)",f"<!-- managed by grok-actor plugin; do not hand-edit -->",f"preset: {preset_id} ({name})",f"intensity: {level:.2f}",f"scope: {scope}",f"source: {source}","",f"**{intensity_banner(level)}**","",body.strip(),"",f"Intensity {level:.2f}: scale how hard you lean into the voice. Higher = more consistent persona. Lower = lighter touch. Never violate safety, honesty, or user-explicit overrides."])
def atomic_write(path:Path,text:str)->None:
 path.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(dir=str(path.parent),prefix=path.name+".",suffix=".tmp")
 try:
  with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as f:f.write(text)
  os.replace(tmp,path)
 except Exception:
  try:os.unlink(tmp)
  except OSError:pass
  raise
def write_persona(preset_id:str,name:str,body:str,level:float)->None:
 desc=f"Grok Actor active overlay: {name}"
 instr=body.replace("\\","\\\\").replace('"""','\\"\\"\\"')
 toml="\n".join([f'description = "{desc}"',f'instructions = """',f"# Voice overlay: {name} (intensity {level:.2f})",intensity_banner(level),instr,'"""',""])
 atomic_write(persona_path(),toml)
def activate(preset:dict,level:float|None,source:str,scope:str="global",session_id:str|None=None)->dict:
 sc=normalize_scope(scope)
 lvl=float(level if level is not None else preset["intensity_default"]);lvl=max(0.0,min(1.0,lvl))
 state={"preset":preset["id"],"name":preset["name"],"intensity":lvl,"source":source,"body":preset["body"],"scope":sc,"updated_at":time.time()}
 if sc=="global":
  atomic_write(active_path(),json.dumps(state,indent=2)+"\n")
  atomic_write(rules_path(),render_block(preset["id"],preset["name"],preset["body"],lvl,source,sc)+"\n")
  write_persona(preset["id"],preset["name"],preset["body"],lvl)
  return state
 if sc=="chat":
  atomic_write(chat_path(),json.dumps(state,indent=2)+"\n");return state
 sid=resolve_session_id(session_id)
 if not sid:raise RuntimeError("session scope needs a session id (hook last-session, GROK_SESSION_ID, or --session-id)")
 state["session_id"]=sid
 atomic_write(session_path(sid),json.dumps(state,indent=2)+"\n")
 return state
def clear_scope(scope:str="all",session_id:str|None=None)->list[str]:
 sc=scope.strip().lower() if scope else "all"
 cleared=[]
 if sc in ("all","global","default"):
  for p in (active_path(),rules_path(),persona_path()):
   if p.exists():p.unlink();cleared.append(str(p))
 if sc in ("all","chat","this-chat","this_chat","conversation"):
  p=chat_path()
  if p.exists():p.unlink();cleared.append(str(p))
 if sc in ("all","session","this-session","this_session"):
  sid=resolve_session_id(session_id)
  if sid:
   p=session_path(sid)
   if p.exists():p.unlink();cleared.append(str(p))
  elif sc=="all":
   sd=sessions_dir()
   if sd.exists():
    for p in sd.glob("*.json"):p.unlink();cleared.append(str(p))
 return cleared
def write_custom_preset(pid:str,name:str,description:str,body:str,intensity:float=0.85)->Path:
 pid=slugify(pid)
 if not ID_RE.match(pid):raise ValueError(f"invalid id: {pid}")
 body=body.strip()
 if not body:raise ValueError("empty body")
 text="\n".join(["---",f"id: {pid}",f"name: {name}",f"description: {description}",f"intensity_default: {intensity:.2f}","---",f"# Actor: {name}",body,""])
 path=custom_dir()/f"{pid}.md"
 atomic_write(path,text)
 return path
def cmd_list(_:argparse.Namespace)->int:
 for p in list_presets():
  tag="[custom]" if p.get("scope")=="custom" else "        "
  print(f"{p['id']:14}  {p['name'][:16]:16}  i={p['intensity_default']:.2f}  {tag}  {p['description']}")
 return 0
def cmd_show(_:argparse.Namespace)->int:
 sid=resolve_session_id();chat=load_chat();sess=load_session(sid);glob=load_global();eff=load_active()
 if not eff and not glob and not chat and not sess:print("active: none");return 0
 if eff:print(f"effective: {eff['preset']} ({eff.get('name',eff['preset'])}) intensity={eff.get('intensity',0):.2f} scope={eff.get('_layer') or eff.get('scope','global')} source={eff.get('source','?')}")
 print(f"global: {glob['preset']} i={glob.get('intensity',0):.2f}" if glob else "global: none")
 print(f"session: {sess['preset']} i={sess.get('intensity',0):.2f} id={sid}" if sess and sid else (f"session: none (id={sid or 'unknown'})"))
 print(f"chat: {chat['preset']} i={chat.get('intensity',0):.2f}" if chat else "chat: none")
 if eff:print(eff.get("body",""))
 return 0
def cmd_has(ns:argparse.Namespace)->int:
 ok=has_preset(ns.preset)
 print("yes" if ok else "no");return 0 if ok else 1
def cmd_set(ns:argparse.Namespace)->int:
 if ns.file:
  path=Path(ns.file).expanduser().resolve();preset=None;source="inline"
  if path.exists():
   source=str(path)
   try:preset=parse_preset(path,"custom" if "custom-presets" in str(path) else "file")
   except ValueError:preset=None
   if preset is None:
    body=path.read_text(encoding="utf-8")
    preset={"id":"custom","name":"Custom","description":"user custom","intensity_default":0.7,"body":body,"path":source,"raw":""}
  else:
   preset={"id":"custom","name":"Custom","description":"user custom","intensity_default":0.7,"body":ns.file,"path":"inline","raw":""}
 else:
  try:preset=load_preset(ns.preset);source=preset["path"]
  except FileNotFoundError:
   print(f"UNKNOWN_PRESET: {ns.preset}",file=sys.stderr)
   print("INVENT: research this persona and run: invent --id <slug> --name <Name> --description <desc> --body-file <md> [--set] [--scope global|session|chat]",file=sys.stderr)
   return 3
 sc=normalize_scope(ns.scope)
 try:st=activate(preset,ns.intensity,source,sc,ns.session_id)
 except RuntimeError as e:print(str(e),file=sys.stderr);return 2
 print(f"set: {st['preset']} intensity={st['intensity']:.2f} scope={st['scope']}"+(f" session_id={st['session_id']}" if st.get("session_id") else ""))
 if sc=="global":
  print(f"rules: {rules_path()}")
  print("note: all sessions pick this up via ~/.grok/rules; mid-session restart or /clear recommended.")
 elif sc=="session":
  print("note: this session only (override). Other sessions keep the global default. Does not rewrite ~/.grok/rules.")
 else:
  print("note: this chat only. Cleared on /clear, compact, or new session start. Does not rewrite ~/.grok/rules.")
 return 0
def cmd_invent(ns:argparse.Namespace)->int:
 body=Path(ns.body_file).expanduser().read_text(encoding="utf-8") if ns.body_file else (sys.stdin.read() if not sys.stdin.isatty() else "")
 if ns.body:body=ns.body
 if not body.strip():print("invent requires --body-file, --body, or stdin body",file=sys.stderr);return 2
 pid=ns.id or slugify(ns.name or "custom")
 name=ns.name or pid.replace("-"," ").title()
 desc=ns.description or f"Invented actor: {name}"
 path=write_custom_preset(pid,name,desc,body,float(ns.intensity if ns.intensity is not None else 0.85))
 print(f"saved: {path}")
 if ns.set_active:
  pr=parse_preset(path,"custom")
  try:st=activate(pr,ns.intensity,str(path),normalize_scope(ns.scope),ns.session_id)
  except RuntimeError as e:print(str(e),file=sys.stderr);return 2
  print(f"set: {st['preset']} intensity={st['intensity']:.2f} scope={st['scope']}")
  if st.get("scope")=="global":print(f"rules: {rules_path()}")
 return 0
def cmd_intensity(ns:argparse.Namespace)->int:
 sc=normalize_scope(ns.scope) if ns.scope else None
 if sc=="chat":a=load_chat();layer="chat"
 elif sc=="session":a=load_session(resolve_session_id(ns.session_id));layer="session"
 elif sc=="global":a=load_global();layer="global"
 else:
  a=load_active();layer=(a or {}).get("_layer") or (a or {}).get("scope") or "global"
 if not a:print("no active voice; set a preset first",file=sys.stderr);return 1
 preset={"id":a["preset"],"name":a.get("name",a["preset"]),"intensity_default":ns.level,"body":a["body"],"path":a.get("source","active")}
 try:st=activate(preset,ns.level,a.get("source","active"),layer if layer in ("global","session","chat") else "global",a.get("session_id") or ns.session_id)
 except RuntimeError as e:print(str(e),file=sys.stderr);return 2
 print(f"intensity: {st['intensity']:.2f} on {st['preset']} scope={st['scope']}");return 0
def cmd_clear(ns:argparse.Namespace)->int:
 cleared=clear_scope(ns.scope or "all",ns.session_id)
 print("cleared"+(f" ({', '.join(cleared)})" if cleared else " (nothing stored)"))
 return 0
def cmd_validate(_:argparse.Namespace)->int:
 errs,presets=[],list_presets()
 if not presets:errs.append("no presets found")
 ids=set()
 for p in presets:
  if not p["id"]:errs.append(f"{p['path']}: empty id")
  if p["id"] in ids:errs.append(f"duplicate id: {p['id']}")
  ids.add(p["id"])
  if not p["body"].strip():errs.append(f"{p['id']}: empty body")
  if not (0.0<=p["intensity_default"]<=1.0):errs.append(f"{p['id']}: intensity_default out of range")
 a=load_global()
 if a and "body" not in a:errs.append("active.json missing body")
 if errs:
  print("INVALID");[print(f" - {e}") for e in errs];return 1
 eff=load_active()
 print(f"OK presets={len(presets)} custom={sum(1 for p in presets if p.get('scope')=='custom')} effective={eff['preset'] if eff else 'none'} global={a['preset'] if a else 'none'}");return 0
def cmd_render(_:argparse.Namespace)->int:
 a=load_active()
 if not a:return 0
 print(render_block(a["preset"],a.get("name",a["preset"]),a["body"],float(a.get("intensity",0.7)),a.get("source","active"),a.get("_layer") or a.get("scope","global")))
 return 0
def cmd_custom_dir(_:argparse.Namespace)->int:
 print(custom_dir());return 0
def main(argv:list[str]|None=None)->int:
 p=argparse.ArgumentParser(prog="actor",description="Grok Actor personality control")
 sub=p.add_subparsers(dest="cmd",required=True)
 sub.add_parser("list").set_defaults(func=cmd_list)
 sub.add_parser("show").set_defaults(func=cmd_show)
 h=sub.add_parser("has");h.add_argument("preset");h.set_defaults(func=cmd_has)
 s=sub.add_parser("set");s.add_argument("preset",nargs="?",default=None);s.add_argument("--file");s.add_argument("--intensity",type=float,default=None);s.add_argument("--scope",default="global",help="global|session|chat (aliases: all, this-session, this-chat)");s.add_argument("--session-id",default=None);s.set_defaults(func=cmd_set)
 inv=sub.add_parser("invent");inv.add_argument("--id");inv.add_argument("--name");inv.add_argument("--description",default="");inv.add_argument("--body-file");inv.add_argument("--body");inv.add_argument("--intensity",type=float,default=None);inv.add_argument("--set",dest="set_active",action="store_true");inv.add_argument("--scope",default="global");inv.add_argument("--session-id",default=None);inv.set_defaults(func=cmd_invent)
 i=sub.add_parser("intensity");i.add_argument("level",type=float);i.add_argument("--scope",default=None);i.add_argument("--session-id",default=None);i.set_defaults(func=cmd_intensity)
 c=sub.add_parser("clear");c.add_argument("--scope",default="all",help="all|global|session|chat");c.add_argument("--session-id",default=None);c.set_defaults(func=cmd_clear)
 sub.add_parser("validate").set_defaults(func=cmd_validate)
 sub.add_parser("render").set_defaults(func=cmd_render)
 sub.add_parser("custom-dir").set_defaults(func=cmd_custom_dir)
 ns=p.parse_args(argv)
 if ns.cmd=="set" and not ns.preset and not ns.file:print("set requires PRESET or --file",file=sys.stderr);return 2
 return ns.func(ns)
if __name__=="__main__":sys.exit(main())
