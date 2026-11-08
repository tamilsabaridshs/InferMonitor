import json
from pathlib import Path
from urllib.parse import urlsplit
DEFAULT = {"server":{"host":"127.0.0.1","port":8090},"collector":{"poll_interval_ms":1000,"request_timeout_ms":700,"max_response_bytes":1048576},"history":{"enabled":True,"directory":"./data","retention_days":7},"endpoints":[{"id":"local-8080","url":"http://127.0.0.1:8080","enabled":True,"engine":"auto"},{"id":"local-8081","url":"http://127.0.0.1:8081","enabled":False,"engine":"auto"},{"id":"local-8082","url":"http://127.0.0.1:8082","enabled":False,"engine":"auto"}]}
def load_config(path):
 p=Path(path)
 if not p.exists():
  p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(DEFAULT,indent=2))
 c=json.loads(p.read_text())
 for k,v in DEFAULT.items():c.setdefault(k,v)
 enabled=[e for e in c["endpoints"] if e.get("enabled",True)]
 if len(enabled)>3:raise ValueError("MVP supports at most three enabled endpoints")
 if len({e["id"] for e in c["endpoints"]})!=len(c["endpoints"]):raise ValueError("Endpoint IDs must be unique")
 if c["server"]["host"] not in ("127.0.0.1","::1","localhost"):raise ValueError("MVP API must bind to loopback")
 for e in c["endpoints"]:
  if e.get("engine","auto") not in ("auto","polystrata","llamacpp"):raise ValueError("Invalid engine override")
  if not e["url"].startswith(("http://","https://")):raise ValueError("Only HTTP(S) endpoints are supported")
  u=urlsplit(e["url"])
  if u.hostname not in ("127.0.0.1","localhost","::1") or u.username or u.password:raise ValueError("MVP inference targets must be loopback URLs without embedded credentials")
 if not 500<=int(c["collector"]["poll_interval_ms"])<=60000:raise ValueError("Poll interval must be 500..60000 ms")
 return c
