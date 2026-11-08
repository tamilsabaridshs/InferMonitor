# MVP implementation notes

## Initial host target

The first runnable slice targets native Ubuntu/Linux on the Ryzen 7 9700X and Radeon RX 9070 16 GB (gfx1201) with ROCm/HIP. This is a target profile, not a claim that this connector environment has tested the user's workstation.

## Implemented components

- Python 3.11+ standard-library companion; no mandatory third-party runtime package.
- Small allow-listed plugin registry with lifecycle state and diagnostics.
- Linux procfs host CPU/RAM and disk throughput sampling; local TCP listener-to-process mapping; process start-time identity.
- AMD SMI command discovery and bounded JSON invocation. Raw device payload is retained because CLI schemas and units vary by ROCm release; canonical VRAM/temperature/power mapping is deliberately deferred until fixtures from the installed version are captured.
- PolyStrata/Strata JSON health and metrics adapter: /health, /props, /metrics, optional /metrics/prometheus.
- llama.cpp Prometheus /metrics adapter. Raw metric names, labels and values are retained.
- Three endpoint slots, session IDs, duplicate-process sampling avoidance, JSONL persistence and local dashboard/API.

## Important limitations before P0 completion

1. AMD SMI field mapping: capture amd-smi metric --json or rocm-smi --json from the target host, version-label it, then map utilization, VRAM, temperature and power with correct units. Until then GPU devices may be listed with raw payload only.
2. PolyStrata: adapter recognizes JSON signatures and preserves numeric leaves. It does not claim every field is semantically normalized. Add sanitized live fixtures from the installed strata-poly build. Supplied handoff observed /health, /props, /metrics and /metrics/prometheus; engine version 0.1.45 was observed.
3. llama.cpp: parser preserves exposition values. Counter rates and gauge semantics need fixtures from the exact llama.cpp build before derived rates are shown.
4. Process identity: procfs socket ownership may require additional privileges or may be hidden by namespaces/hardening. Weak/unknown identity is reported as such; PID-only strong identity is not fabricated.
5. History retention: JSONL append/query is implemented; automatic pruning/rotation and crash-safe compaction remain follow-up work.
6. Run the acceptance matrix on Ubuntu 26.04.1/kernel 7.0.0-38, ROCm 7.16/HIP, RX 9070 gfx1201, PolyStrata and llama.cpp before claiming hardware compatibility.

## Architecture rationale

The BRD/PRD prioritise Python standard library, local HTTP, plain HTML, JSONL and minimal dependencies. The registry uses Cordis ideas only for deterministic registration, lifecycle, capability boundaries and diagnostics. It is not a Cordis dependency or a general plugin marketplace.

## Run and test

See README. The companion binds to loopback and makes bounded GET-only requests to configured endpoints. It never stores prompts or completions.
