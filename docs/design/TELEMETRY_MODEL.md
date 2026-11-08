# Telemetry Catalogue and Data Semantics

## Principles
Each metric has a name, value, unit, scope, source and observation timestamp. Preserve source semantics. Unsupported values are null with an availability reason, never zero.

## Scopes
| Scope | Examples | Sampling |
|---|---|---|
| Host | CPU, system RAM, disk IO, physical GPU utilisation/VRAM/temp/power | Once per cycle |
| Process | PID, process start time, RSS, CPU time | Per unique process |
| Engine | prompt/decode throughput, requests, queue/slot information | Per engine adapter context |
| Runtime subsystem | KV, expert cache, arena, draft/MTP | Per engine |
| Session | start/end, engine/process identity | Lifecycle events |

## Canonical metric envelope
```json
{
  "name": "decode_tokens_per_second",
  "value": 18.4,
  "unit": "tokens/s",
  "scope": "engine",
  "source": "polystrata:/metrics",
  "observed_at": "2026-11-08T06:30:00Z",
  "availability": "available",
  "semantics": "Engine-reported decode throughput"
}
```
Unavailable fields use null and a reason such as unsupported, not_exposed, provider_unavailable or temporarily_unavailable.

## Initial catalogue
| Name | Scope | Unit | Notes |
|---|---|---|---|
| prompt_tokens_per_second | engine | tokens/s | Prompt/prefill semantics source-defined |
| decode_tokens_per_second | engine | tokens/s | Decode throughput |
| requests_active | engine | requests | Only if exposed |
| requests_total | engine | requests | Counter, not active count |
| queue_depth | engine | requests | Only if exposed |
| context_tokens | engine/session | tokens | Define exact source meaning |
| gpu_utilization | host | % | Physical device/provider |
| gpu_vram_used / gpu_vram_total | host | bytes | Physical device memory |
| gpu_temperature | host | °C | Physical device |
| gpu_power | host | W | Physical device |
| cpu_utilization | host | % | Aggregate host |
| system_ram_used | host | bytes | OS view |
| process_rss | process | bytes | Resident set only |
| disk_read/write_bytes_per_sec | host | bytes/s | Interval delta |
| expert_cache_hit_rate | runtime subsystem | native ratio or % | Preserve source scale/definition |
| pcie_share | runtime subsystem | source-defined | No unverified conversion |
| kv_cache_used | runtime subsystem | source-defined | Preserve original unit |
| arena_used | runtime subsystem | source-defined | Do not assume disjoint from VRAM |
| draft_acceptance | runtime subsystem | native ratio or % | Only if exposed |

## Memory accounting
Keep physical VRAM, KV cache, expert cache, arena, pinned host memory, process RSS, mmap pages and OS page cache distinct. These can overlap; never sum them unless the source guarantees disjointness.

## Correlation
Every cycle has cycle_id and one host_sample_id. Endpoint observations reference that host sample. Persist host metrics once, not once per endpoint.

## Example snapshot
```json
{"schema_version":1,"cycle_id":"cycle-000123","observed_at":"2026-11-08T06:30:00Z","host_sample":{"host_sample_id":"host-000123","metrics":{"gpu_utilization":{"value":72,"unit":"%","availability":"available"}}},"endpoints":[{"endpoint_id":"local-8080","session_id":"session-001","engine":"polystrata","state":"connected","process":{"pid":18471,"start_time":"proc-start-token"},"host_sample_id":"host-000123","metrics":{"decode_tokens_per_second":{"value":18.4,"unit":"tokens/s","availability":"available"}}}]}
```

## Prometheus exposition
Use a tested parser for metric families, labels, escapes, comments, counters and floating-point values. Do not parse by naive string splitting. Preserve original names/labels as provenance. Avoid a mandatory Prometheus server/client dependency for MVP.

## Aggregation
Do not aggregate across engines by default. Any aggregate must define comparability, weighting and time alignment.