from dataclasses import dataclass
@dataclass
class Plugin:
 id: str
 version: str
 provides: tuple
 start_fn: object
 stop_fn: object=None
 state: str="DISCOVERED"
 error: str|None=None
 def start(self,ctx):
  self.state="STARTING"
  try: self.start_fn(ctx); self.state="ACTIVE"
  except Exception as e: self.state="FAILED"; self.error=str(e)
 def stop(self):
  self.state="STOPPING"
  try:
   if self.stop_fn: self.stop_fn()
   self.state="STOPPED"
  except Exception as e: self.state="FAILED"; self.error=str(e)
class Registry:
 def __init__(self): self.plugins={}; self.services={}
 def register(self,p,services):
  if p.id in self.plugins: raise ValueError("Duplicate plugin "+p.id)
  if set(services)&set(self.services): raise ValueError("Duplicate service key")
  self.plugins[p.id]=p; self.services.update(services)
 def start(self):
  for p in self.plugins.values(): p.start({})
 def stop(self):
  for p in reversed(list(self.plugins.values())): p.stop()
 def diagnostics(self):
  return [{"plugin_id":p.id,"version":p.version,"state":p.state,"provides":list(p.provides),"error":p.error} for p in self.plugins.values()]
