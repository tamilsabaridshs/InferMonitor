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
    if dt>0:metrics.append({"name":"cpu.utilization","value":round(100*(dt-di)/dt,2),"unit":"%","source":"procfs","scope":"host"})
   self.prev=(total,idle);mem={}
   for x in (PROC/"meminfo").read_text().splitlines():
    k,v=x.split(":",1);mem[k]=int(v.split()[0])*1024
   for n,v in (("memory.total",mem.get("MemTotal")),("memory.available",mem.get("MemAvailable"))):
    if v is not None:metrics.append({"name":n,"value":v,"unit":"bytes","source":"procfs","scope":"host"})
   if "MemTotal" in mem and "MemAvailable" in mem:metrics.append({"name":"memory.used","value":mem["MemTotal"]-mem["MemAvailable"],"unit":"bytes","source":"procfs","scope":"host"})
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
 def collect(self):
  cmd=shutil.which("amd-smi") or shutil.which("rocm-smi")
  if not cmd:return {"provider_id":self.id,"state":"DEGRADED","devices":[],"error":"amd-smi/rocm-smi not installed"}
  args=["metric","--json"] if cmd.endswith("amd-smi") else ["--json"]
  try:
   p=subprocess.run([cmd,*args],capture_output=True,text=True,timeout=2)
   if p.returncode:raise RuntimeError(p.stderr[:250])
   raw=json.loads(p.stdout)
   if isinstance(raw,list):devs=raw
   elif isinstance(raw,dict):
    devs=raw.get("gpu",raw.get("GPUs",raw.get("devices")))
    if devs is None:devs=[v for k,v in raw.items() if isinstance(v,dict) and (k.lower().startswith("card") or "gpu" in k.lower())]
   else:devs=[]
   if isinstance(devs,dict):devs=list(devs.values())
   out=[]
   for i,d in enumerate(devs if isinstance(devs,list) else []):
    if not isinstance(d,dict):continue
    flat={}
    def walk(x,k=""):
     if isinstance(x,dict):
      for a,b in x.items():walk(b,(k+"."+a).lower())
     elif isinstance(x,(int,float)) and not isinstance(x,bool):flat[k]=x
    walk(d)
    out.append({"device_id":str(d.get("uuid") or d.get("bdf") or d.get("pci_bus") or "amd-index-"+str(i)),"vendor":"amd","provider_id":self.id,"raw_numeric_fields":flat,"metrics":[]})
   return {"provider_id":self.id,"state":"ACTIVE" if out else "DEGRADED","devices":out,"error":None if out else "No AMD device records parsed; field mapping awaits version-labelled fixture"}
  except Exception as e:return {"provider_id":self.id,"state":"DEGRADED","devices":[],"error":str(e)}
