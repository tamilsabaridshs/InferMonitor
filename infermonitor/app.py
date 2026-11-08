import argparse,signal,threading,time,uuid
from datetime import datetime,timezone
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit,urlparse,parse_qs
from pathlib import Path
from .config import load_config
from .providers import LinuxProvider,AmdRocmProvider,listener_process
from .plugins import Plugin,Registry
from .engines import Adapter,get
from .history import History
from . import __version__
def now():return datetime.now(timezone.utc).isoformat()
class Collector:
 def __init__(self,cfg,hist,registry):
  self.cfg,self.hist,self.registry=cfg,hist,registry;self.host=LinuxProvider();self.gpu=AmdRocmProvider();self.adapters=[Adapter("polystrata"),Adapter("llamacpp")];self.sessions={};self.last=None;self.running=False;self.error=None
 def once(self):
  host=self.host.collect();gpu=self.gpu.collect();eps=[];seen=set();timeout=self.cfg["collector"]["request_timeout_ms"]/1000;limit=self.cfg["collector"]["max_response_bytes"];probe_cache={}
  def http(url):
   if url not in probe_cache:probe_cache[url]=get(url,timeout,limit)
   return probe_cache[url]
  for e in self.cfg["endpoints"]:
   if not e.get("enabled",True):continue
   base=e["url"].rstrip("/");p=urlsplit(base);proc=listener_process(p.hostname,p.port or (443 if p.scheme=="https" else 80));selected=e.get("engine","auto");adapter=None;proof={}
   if selected!="auto":
    adapter=next((x for x in self.adapters if x.engine==selected),None)
    proof[selected]={"signature":"explicit user override","mode":"manual"}
   else:
    for a in self.adapters:
     ok,ev=a.identify(base,http);proof[a.engine]=ev
     if ok:adapter=a;break
   if not adapter:
    unavailable=bool(proof) and all(x.get("metrics_status") is None and x.get("health_status") is None for x in proof.values())
    eps.append({"endpoint_id":e["id"],"url":base,"state":"unavailable" if unavailable else "unknown_engine","engine":None,"process":proc,"detection":{"evidence":proof},"metrics":[],"error":"Endpoint unreachable" if unavailable else "No validated engine fingerprint matched"});continue
   identity=(str(proc["pid"])+":"+str(proc["start_time"])) if proc else "local-unidentified:"+base;sig=identity+":"+adapter.engine
   if e["id"] not in self.sessions or self.sessions[e["id"]]["signature"]!=sig:self.sessions[e["id"]]={"signature":sig,"session_id":"session-"+uuid.uuid4().hex[:12]}
   if identity in seen:result={"metrics":[],"details":{"deduplicated":True},"diagnostics":{}}
   else:result=adapter.collect(base,http);seen.add(identity)
   diagnostics=result.get("diagnostics",{});states=[v.get("state") for v in diagnostics.values()]
   endpoint_state="unavailable" if states and all(x in ("unreachable","http_error") for x in states) else "connected"
   eps.append({"endpoint_id":e["id"],"url":base,"state":endpoint_state,"engine":adapter.engine,"engine_version":proof.get(adapter.engine,{}).get("engine_version"),"process":proc,"session_id":self.sessions[e["id"]]["session_id"],"detection":{"mode":"manual" if selected!="auto" else "automatic","evidence":proof},"metrics":result.get("metrics",[]),"diagnostics":diagnostics})
  host_sample_id=uuid.uuid4().hex
  for endpoint in eps:endpoint["host_sample_id"]=host_sample_id
  self.last={"schema_version":1,"cycle_id":uuid.uuid4().hex,"observed_at":now(),"host_sample_id":host_sample_id,"host":host,"gpu_devices":gpu.get("devices",[]),"gpu_provider":{"state":gpu["state"],"error":gpu.get("error")},"endpoints":eps,"plugins":self.registry.diagnostics()}
  if self.hist:self.hist.append(self.last)
 def run(self):
  self.running=True;interval=self.cfg["collector"]["poll_interval_ms"]/1000
  while self.running:
   t=time.monotonic()
   try:self.once();self.error=None
   except Exception as e:self.error=str(e)
   time.sleep(max(.05,interval-(time.monotonic()-t)))
 def stop(self):self.running=False
class Api:
 def __init__(self,cfg,col,hist):
  self.cfg,self.col,self.hist=cfg,col,hist;outer=self
  class H(BaseHTTPRequestHandler):
   def log_message(self,*a):pass
   def send(self,code,obj,ctype="application/json"):
    b=obj if isinstance(obj,bytes) else __import__("json").dumps(obj,ensure_ascii=False).encode()
    self.send_response(code);self.send_header("Content-Type",ctype);self.send_header("Content-Length",str(len(b)));self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(b)
   def do_GET(self):
    u=urlparse(self.path)
    if u.path=="/":self.send(200,(Path(__file__).parent/"web"/"index.html").read_bytes(),"text/html; charset=utf-8");return
    if u.path=="/api/health":self.send(200,{"status":"ok","api_version":"1","collector":{"running":outer.col.running,"last_cycle_at":(outer.col.last or {}).get("observed_at"),"last_error":outer.col.error}});return
    if u.path=="/api/snapshot":self.send(200,outer.col.last or {"status":"starting"});return
    if u.path=="/api/endpoints":self.send(200,{"endpoints":(outer.col.last or {}).get("endpoints",[])});return
    if u.path=="/api/config":self.send(200,{"server":{"host":"127.0.0.1","port":outer.cfg["server"]["port"]},"collector":outer.cfg["collector"],"endpoints":outer.cfg["endpoints"]});return
    if u.path=="/api/history":
     q=parse_qs(u.query)
     try:limit=int(q.get("limit",["500"])[0])
     except ValueError:self.send(400,{"error":{"code":"INVALID_QUERY","message":"limit must be an integer"}});return
     self.send(200,{"items":outer.hist.query(limit,q.get("endpoint_id",[None])[0],q.get("session_id",[None])[0],q.get("from",[None])[0])});return
    self.send(404,{"error":{"code":"NOT_FOUND","message":"Unknown route"}})
  self.server=ThreadingHTTPServer((cfg["server"]["host"],cfg["server"]["port"]),H);self.server.daemon_threads=True
 def serve(self):self.server.serve_forever()
 def stop(self):self.server.shutdown();self.server.server_close()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--config",default="config/infermonitor.json");a=ap.parse_args();cfg=load_config(a.config)
 hist=History(cfg["history"]["directory"],cfg["history"]["retention_days"]) if cfg["history"]["enabled"] else None
 reg=Registry();plat=LinuxProvider();gpu=AmdRocmProvider()
 reg.register(Plugin("platform.linux",__version__,("process.discovery","host.telemetry"),lambda c:None),{"platform.linux":plat})
 reg.register(Plugin("gpu.amd.rocm",__version__,("gpu.telemetry",),lambda c:None),{"gpu.amd.rocm":gpu});reg.start()
 col=Collector(cfg,hist,reg);api=Api(cfg,col,hist or History("./data",7));worker=threading.Thread(target=col.run,daemon=True);worker.start()
 print("InferMonitor "+__version__+" at http://127.0.0.1:"+str(cfg["server"]["port"]))
 def stop(*_):
  col.stop()
  threading.Thread(target=api.stop,daemon=True).start()
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:api.serve()
 finally:col.stop();reg.stop()
