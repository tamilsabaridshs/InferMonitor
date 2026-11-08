# Component and Module Design

**Status:** Proposed. Keep the first implementation small and extract modules as responsibilities grow.

## Proposed logical structure

```text
InferMonitor/
├── app.py
├── config.py
├── core/
│   ├── context.py
│   ├── registry.py
│   ├── lifecycle.py
│   ├── capabilities.py
│   └── events.py
├── application/
│   ├── collector.py
│   ├── scheduler.py
│   ├── discovery.py
│   ├── fingerprint.py
│   ├── sessions.py
│   └── snapshot.py
├── plugins/
│   ├── engines/ (polystrata.py, llamacpp.py)
│   ├── platforms/ (linux/, windows/, macos/)
│   ├── hardware/ (amd/, nvidia/, intel/, apple/)
│   └── storage/ (jsonl/)
├── telemetry/ (models.py, metrics.py, resources.py, provenance.py)
├── api.py
├── web/ (index.html, app.js, style.css)
└── tests/ (unit/, contracts/, integration/, fixtures/)
```

This is a logical target, not a requirement to create every directory in the MVP. Begin with a small flat layout and split packages when there is more than one real implementation or a clear cohesion boundary.

## Responsibilities

- **Plugin kernel:** built-in plugin registration, service/capability ownership, dependency validation, lifecycle, health and cleanup. No recurring polling or persistence.
- **Configuration:** defaults, validation, endpoint definitions, enabled built-in providers and safe options. No arbitrary import paths.
- **Scheduler/collector:** owns poll cadence, cycle IDs, timeouts, bounded concurrency and invokes providers.
- **Discovery:** endpoint reachability, bounded HTTP evidence and local process identity supplied by platform provider.
- **Fingerprinter:** validated engine signatures, evidence/confidence or Unknown.
- **Engine adapter:** health and engine metrics; preserves native metric names/units/semantics. No host/GPU sampling, sessions, storage or UI.
- **Platform provider:** OS identity, process listener lookup/identity, CPU, RAM and disk. No vendor GPU assumptions.
- **GPU provider:** device discovery, stable device identity, capability discovery and physical device metrics. No process listener discovery or engine cache interpretation.
- **Session manager:** endpoint/process lifetime transitions; strong local identity requires PID plus process start time.
- **Telemetry model:** canonical DTOs with resource scope, stable identity, unit, timestamp, source, availability and semantics.
- **Snapshot assembler:** correlates one shared host sample, device samples and endpoint observations.
- **History:** versioned JSONL append/read/recovery/retention. Providers do not write directly.
- **API/UI:** serve cached snapshots and history; browser does not poll inference endpoints.

## Dependency direction

```text
API/UI --> Snapshot + History
Scheduler --> Discovery + Sessions + Engine adapters + Platform/GPU providers
Plugin kernel --> Registration + dependency/lifecycle services
Engine adapters --> Engine telemetry contracts
Platform providers --> Platform contracts
GPU providers --> GPU/device contracts
All providers --> Canonical telemetry DTOs
Snapshot assembler --> Telemetry DTOs
History --> Versioned records
```

Avoid circular dependencies. Core orchestration must not import vendor libraries or OS-specific modules. Only the relevant provider module may import its platform/vendor binding, and optional imports must fail gracefully.

## Composition rules

1. Engine, platform and GPU provider categories are independent.
2. A platform provider does not imply a GPU provider; a GPU provider does not imply process discovery.
3. Multiple GPU devices and mixed vendors are supported by inventory, not a single `GPU 0` assumption.
4. Each provider declares capabilities per device/host; unsupported optional metrics do not fail the entire provider.
5. Scheduler samples host and physical devices once per cycle; engine metrics are per unique process/adapter context where safe.
6. Provider failure is isolated and visible in diagnostics.
7. Plugins are built-in and allow-listed initially; no arbitrary dynamic loading or hot reload.
8. No provider owns persistence, dashboard, API or an independent recurring loop.

## Why this decomposition

This prevents an OS × GPU vendor × engine Cartesian product. A Linux process provider can coexist with AMD, NVIDIA, Intel or no GPU provider. A Windows provider can reuse the same engine adapter and canonical telemetry contracts. The cost is a small set of explicit interfaces and compatibility tests; that is preferable to platform/vendor conditionals spreading through the core.
