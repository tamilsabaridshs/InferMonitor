import json,re,urllib.request,urllib.error
def get(url,timeout,limit):
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"InferMonitor/0.1","Accept":"application/json,text/plain,*/*"})
  with urllib.request.urlopen(req,timeout=timeout) as r:
   b=r.read(limit+1)
   if len(b)>limit:return "too_large",None,r.status
   return "ok",b.decode("utf-8","replace"),r.status
 except urllib.error.HTTPError as e:return "http_error",e.read(2048).decode("utf-8","replace"),e.code
 except Exception as e:return "unreachable",str(e),None
SAMPLE=re.compile(r'^([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{(.*?)\})?\s+([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?|NaN|[+-]?Inf)$')
LABEL=re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)="((?:\\.|[^"])*)"')
def parse_prom(body,source):
 out=[]
 for line in body.splitlines():
  m=SAMPLE.match(line.strip())
  if not m:continue
  name,rawlabels,raw=m.groups()
  try:v=float(raw)
  except ValueError:continue
  if not (float("-inf")<v<float("inf")):continue
  labels={k:val.replace('\\n','\n').replace('\\\"','"').replace('\\\\','\\') for k,val in LABEL.findall(rawlabels or "")}
  out.append({"name":name,"value":v,"unit":None,"scope":"engine","source":source,"availability":"available","semantics":"raw Prometheus sample; type is defined by exposition","labels":labels})
 return out
class Adapter:
 def __init__(self,engine):self.engine=engine
 def identify(self,base,http):
  if self.engine=="polystrata":
   state,body,status=http(base+"/metrics")
   try:d=json.loads(body) if body else {}
   except ValueError:d={}
   hs,hb,hstatus=http(base+"/health")
   try:h=json.loads(hb) if hb else {}
   except ValueError:h={}
   ok=isinstance(d,dict) and (("engine" in d and isinstance(d["engine"],dict) and "version" in d["engine"]) or any(k in d for k in ("hardware_static","requests","max_context","expert_cache_mib")))
   ok=ok or (isinstance(h,dict) and ("max_context" in h or ("loaded" in h and "model" in h)))
   return ok,{"metrics_status":status,"health_status":hstatus,"signature":"PolyStrata JSON metrics/health" if ok else None}
  state,body,status=http(base+"/metrics")
  if state=="ok" and ("llamacpp:" in body or ("# TYPE" in body and "llama_" in body)):return True,{"metrics_status":status,"signature":"llama.cpp Prometheus exposition"}
  return False,{"metrics_status":status}
 def collect(self,base,http):
  if self.engine=="llamacpp":
   state,body,status=http(base+"/metrics")
   return {"metrics":parse_prom(body or "","llamacpp.prometheus") if state=="ok" else [],"diagnostics":{"/metrics":{"state":state,"status":status}}}
  result={"metrics":[],"diagnostics":{}}
  for path in ("/health","/props","/metrics"):
   state,body,status=http(base+path);result["diagnostics"][path]={"state":state,"status":status}
   try:d=json.loads(body) if state=="ok" and body else None
   except ValueError:d=None
   if isinstance(d,dict):
    def walk(x,key):
     if isinstance(x,dict):
      for k,v in x.items():walk(v,key+"."+k)
     elif isinstance(x,list):
      for i,v in enumerate(x):
       if isinstance(v,dict):walk(v,key+"["+str(i)+"]")
     elif isinstance(x,(int,float)) and not isinstance(x,bool):
      result["metrics"].append({"name":key,"value":x,"unit":None,"scope":"engine","source":"polystrata.json","availability":"available","semantics":"raw engine field; no unit inferred"})
    walk(d,path)
  state,body,status=http(base+"/metrics/prometheus")
  if state=="ok" and body and "# TYPE" in body:result["metrics"]+=parse_prom(body,"polystrata.prometheus")
  return result
