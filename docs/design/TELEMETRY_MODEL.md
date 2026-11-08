# Telemetry Catalogue and Data Semantics

**Status:** Proposed canonical contract. Implementation must validate field availability against real providers.

## 1. Principles

Each metric has a name, value, unit, scope, source/provider, resource identity, observation timestamp, availability and semantics. Preserve source meanings and units. Unsupported or unavailable values are null, never zero.

Canonical names are used only when semantic equivalence is valid. Otherwise retain a source-specific metric name and raw provenance rather than forcing a misleading normalization.

## 2. Scopes

| Scope | Examples | Sampling |
|---|---|---|
| Host | CPU, system RAM, disk IO | Once per cycle |
| Physical device | GPU utilisation, physical VRAM, temperature, power, PCIe | Once per device per cycle |
| Process | PID, start time, RSS, CPU time | Per unique process |
| Engine | prompt/decode throughput, requests, queue/slot information | Per engine adapter context |
| Runtime subsystem | KV, expert cache, arena, draft/MTP | Per engine |
| Session | start/end, engine/process identity | Lifecycle events |

## 3. Availability states

Every optional field uses one of:
- `available`
- `unsupported`
- `not_exposed`
- `temporarily_unavailable`
- `permission_denied`
- `provider_unavailable`
- `provider_error`
- `not_probed`

A missing metric is never zero. Provider-level health and metric-level availability are separate: a GPU provider can be healthy while temperature is unsupported.

## 4. Canonical metric envelope

```json
{
  "name": "decode_tokens_per_second",
  "value": 18.4,
  "unit": "tokens/s",
  "scope": "engine",
  "resource_id": "process-session-001",
  "source": "polystrata:/metrics",
  "provider_id": "engine.polystrata",
  "provider_version": "0.1",
  "observed_at": "2026-11-08T06:30:00Z",
  "availability": "available",
  "semantics": "Engine-reported decode throughput",
  "raw_name": "decode_tok_s"
}
```

Use typed DTOs in implementation. The JSON is illustrative.

## 5. Resource identity

### Host
Stable local installation identity, scoped to the host. Do not expose machine secrets or external identifiers.

### Process
Host scope + PID + process start time. Executable identity may corroborate. PID alone is insufficient.

### Physical GPU
Preferred identity order:
1. vendor UUID/stable native device ID;
2. PCI BDF (domain:bus:device.function);
3. platform-native stable identifier;
4. weak fallback fingerprint, explicitly labelled.

Enumeration index is a transient locator and must not be the historical primary key.

### Endpoint/session
Endpoint identity is separate from process identity. Remote endpoints use endpoint-scoped sessions and do not claim local process identity.

## 6. Initial metric catalogue

| Name | Scope | Unit | Notes |
|---|---|---|---|
| prompt_tokens_per_second | engine | tokens/s | Prompt/prefill semantics source-defined |
| decode_tokens_per_second | engine | tokens/s | Decode throughput |
| requests_active | engine | requests | Only if exposed |
| requests_total | engine | requests | Counter, not active count |
| queue_depth | engine | requests | Only if exposed |
| context_tokens | engine/session | tokens | Define exact source meaning |
| gpu_utilization | device | % | Physical device/provider |
| gpu_vram_used / gpu_vram_total | device | bytes | Physical device memory |
| gpu_temperature | device | °C | Physical device |
| gpu_power | device | W | Physical device |
| gpu_pcie_link | device | source-defined | Preserve generation/width semantics |
| gpu_process_memory | process/device | bytes | Only if provider exposes reliable attribution |
| cpu_utilization | host | % | Document aggregate/per-core semantics |
| system_ram_used | host | bytes | OS view |
| process_rss | process | bytes | Resident set only |
| disk_read/write_bytes_per_sec | host | bytes/s | Interval delta |
| expert_cache_hit_rate | runtime subsystem | native ratio or % | Preserve source scale/definition |
| pcie_share | runtime subsystem | source-defined | Do not conflate with physical link throughput |
| kv_cache_used | runtime subsystem | source-defined | Preserve original unit |
| arena_used | runtime subsystem | source-defined | Do not assume disjointness |
| draft_acceptance | runtime subsystem | native ratio or % | Only if exposed |

## 7. Memory accounting

Keep separate:
- physical VRAM used/total;
- process-attributed GPU memory;
- engine KV cache;
- expert cache;
- arena allocation;
- pinned host memory;
- process RSS;
- memory-mapped pages;
- OS page cache.

These categories may overlap. Never sum them unless the source guarantees they are disjoint. Engine-reported cache metrics are not a substitute for physical GPU accounting. GPU providers do not reinterpret engine-internal metrics.

## 8. Provider capability model

Providers declare capability availability per device. Example:

```json
{
  "provider_id": "gpu.amd_smi",
  "device_id": "pci-0000-03-00.0",
  "capabilities": {
    "gpu.utilization": "available",
    "gpu.memory": "available",
    "gpu.temperature": "available",
    "gpu.power": "available",
    "gpu.pcie.link": "temporarily_unavailable",
    "gpu.process_memory": "unsupported"
  }
}
```

Illustrative only; actual values must come from the running provider. Capability discovery is not proof that every sample succeeds.

## 9. Correlation and sampling

Every collector cycle has a cycle_id and one host_sample_id. Endpoint observations reference that host sample. Host CPU/RAM/disk is persisted once. Physical GPU device observations are stored once per selected provider/device per cycle, not duplicated into each endpoint.

If multiple providers report the same physical device, merge only with stable identity evidence and a defined source-selection policy. Never sum duplicate samples.

## 10. Example snapshot

```json
{
  "schema_version": 2,
  "cycle_id": "cycle-000123",
  "observed_at": "2026-11-08T06:30:00Z",
  "host_sample_id": "host-000123",
  "host": {"metrics": {}},
  "devices": [
    {
      "device_id": "pci-0000-03-00.0",
      "identity_strength": "strong",
      "vendor": "amd",
      "provider_id": "gpu.amd_smi",
      "metrics": {}
    }
  ],
  "endpoints": [
    {
      "endpoint_id": "local-8080",
      "session_id": "session-001",
      "engine": "polystrata",
      "state": "connected",
      "process": {"pid": 18471, "start_time": "platform-token"},
      "host_sample_id": "host-000123",
      "metrics": {}
    }
  ]
}
```

The schema version is a proposed next version. Define migration/compatibility rules before implementation; do not silently reinterpret existing records.

## 11. Prometheus exposition

Use a tested parser for metric families, labels, escapes, comments, counters and floating-point values. Do not parse by naive string splitting. Preserve original names/labels as provenance. Avoid a mandatory Prometheus server/client dependency for MVP.

## 12. Aggregation

Do not aggregate across engines, devices or vendors by default. Any aggregate must define semantic comparability, weighting, device identity, time alignment and missing-value handling.
