# Component and Module Design

## Proposed repository structure
```text
InferMonitor/
├── README.md
├── LICENSE
├── pyproject.toml
├── config.example.json
├── app.py
├── infermonitor/
│   ├── config.py
│   ├── collector.py
│   ├── discovery.py
│   ├── fingerprint.py
│   ├── sessions.py
│   ├── snapshot.py
│   ├── history.py
│   ├── api.py
│   ├── metrics.py
│   ├── host/ (base.py, linux.py, amd_rocm.py)
│   └── adapters/ (base.py, polystrata.py, llamacpp.py)
├── web/ (index.html, app.js, style.css)
├── tests/ (fixtures and focused module tests)
└── data/.gitkeep
```
Proposed structure, not existing code. Keep modules flat until complexity justifies nesting.

## Responsibilities
- **Discovery:** endpoint config in; probe evidence, HTTP capabilities and optional process identity out. Never infer engine from port alone.
- **Fingerprinter:** evidence in; engine ID, evidence/confidence or Unknown out.
- **Adapter:** normalised engine metrics and provenance; no collector loop, host sampling, persistence or UI.
- **Host provider:** OS/device metrics independent of endpoint count, with provider/version and field availability.
- **Session manager:** endpoint-to-session mapping; PID plus process start time when available; label weaker identity.
- **Snapshot assembler:** one cycle snapshot; each target references one host sample ID.
- **History:** versioned JSONL, tolerate incomplete final line, do not silently reinterpret unknown schema.
- **API/UI:** serve cached snapshot; browser is not a collector.

## Dependency direction
```text
API/UI --> Snapshot + History
Collector --> Discovery + Adapters + Host + Sessions + Snapshot + History
Adapters --> Canonical metric DTOs
Host providers --> Host DTOs
Config --> configured components
```
Avoid circular dependencies. Confine OS command execution to provider/discovery modules.