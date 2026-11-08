# Platform Provider Contract

**Status:** Proposed architecture baseline  
**Initial target:** Linux  
**Future targets:** Windows and macOS  
**Related requirements:** REQ-PLAT-01..12, REQ-PROC-01..08

## 1. Purpose

Define operating-system-specific capabilities behind stable contracts. Core application code must not import procfs, sysfs, Windows APIs, macOS frameworks or platform-specific command-line tools.

Platform providers describe the host on which InferMonitor runs. GPU-vendor providers are separate and may be composed with any supported platform where the vendor supports that combination.

## 2. Requirements and rationale

| ID | Requirement | Reason |
|---|---|---|
| REQ-PLAT-01 | Detect and report host OS, release and architecture. | Diagnostics and compatibility decisions need host provenance. |
| REQ-PLAT-02 | Provide process listener lookup where local permissions permit. | Correlate endpoint with its serving process. |
| REQ-PLAT-03 | Provide process identity including PID and process start time. | PID reuse must not merge sessions. |
| REQ-PLAT-04 | Provide executable identity without requiring full command-line persistence. | Corroborate engine detection while limiting sensitive data. |
| REQ-PLAT-05 | Provide host CPU and RAM telemetry. | Shared host panel independent of engine count. |
| REQ-PLAT-06 | Provide disk activity where supported. | Host-level performance context. |
| REQ-PLAT-07 | Report capability and permission availability per field. | Different OS versions/permissions expose different fields. |
| REQ-PLAT-08 | Use stable process identity semantics across platforms. | Session logic must be portable. |
| REQ-PLAT-09 | Never assume an OS provider implies a GPU vendor or runtime. | Avoid OS/GPU coupling. |
| REQ-PLAT-10 | Keep platform calls bounded and read-only. | Protect responsiveness and least privilege. |
| REQ-PLAT-11 | Isolate platform-specific code within provider modules. | Enable independent platform testing. |
| REQ-PLAT-12 | Declare tested OS versions and limitations. | Avoid claiming unsupported compatibility. |

## 3. Contract boundaries

Conceptual interfaces:

```python
class PlatformInfoProvider:
    def get_host_info(self): ...

class ProcessDiscoveryProvider:
    def list_listeners(self, address, port): ...
    def get_process_identity(self, pid): ...
    def get_executable_identity(self, pid): ...

class SystemTelemetryProvider:
    def collect_cpu(self): ...
    def collect_memory(self): ...
    def collect_disk(self): ...
```

The exact contracts should return typed results with timestamps, source, availability and structured errors rather than raw platform objects.

## 4. Process identity

Canonical local process identity should contain:
- host identity (local installation/host scope);
- PID;
- process creation/start time in a platform-independent UTC or monotonic-safe representation;
- executable identity (path/hash/signature where available and permitted);
- identity confidence/source.

PID alone is never sufficient. Process start time is mandatory for a strong local identity. If permissions prevent reading it, mark identity weak/unknown and do not claim certainty.

Do not persist full command lines by default. Read only the minimum executable/argument evidence needed for detection, redact secrets and keep raw values transient.

Remote endpoints have no local process identity. They use endpoint-scoped sessions and must not claim OS-process certainty.

## 5. Platform implementations

### Linux (initial)
Use procfs/sysfs and supported OS interfaces where practical. Process listener resolution may require privileges depending on socket ownership and namespace. Process start time must be read with correct procfs semantics; do not treat PID directory existence as proof of identity.

### Windows (future)
Use documented Windows process and performance APIs. Handle access-denied and process-exited races. Do not shell out to PowerShell for every polling cycle.

### macOS (future)
Use documented process/system APIs. Treat GPU telemetry as a separate Apple/Metal provider concern.

## 6. Sampling

Platform providers expose bounded point-in-time or interval-based samples. Disk throughput requires deltas between monotonic-time observations; the provider or sampler must define reset/wrap behaviour. CPU percentages must document interval and normalization (whole-host vs per-core).

Host telemetry is sampled once per collector cycle, not once per endpoint.

## 7. Acceptance tests

- Same PID with changed process start time creates a new process session.
- PID change creates a new session.
- Process exit during lookup returns a structured race/unavailable result.
- Permission denied is not reported as zero or as a process absence.
- Three endpoints sharing one host still cause one host sample per cycle.
- Platform provider absence does not prevent HTTP engine telemetry.
- Windows/macOS implementations must pass the same contract suite before being declared supported.
