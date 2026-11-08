# Delivery Roadmap

The roadmap sequences work to minimise rework: stabilise contracts before platform/vendor integrations, then implement the first validated vertical slice.

## Phase 0 — Requirements and architecture baseline
- Review BRD/PRD/scope and attached primary requirements.
- Adopt the Cordis-inspired in-process kernel, not the full framework.
- Finalise plugin, platform, GPU and engine adapter contracts.
- Finalise telemetry identity, availability, provenance and JSONL schema/versioning.
- Capture real PolyStrata and llama.cpp fixtures; validate signatures and metric semantics.

**Exit:** architecture decisions approved; requirement IDs mapped to contract tests; target runtime versions and fingerprints evidence-backed.

## Phase 1 — Plugin kernel and companion skeleton
- Configuration loader/validation.
- Built-in plugin registry, dependency validation, lifecycle, health and cleanup.
- One collector loop and cycle IDs.
- Local HTTP API and static UI shell; endpoint probing.
- No arbitrary plugin loading or hot reload.

**Exit:** lifecycle tests pass; UI/API report reachability; optional plugin failure does not stop application startup.

## Phase 2 — Linux platform and process discovery
- Linux host identity, listener/PID discovery and process start-time identity.
- CPU/RAM/disk provider.
- Multi-signal fingerprints and Unknown fallback.
- Same-port switching; three endpoint maximum.

**Exit:** AT-01..AT-08 and PT contract tests pass.

## Phase 3 — Engine adapters
- PolyStrata and llama.cpp adapters.
- Version-labelled fixtures.
- Normalised telemetry with provenance and null/availability semantics.

**Exit:** engine metrics correctly displayed; adapter failures isolated.

## Phase 4 — AMD GPU provider and shared hardware telemetry
- AMD SMI provider where supported by the exact installed platform/driver.
- GPU inventory and stable device identity.
- Capability discovery for utilisation, memory, temperature, power and optional PCIe/process metrics.
- One host sample and one selected device sample per cycle.

**Exit:** RX 9070 Linux integration tests record OS, device, driver, AMD SMI/ROCm versions and field availability; GT tests pass. Do not assume every requested metric is exposed.

## Phase 5 — History and dashboard
- JSONL persistence/recovery/retention.
- Session-aware history and device identity history.
- Endpoint cards, shared host panel, device panels and diagnostics.

**Exit:** browser closure does not stop recording; history survives restart; unavailable metrics are explained.

## Phase 6 — Hardening and MVP release
- Security, resilience and performance tests.
- Measure baseline overhead with one, two and three endpoints.
- Installation guidance and compatibility matrix.

**Exit:** all MVP acceptance tests pass; publish only tested engine/provider/OS combinations.

## Phase 7 — Additional providers
1. Linux + NVIDIA NVML.
2. Windows platform/process provider.
3. Windows + AMD/NVIDIA GPU providers where officially supported and locally validated.
4. Intel Level Zero on supported Linux/Windows systems.
5. macOS platform and Apple GPU investigation.

Each provider must pass the same contract suite. These are roadmap targets, not current compatibility claims.

## Deferred
SQLite, Prometheus exporter, Grafana, remote agents, distributed aggregation, alerting, arbitrary third-party plugin distribution, hot reload, plugin marketplace, message brokers, containers and a full Cordis runtime. Reconsider only when requirements justify them.
