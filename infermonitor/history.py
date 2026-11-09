import json,threading
from pathlib import Path
from datetime import datetime,timedelta,timezone
class History:
 def __init__(self,directory,days):
  self.path=Path(directory)/"telemetry.jsonl";self.path.parent.mkdir(parents=True,exist_ok=True);self.days=days;self.lock=threading.Lock();self.prune()
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
 def prune(self):
  if not self.path.exists():return
  cutoff=datetime.now(timezone.utc)-timedelta(days=max(1,int(self.days)));kept=[]
  with self.lock,self.path.open(encoding="utf-8") as f:
   for line in f:
    try:
     item=json.loads(line);stamp=datetime.fromisoformat(item["observed_at"].replace("Z","+00:00"))
     if stamp>=cutoff:kept.append(json.dumps(item,separators=(",",":")))
    except (ValueError,KeyError,TypeError):continue
  tmp=self.path.with_suffix(".jsonl.tmp");tmp.write_text("\n".join(kept)+("\n" if kept else ""),encoding="utf-8");tmp.replace(self.path)
