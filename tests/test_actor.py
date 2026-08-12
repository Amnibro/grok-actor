#!/usr/bin/env python3
from __future__ import annotations
import json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CLI=ROOT/"scripts"/"actor_cli.py"
INJECT=ROOT/"hooks"/"inject_actor.py"
class VoiceTests(unittest.TestCase):
 def setUp(self)->None:
  self.tmp=tempfile.TemporaryDirectory();self.data=Path(self.tmp.name)/"data";self.data.mkdir()
  self.home=Path(self.tmp.name)/"home";(self.home/".grok"/"rules").mkdir(parents=True);(self.home/".grok"/"personas").mkdir(parents=True)
  self.env=os.environ.copy();self.env["GROK_PLUGIN_ROOT"]=str(ROOT);self.env["GROK_PLUGIN_DATA"]=str(self.data);self.env["HOME"]=str(self.home);self.env["USERPROFILE"]=str(self.home)
  for k in ("GROK_SESSION_ID","CLAUDE_SESSION_ID"):self.env.pop(k,None)
 def tearDown(self)->None:self.tmp.cleanup()
 def run_cli(self,*args:str)->subprocess.CompletedProcess:
  return subprocess.run([sys.executable,str(CLI),*args],capture_output=True,text=True,env=self.env,cwd=str(ROOT))
 def run_inject(self,payload:dict|str,event:str|None=None)->subprocess.CompletedProcess:
  env=self.env.copy()
  if event:env["GROK_HOOK_EVENT"]=event
  raw=payload if isinstance(payload,str) else json.dumps(payload)
  return subprocess.run([sys.executable,str(INJECT)],input=raw,capture_output=True,text=True,env=env)
 def test_presets_parse(self)->None:
  r=self.run_cli("list");self.assertEqual(r.returncode,0,r.stderr)
  for pid in ("neutral","concise","mentor","formal","playful","drill","rikku"):self.assertIn(pid,r.stdout)
 def test_validate_ok(self)->None:
  r=self.run_cli("validate");self.assertEqual(r.returncode,0,r.stdout+r.stderr);self.assertIn("OK",r.stdout)
 def test_set_show_clear_roundtrip(self)->None:
  r=self.run_cli("set","concise","--intensity","0.9");self.assertEqual(r.returncode,0,r.stderr)
  active=json.loads((self.data/"active.json").read_text(encoding="utf-8"))
  self.assertEqual(active["preset"],"concise");self.assertAlmostEqual(active["intensity"],0.9);self.assertEqual(active.get("scope"),"global")
  rules=self.home/".grok"/"rules"/"grok-actor-active.md"
  self.assertTrue(rules.exists());self.assertIn("Concise",rules.read_text(encoding="utf-8"))
  persona=self.home/".grok"/"personas"/"grok-actor-active.toml"
  self.assertTrue(persona.exists());self.assertIn("instructions",persona.read_text(encoding="utf-8"))
  s=self.run_cli("show");self.assertEqual(s.returncode,0);self.assertIn("concise",s.stdout);self.assertIn("global:",s.stdout)
  c=self.run_cli("clear");self.assertEqual(c.returncode,0);self.assertFalse((self.data/"active.json").exists());self.assertFalse(rules.exists())
 def test_intensity_clamp_and_update(self)->None:
  self.assertEqual(self.run_cli("set","mentor").returncode,0)
  r=self.run_cli("intensity","1.5");self.assertEqual(r.returncode,0)
  active=json.loads((self.data/"active.json").read_text(encoding="utf-8"));self.assertAlmostEqual(active["intensity"],1.0)
 def test_unknown_preset(self)->None:
  r=self.run_cli("set","not-a-real-preset");self.assertNotEqual(r.returncode,0)
 def test_custom_file(self)->None:
  f=Path(self.tmp.name)/"custom.md";f.write_text("---\nid: spacex\nname: SpaceX\ndescription: d\nintensity_default: 0.6\n---\n# Voice: SpaceX\nBe crisp and mission-focused.\n",encoding="utf-8")
  r=self.run_cli("set","--file",str(f));self.assertEqual(r.returncode,0,r.stderr)
  active=json.loads((self.data/"active.json").read_text(encoding="utf-8"));self.assertEqual(active["preset"],"spacex")
 def test_scope_chat_does_not_touch_global_rules(self)->None:
  self.assertEqual(self.run_cli("set","formal","--scope","global").returncode,0)
  rules=self.home/".grok"/"rules"/"grok-actor-active.md";before=rules.read_text(encoding="utf-8")
  r=self.run_cli("set","playful","--scope","chat");self.assertEqual(r.returncode,0,r.stderr)
  self.assertTrue((self.data/"chat-override.json").exists())
  self.assertEqual(json.loads((self.data/"active.json").read_text(encoding="utf-8"))["preset"],"formal")
  self.assertEqual(rules.read_text(encoding="utf-8"),before)
  show=self.run_cli("show");self.assertIn("effective: playful",show.stdout);self.assertIn("chat: playful",show.stdout);self.assertIn("global: formal",show.stdout)
 def test_scope_session_needs_id(self)->None:
  r=self.run_cli("set","drill","--scope","session");self.assertEqual(r.returncode,2);self.assertIn("session id",r.stderr.lower())
 def test_scope_session_with_id(self)->None:
  self.assertEqual(self.run_cli("set","neutral","--scope","global").returncode,0)
  r=self.run_cli("set","trump","--scope","session","--session-id","sess-abc");self.assertEqual(r.returncode,0,r.stderr)
  self.assertTrue((self.data/"sessions"/"sess-abc.json").exists())
  self.assertEqual(json.loads((self.data/"active.json").read_text(encoding="utf-8"))["preset"],"neutral")
  env=self.env.copy();env["GROK_SESSION_ID"]="sess-abc"
  show=subprocess.run([sys.executable,str(CLI),"show"],capture_output=True,text=True,env=env,cwd=str(ROOT))
  self.assertIn("effective: trump",show.stdout);self.assertIn("session: trump",show.stdout)
 def test_priority_chat_over_session_over_global(self)->None:
  self.assertEqual(self.run_cli("set","neutral","--scope","global").returncode,0)
  self.assertEqual(self.run_cli("set","sherlock","--scope","session","--session-id","s1").returncode,0)
  self.assertEqual(self.run_cli("set","pirate","--scope","chat").returncode,0)
  env=self.env.copy();env["GROK_SESSION_ID"]="s1"
  show=subprocess.run([sys.executable,str(CLI),"show"],capture_output=True,text=True,env=env,cwd=str(ROOT))
  self.assertIn("effective: pirate",show.stdout)
  self.run_cli("clear","--scope","chat")
  show2=subprocess.run([sys.executable,str(CLI),"show"],capture_output=True,text=True,env=env,cwd=str(ROOT))
  self.assertIn("effective: sherlock",show2.stdout)
 def test_inject_session_start_json(self)->None:
  self.assertEqual(self.run_cli("set","formal").returncode,0)
  r=self.run_inject({"session_id":"s1","hook_event_name":"SessionStart","source":"startup"},"session_start")
  self.assertEqual(r.returncode,0,r.stderr);payload=json.loads(r.stdout)
  self.assertIn("additionalContext",payload);self.assertIn("GROK_ACTOR_ACTIVE",payload["additionalContext"])
  self.assertIn("hookSpecificOutput",payload);self.assertEqual(payload["hookSpecificOutput"]["hookEventName"],"SessionStart")
  last=json.loads((self.data/"last-session.json").read_text(encoding="utf-8"));self.assertEqual(last["session_id"],"s1")
 def test_inject_user_prompt_json(self)->None:
  self.assertEqual(self.run_cli("set","playful").returncode,0)
  r=self.run_inject({"session_id":"s2","hook_event_name":"UserPromptSubmit"},"user_prompt_submit")
  self.assertEqual(r.returncode,0);payload=json.loads(r.stdout)
  self.assertEqual(payload["hookSpecificOutput"]["hookEventName"],"UserPromptSubmit")
  self.assertIn("Playful",payload["additionalContext"])
 def test_inject_clears_chat_on_session_start_not_prompt(self)->None:
  self.assertEqual(self.run_cli("set","concise","--scope","global").returncode,0)
  self.assertEqual(self.run_cli("set","yoda","--scope","chat").returncode,0)
  r=self.run_inject({"session_id":"s3","hook_event_name":"UserPromptSubmit"},"user_prompt_submit")
  self.assertIn("Yoda",json.loads(r.stdout)["additionalContext"])
  self.assertTrue((self.data/"chat-override.json").exists())
  r2=self.run_inject({"session_id":"s3","hook_event_name":"SessionStart","source":"clear"},"session_start")
  self.assertFalse((self.data/"chat-override.json").exists())
  self.assertIn("Concise",json.loads(r2.stdout)["additionalContext"])
 def test_inject_session_override(self)->None:
  self.assertEqual(self.run_cli("set","neutral","--scope","global").returncode,0)
  self.assertEqual(self.run_cli("set","unhinged","--scope","session","--session-id","s9").returncode,0)
  r=self.run_inject({"session_id":"s9","hook_event_name":"UserPromptSubmit"},"user_prompt_submit")
  self.assertIn("Unhinged",json.loads(r.stdout)["additionalContext"])
  r2=self.run_inject({"session_id":"other","hook_event_name":"UserPromptSubmit"},"user_prompt_submit")
  self.assertIn("Neutral",json.loads(r2.stdout)["additionalContext"])
 def test_inject_noop_without_active(self)->None:
  r=self.run_inject({},None)
  self.assertEqual(r.returncode,0);self.assertEqual(r.stdout.strip(),"")
 def test_plugin_manifest_present(self)->None:
  man=ROOT/".claude-plugin"/"plugin.json";self.assertTrue(man.exists());data=json.loads(man.read_text(encoding="utf-8"))
  self.assertEqual(data["name"],"grok-actor");self.assertIn("version",data)
 def test_hooks_json_shape(self)->None:
  data=json.loads((ROOT/"hooks"/"hooks.json").read_text(encoding="utf-8"))
  self.assertIn("SessionStart",data["hooks"]);self.assertIn("UserPromptSubmit",data["hooks"])
if __name__=="__main__":
 raise SystemExit(0 if unittest.main(verbosity=2) is None else 0)
