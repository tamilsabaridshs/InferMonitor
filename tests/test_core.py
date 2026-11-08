import tempfile,unittest
from pathlib import Path
from infermonitor.config import load_config
from infermonitor.plugins import Plugin,Registry
from infermonitor.engines import parse_prom
from infermonitor.history import History
from infermonitor.system import LinuxMemoryProvider, SystemInventoryProvider, AmdRocmProcessProvider
class Tests(unittest.TestCase):
 def test_memory_provider_schema(self):
  m=LinuxMemoryProvider(refresh_seconds=0).collect()
  self.assertIn('state',m);self.assertIn('fields',m);self.assertIn('processes',m)
  self.assertIn('processes_semantics',m)
 def test_system_inventory_schema(self):
  s=SystemInventoryProvider().collect()
  self.assertIn('cpu',s);self.assertIn('os',s);self.assertIn('storage_devices',s)
 def test_amd_memory_unit_parser(self):
  self.assertEqual(AmdRocmProcessProvider._number('1.5 GiB'),(1610612736,'bytes'))
  self.assertEqual(AmdRocmProcessProvider._number('bad'),(None,None))
 def test_parse_prometheus(self):
  x=parse_prom('llamacpp:requests_processing{slot="0"} 2\nllamacpp:kv_cache_usage_ratio 0.5',"fixture")
  self.assertEqual(len(x),2);self.assertEqual(x[0]["labels"]["slot"],"0")
 def test_duplicate_plugin(self):
  r=Registry();r.register(Plugin("x","1",(),lambda c:None),{"a":1})
  with self.assertRaises(ValueError):r.register(Plugin("x","1",(),lambda c:None),{"b":2})
 def test_config_default(self):
  with tempfile.TemporaryDirectory() as d:
   c=load_config(str(Path(d)/"cfg.json"));self.assertEqual(c["server"]["host"],"127.0.0.1")
 def test_jsonl_partial_line(self):
  with tempfile.TemporaryDirectory() as d:
   h=History(d,7);h.append({"observed_at":"2026-01-01T00:00:00Z","endpoints":[]})
   with h.path.open("a") as f:f.write('{"bad":')
   self.assertEqual(len(h.query()),1)
if __name__=="__main__":unittest.main()
