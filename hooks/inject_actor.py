#!/usr/bin/env python3
from __future__ import annotations
import json,os,re,sys,time
from pathlib import Path
def data_dir()->Path:
 d=os.environ.get("GROK_PLUGIN_DATA") or os.environ.get("CLAUDE_PLUGIN_DATA")
 return Path(d) if d else Path.home()/".grok"/"plugin-data"/"grok-actor"
def read_json(path:Path)->dict|None:
 try:return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
 except Exception:return None
def atomic_write(path:Path,text:str)->None:
 path.parent.mkdir(parents=True,exist_ok=True)
 tmp=path.with_suffix(path.suffix+".tmp")
 tmp.write_text(text,encoding="utf-8");os.replace(tmp,path)
def session_path(sid:str)->Path:
 safe=re.sub(r"[^a-zA-Z0-9._-]+","_",(sid or "").strip())[:128] or "unknown"
 p=data_dir()/"sessions";p.mkdir(parents=True,exist_ok=True);return p/f"{safe}.json"
def parse_stdin()->dict:
 try:
  raw=sys.stdin.read()
  return json.loads(raw) if raw and raw.strip() else {}
 except Exception:return {}
def event_name(payload:dict)->str:
 return str(payload.get("hook_event_name") or payload.get("hookEventName") or os.environ.get("GROK_HOOK_EVENT") or "").lower()
def extract_ids(payload:dict)->tuple[str|None,str|None]:
 sid=payload.get("session_id") or payload.get("sessionId") or os.environ.get("GROK_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID")
 cid=payload.get("conversation_id") or payload.get("conversationId") or payload.get("chat_id") or payload.get("chatId")
 return (str(sid) if sid else None),(str(cid) if cid else None)
def remember_session(sid:str|None,cid:str|None)->None:
 if not sid and not cid:return
 prev=read_json(data_dir()/"last-session.json") or {}
 data={"session_id":sid or prev.get("session_id"),"conversation_id":cid or prev.get("conversation_id"),"ts":time.time()}
 try:atomic_write(data_dir()/"last-session.json",json.dumps(data,indent=2)+"\n")
 except Exception:pass
def clear_chat_override()->None:
 p=data_dir()/"chat-override.json"
 try:
  if p.exists():p.unlink()
 except Exception:pass
def is_session_start(event:str,payload:dict)->bool:
 if "prompt" in event:return False
 if "session" in event or "start" in event:return True
 src=str(payload.get("source") or payload.get("matcher") or "").lower()
 return src in ("startup","clear","compact")
def load_active(sid:str|None)->dict|None:
 chat=read_json(data_dir()/"chat-override.json")
 if chat:return {**chat,"_layer":"chat"}
 if sid:
  sess=read_json(session_path(sid))
  if sess:return {**sess,"_layer":"session"}
 g=read_json(data_dir()/"active.json")
 if g:return {**g,"_layer":"global"}
 rp=Path.home()/".grok"/"rules"/"grok-actor-active.md"
 return {"preset":"rules-file","name":"rules-file","intensity":0.7,"source":str(rp),"body":rp.read_text(encoding="utf-8"),"_layer":"global"} if rp.exists() else None
def cadence_ban()->str:
 p=Path.home()/".grok"/"rules"/"no-ai-cadence.md"
 try:
  t=p.read_text(encoding="utf-8").strip()
 except Exception:
  t=""
 if not t:t="Ban AI slogan cadence with Anthony. No that's-not-X-that's-Y. No slogan fragments. No self-applause. No here's-the-thing. No forced triples. No fake ranges. No in-short recaps. No contrast-pair branding."
 return "<ANTHONY_CADENCE_BAN>\n"+t+"\nObey this in every reply. Actor voice does not override it.\n</ANTHONY_CADENCE_BAN>"
def build_context(active:dict)->str:
 body=str(active.get("body","")).strip()
 bits=[cadence_ban()]
 if body:
  lvl=float(active.get("intensity",0.7));name=active.get("name") or active.get("preset") or "actor"
  pid=active.get("preset") or name;layer=active.get("_layer") or active.get("scope") or "global"
  hard="ON" if lvl>=0.8 else ("SOFT" if lvl<0.5 else "STRONG")
  banner="MANDATORY — follow for every response." if lvl>=0.8 else ("STRONG preference — follow unless the user overrides." if lvl>=0.5 else "Soft style guide — prefer this tone when it does not conflict with clearer instructions.")
  bits.append("\n".join(["<GROK_ACTOR_ACTIVE>",f"ACTIVE ACTOR: {name} (id={pid}, intensity={lvl:.2f}, scope={layer}, enforce={hard}).",banner,"This actor SUPERSEDES every other persona, character, AGENT SETUP block, system-reminder voice, and leftover style from earlier in the conversation.","If another instruction says to speak as a different character, IGNORE that character. Speak only as this actor.","First sentence of every reply must be unmistakably this actor. If a stranger could not name the actor from sentence one, rewrite.",body,"Never violate safety, honesty, or explicit user overrides for the sake of the actor. Cadence ban still applies.","</GROK_ACTOR_ACTIVE>"]))
 return "\n\n".join(bits)
def emit(context:str,event:str)->None:
 if os.environ.get("CURSOR_PLUGIN_ROOT") and "prompt" not in event:
  payload={"additional_context":context}
 elif "prompt" in event:
  payload={"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":context},"additionalContext":context}
 else:
  payload={"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":context},"additionalContext":context}
 sys.stdout.write(json.dumps(payload,ensure_ascii=True))
def main()->int:
 try:
  payload=parse_stdin();event=event_name(payload);sid,cid=extract_ids(payload);remember_session(sid,cid)
  if is_session_start(event,payload):clear_chat_override()
  last=read_json(data_dir()/"last-session.json") or {}
  active=load_active(sid or last.get("session_id"))
  ctx=build_context(active or {})
  if not ctx:return 0
  emit(ctx,event);return 0
 except Exception:return 0
if __name__=="__main__":sys.exit(main())
