import json, threading
from pathlib import Path
class History:
 def __init__(self,directory,days):
  self.path=Path(directory)/"telemetry.jsonl";self.path.parent.mkdir(parents=True,exist_ok=True);self.days=days;self.lock=threading.Lock()
 def append(self,item):
  with self.lock,self.path.open("a",encoding="utf-8") as f:f.write(json.dumps(item,separators=(",",":"),allow_nan=False)+"\n")
 def query(self,limit=500,endpoint=None,session=None,since=None):
  out=[]
  if not self.path.exists():return out
  with self.lock,self.path.open(encoding="utf-8") as f:
   for line in f:
    try:x=json.loads(line)
    except ValueError:continue
    if since and x.get("observed_at","")<since:continue
    eps=x.get("endpoints",[])
    if endpoint and not any(e.get("endpoint_id")==endpoint for e in eps):continue
    if session and not any(e.get("session_id")==session for e in eps):continue
    out.append(x)
  return out[-max(1,min(int(limit),5000)):]
