# InferMonitor

Local inference observability companion. Initial MVP target: native Ubuntu/Linux, AMD ROCm, PolyStrata/Strata and llama.cpp.

## Quick start

    python3 -m venv .venv
    . .venv/bin/activate
    python -m pip install -e .
    cp config/infermonitor.example.json config/infermonitor.json
    infermonitor

Open http://127.0.0.1:8090. Stop with Ctrl+C. Python 3.11+; no third-party runtime dependencies. AMD GPU telemetry is optional and uses amd-smi or rocm-smi JSON output when available.

## Initial capability scope

- Linux host CPU/RAM telemetry and local TCP listener-to-process lookup through procfs.
- AMD GPU telemetry through ROCm SMI CLI, best-effort and version-sensitive.
- PolyStrata JSON /health, /props, /metrics and optional /metrics/prometheus.
- llama.cpp Prometheus /metrics.
- Three endpoint slots, session-aware JSONL history and lightweight HTML dashboard.

Copy the example configuration and enable ports 8081/8082 as needed. Auto-detection is preferred; manual engine override is available. Unknown services remain Unknown.

## System inventory and memory breakdown

Phase 2 adds CPU/platform inventory, storage and network summaries, detailed Linux RAM categories, top-process RSS/PSS, swap, and best-effort AMD SMI per-process VRAM/GTT attribution. Values that cannot be read remain unavailable rather than being reported as zero. See [Phase 2 notes](docs/implementation/PHASE2-SYSTEM-MEMORY.md) for accounting semantics and limitations.

## Tests

    python -m unittest discover -s tests -v

## Safety and semantics

Loopback-only API, bounded read-only HTTP GET requests, no prompts/completions, no remote telemetry and no inference control. Raw engine metric names and source provenance are retained. PolyStrata JSON numeric fields are not assigned invented units. GPU field mapping must be validated against the installed ROCm SMI version before relying on it.
