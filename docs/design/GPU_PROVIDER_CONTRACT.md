# GPU Provider Contract

**Status:** Proposed architecture baseline  
**Initial target:** AMD GPU telemetry on Linux  
**Future targets:** NVIDIA, Intel and Apple platforms where supported  
**Related requirements:** REQ-GPU-01..18, REQ-MEM-01..08

## 1. Purpose

Define vendor-neutral GPU inventory and telemetry contracts while preserving vendor-specific semantics. This contract does not promise that all vendors or devices expose every metric.

GPU discovery, GPU telemetry, OS process discovery and inference-engine metrics are independent concerns.

## 2. Requirements and rationale

| ID | Requirement | Reason |
|---|---|---|
| REQ-GPU-01 | Discover physical GPU devices independently of engine endpoints. | Hardware exists even when no inference server is running. |
| REQ-GPU-02 | Assign stable device identity; do not persist enumeration index as identity. | Indices can change across reboot, driver or runtime changes. |
| REQ-GPU-03 | Record PCI BDF where available and vendor UUID/native ID where available. | Correlate devices across providers and restarts. |
| REQ-GPU-04 | Report vendor, model, device ID, architecture, driver and runtime provenance when exposed. | Diagnose compatibility and identify actual device. |
| REQ-GPU-05 | Discover per-metric capabilities. | Partial support must remain useful. |
| REQ-GPU-06 | Collect utilisation, physical VRAM, temperature and power where exposed. | Required initial hardware panel. |
| REQ-GPU-07 | Collect PCIe/link and per-process memory only where reliable and supported. | Optional advanced diagnostics; avoid fabricated values. |
| REQ-GPU-08 | Distinguish unsupported, permission denied, temporary unavailable and provider error. | Null must be explainable. |
| REQ-GPU-09 | Sample each physical device once per cycle per selected source. | Avoid duplicate work and double-counting. |
| REQ-GPU-10 | Preserve native units, scale, scope and source semantics. | Vendor metrics are not always directly comparable. |
| REQ-GPU-11 | Do not assume a GPU runtime from vendor or OS alone. | Driver/toolchain presence and runtime support differ. |
| REQ-GPU-12 | Optional vendor libraries must not be mandatory for application startup. | Users may have no supported GPU or driver. |
| REQ-GPU-13 | Device disappearance/re-enumeration must not corrupt history. | Hardware can be hot-plugged or reset. |
| REQ-GPU-14 | No elevated privileges by default. | Least-privilege local monitoring. |
| REQ-GPU-15 | No vendor provider may own its own recurring polling loop. | Scheduler owns sampling cadence. |
| REQ-GPU-16 | Record provider and library versions. | Reproducibility and diagnostics. |
| REQ-GPU-17 | Physical VRAM and engine-internal allocations remain separate. | Prevent overlapping memory values being summed. |
| REQ-GPU-18 | Support multiple GPUs and multiple vendors in inventory. | Future multi-device systems without redesign. |

## 3. Provider contract

Conceptual interface:

```python
class GpuProvider:
    provider_id: str

    def discover_devices(self): ...
    def get_capabilities(self, device_id): ...
    def collect(self, device_id, requested_capabilities): ...
    def health(self): ...
    def close(self): ...
```

Return typed device descriptors and metric observations, not unvalidated dictionaries in the production contract. Every metric observation includes:
- canonical metric name (when mapping is semantically valid);
- raw source metric name;
- value or null;
- unit;
- scope (device/process);
- observed timestamp;
- availability state and reason;
- provider ID/version;
- native semantics/notes.

## 4. Stable device identity

Use a hierarchy:
1. vendor UUID or stable native device ID, if available;
2. PCI domain:bus:device.function (BDF), if available;
3. platform-native stable identity;
4. fallback fingerprint clearly marked as weak.

Enumeration index is a transient locator only. Record it as an observation attribute, never as the primary historical key.

Do not assume PCI BDF is available for integrated or virtual devices. Do not silently merge devices when identity confidence is weak.

## 5. Capability catalogue

Initial capability identifiers:
- `gpu.utilization`
- `gpu.memory.total`
- `gpu.memory.used`
- `gpu.temperature`
- `gpu.power`
- `gpu.pcie.link`
- `gpu.pcie.throughput`
- `gpu.process_memory`
- `gpu.clock`
- `gpu.fan`

A provider reports capability state per device and may include a reason. Capability states:
- available;
- unsupported;
- permission_denied;
- temporarily_unavailable;
- provider_error;
- not_probed.

Do not mark an entire provider failed because one optional capability is unavailable.

## 6. Vendor integration strategy

Use official or vendor-supported APIs where practical; avoid parsing CLI text as the primary long-term contract.

| Vendor/platform | Candidate integration | Qualification |
|---|---|---|
| AMD Linux | AMD SMI | Validate exact GPU, driver/runtime and fields; ROCm presence alone is not proof all metrics are available. |
| NVIDIA Linux/Windows | NVML | Validate library availability, driver version and permissions. |
| Intel Linux/Windows | Level Zero Sysman | Validate GPU and driver coverage for each field. |
| Apple macOS | Metal/system interfaces | Separate investigation required; do not promise parity with discrete GPU APIs. |

These are candidate technologies, not completed integrations or a guarantee of identical metric coverage.

## 7. Memory semantics

Keep distinct:
- physical device memory used/total;
- process-attributed device memory;
- engine-reported KV cache;
- expert cache;
- arena allocation;
- pinned host memory;
- process RSS;
- mmap pages and OS page cache.

These categories may overlap. Do not sum them unless the source documents that they are disjoint. Every engine-internal metric retains its engine source and semantics; a GPU provider must not reinterpret it.

## 8. Multi-provider and deduplication policy

A machine may have AMD and NVIDIA devices simultaneously. Discover devices across enabled providers and merge only when stable identity proves they refer to the same physical device. If two providers expose the same device, choose a configured/preferred source per capability or report source conflict; never sum duplicate readings.

The scheduler samples one selected provider per device/capability set per cycle. Host sample stores a device collection, not a single assumed GPU.

## 9. Failure and lifecycle

- Missing vendor library: provider unavailable; other providers continue.
- Permission denied: report field state; do not escalate privileges.
- Device reset/disappearance: mark unavailable and retain prior history.
- Driver/runtime mismatch: provider diagnostic with version information.
- One metric parser failure: isolate that metric where possible; do not discard unrelated devices.
- Provider shutdown: release native handles.

## 10. Acceptance tests

- Device identity remains stable when enumeration order changes, where stable OS/vendor identity exists.
- Two GPUs are represented independently.
- Mixed-vendor devices are represented without vendor assumptions in core.
- Missing temperature does not remove utilisation or memory.
- Missing optional library does not prevent companion startup.
- Provider errors do not stop engine adapters or other providers.
- Device metrics include provider, timestamp, units and availability.
- Duplicate providers do not create duplicate physical-device samples.
- Engine KV/expert/arena values are not added to physical VRAM totals.
