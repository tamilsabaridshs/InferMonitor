import os,platform,re,time,shutil,json,subprocess
from pathlib import Path
PROC=Path("/proc")
def process_start(pid):
 try:
  tail=(PROC/str(pid)/"stat").read_text().split(")",1)[1].split();ticks=int(tail[19]);hz=os.sysconf(os.sysconf_names["SC_CLK_TCK"])
  boot=int(next(x.split()[1] for x in (PROC/"stat").read_text().splitlines() if x.startswith("btime ")))
  return str(boot+ticks/hz)
 except Exception:return None
def listener_process(host,port):
 if host not in ("127.0.0.1","localhost","::1"):return None
 inodes=set()
 for tab in ("tcp","tcp6"):
  try:lines=(PROC/"net"/tab).read_text().splitlines()[1:]
  except OSError:continue
  for line in lines:
   c=line.split()
   if len(c)>9 and c[3]=="0A":
    try:
     if int(c[1].rsplit(":",1)[1],16)==port:inodes.add(c[9])
    except ValueError:pass
 for ent in PROC.iterdir():
  if not ent.name.isdigit():continue
  try:
   for fd in (ent/"fd").iterdir():
    try:target=os.readlink(fd)
    except OSError:continue
    m=re.fullmatch(r"socket:\[(\d+)\]",target)
    if m and m.group(1) in inodes:
     pid=int(ent.name);start=process_start(pid)
     try:exe=os.path.basename(os.readlink(ent/"exe"))
     except OSError:exe=None
     return {"pid":pid,"start_time":start,"executable":exe,"identity_strength":"strong" if start else "weak"}
  except OSError:pass
 return None
class LinuxProvider:
 id="platform.linux.procfs"
 def __init__(self):self.prev=None;self.disk_prev=None;self.sample_at=None
 def collect(self):
  metrics=[]
  try:
   cpu=next(x for x in (PROC/"stat").read_text().splitlines() if x.startswith("cpu ")).split()[1:];vals=list(map(int,cpu));idle=vals[3]+(vals[4] if len(vals)>4 else 0);total=sum(vals)
   if self.prev:
    dt=total-self.prev[0];di=idle-self.prev[1]
    if dt>0:metrics.append({"name":"cpu.utilization","value":round(100*(dt-di)/dt,2),"unit":"%","source":"procfs","scope":"host","semantics":"whole-host delta"})
   self.prev=(total,idle);mem={}
   for x in (PROC/"meminfo").read_text().splitlines():
    k,v=x.split(":",1);mem[k]=int(v.split()[0])*1024
   for n,v in (("memory.total",mem.get("MemTotal")),("memory.available",mem.get("MemAvailable"))):
    if v is not None:metrics.append({"name":n,"value":v,"unit":"bytes","source":"procfs","scope":"host"})
   if "MemTotal" in mem and "MemAvailable" in mem:metrics.append({"name":"memory.used","value":mem["MemTotal"]-mem["MemAvailable"],"unit":"bytes","source":"procfs","scope":"host","semantics":"MemTotal - MemAvailable"})
   disk={}
   for x in (PROC/"diskstats").read_text().splitlines():
    c=x.split()
    if len(c)>=14 and c[2].startswith(("nvme","sd","vd")):disk[c[2]]=(int(c[5]),int(c[9]))
   now=time.monotonic()
   if self.disk_prev and self.sample_at:
    elapsed=max(.001,now-self.sample_at)
    for name,(rd,wr) in disk.items():
     old=self.disk_prev.get(name)
     if old:metrics.extend([{"name":"disk."+name+".read_bytes_per_sec","value":max(0,rd-old[0])*512/elapsed,"unit":"bytes/s","source":"procfs","scope":"host"},{"name":"disk."+name+".write_bytes_per_sec","value":max(0,wr-old[1])*512/elapsed,"unit":"bytes/s","source":"procfs","scope":"host"}])
   self.disk_prev,self.sample_at=disk,now
   return {"provider_id":self.id,"state":"ACTIVE","metrics":metrics,"details":{"os":platform.platform(),"machine":platform.machine()}}
  except Exception as e:return {"provider_id":self.id,"state":"DEGRADED","metrics":metrics,"error":str(e)}
class AmdRocmProvider:
 id="gpu.amd.rocm_smi"
 def _run_json(self,cmd,args):
  p=subprocess.run([cmd,*args],capture_output=True,text=True,timeout=2)
  if p.returncode:raise RuntimeError(p.stderr[:250] or "AMD SMI command failed")
  return json.loads(p.stdout)
 def _leaf_metrics(self,obj,prefix=""):
  out=[]
  if isinstance(obj,dict):
   if "value" in obj and "unit" in obj and isinstance(obj["value"],(int,float)):
    out.append((prefix,obj["value"],str(obj["unit"])))
   else:
    for k,v in obj.items():out.extend(self._leaf_metrics(v,(prefix+"."+k if prefix else k).lower()))
  elif isinstance(obj,(int,float)) and not isinstance(obj,bool):out.append((prefix,obj,None))
  return out
 def collect(self):
  cmd=shutil.which("amd-smi")
  if cmd:
   try:
    metrics=self._run_json(cmd,["metric","--json"])
    try:inventory=self._run_json(cmd,["list","--json"])
    except Exception:inventory=[]
    if not isinstance(metrics,list):metrics=metrics.get("gpu_data",[]) if isinstance(metrics,dict) else []
    if not isinstance(inventory,list):inventory=inventory.get("gpu_data",[]) if isinstance(inventory,dict) else []
    inventory_by_gpu={str(x.get("gpu")):x for x in inventory if isinstance(x,dict)}
    devices=[]
    for row in metrics:
     if not isinstance(row,dict):continue
     idx=str(row.get("gpu","?"));static=inventory_by_gpu.get(idx,{})
     dev_metrics=[]
     for section,value in row.items():
      if section=="gpu":continue
      for field,val,unit in self._leaf_metrics(value,section):
       name=field.lower()
       canonical={"usage.gfx_activity":"gpu.utilization","power.socket_power":"gpu.power","temperature.hotspot":"gpu.temperature.hotspot","temperature.edge":"gpu.temperature.edge","mem_usage.used_vram":"gpu.memory.used","mem_usage.total_vram":"gpu.memory.total"}.get(name)
       if canonical:
        # Preserve the exact AMD SMI unit (for example MB); do not assume MB means MiB.
        dev_metrics.append({"name":canonical,"value":val,"unit":unit,"scope":"gpu","source":"amd-smi.metric","availability":"available","semantics":"AMD SMI field "+field})
       dev_metrics.append({"name":"amd_smi."+field,"value":val,"unit":unit,"scope":"gpu","source":"amd-smi.metric","availability":"available","semantics":"raw AMD SMI metric"})
     bdf=static.get("bdf") or static.get("pci_bdf");uuid=static.get("uuid")
     devices.append({"device_id":str(uuid or bdf or "amd-index-"+idx),"identity_strength":"strong" if uuid or bdf else "weak","vendor":"amd","provider_id":self.id,"metrics":dev_metrics})
    return {"provider_id":self.id,"state":"ACTIVE" if devices else "DEGRADED","devices":devices,"error":None if devices else "amd-smi returned no GPU metrics"}
   except Exception as e:return {"provider_id":self.id,"state":"DEGRADED","devices":[],"error":str(e)}
  cmd=shutil.which("rocm-smi")
  if not cmd:return {"provider_id":self.id,"state":"DEGRADED","devices":[],"error":"amd-smi/rocm-smi not installed"}
  try:
   raw=self._run_json(cmd,["--json"]);devs=raw if isinstance(raw,list) else raw.get("card",raw.get("gpu",[])) if isinstance(raw,dict) else []
   if isinstance(devs,dict):devs=list(devs.values())
   devices=[{"device_id":"rocm-smi-index-"+str(i),"identity_strength":"weak","vendor":"amd","provider_id":self.id,"metrics":[],"raw_numeric_fields":{k:v for k,v in d.items() if isinstance(v,(int,float))}} for i,d in enumerate(devs) if isinstance(d,dict)]
   return {"provider_id":self.id,"state":"ACTIVE" if devices else "DEGRADED","devices":devices,"error":None if devices else "No legacy ROCm SMI device records parsed"}
  except Exception as e:return {"provider_id":self.id,"state":"DEGRADED","devices":[],"error":str(e)}
