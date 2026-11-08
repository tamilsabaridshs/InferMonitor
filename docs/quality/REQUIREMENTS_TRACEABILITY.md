# Requirements Traceability Matrix

This matrix connects the primary requirements to architecture documents and acceptance tests. Requirement IDs introduced in the provider/plugin design are normative design requirements; implementation is not yet complete.

| Requirement | Design reference | Test / acceptance |
|---|---|---|
| Three endpoint maximum | PRD, config, architecture | AT-03, AT-15 |
| Same-port runtime switching | Process discovery, ADR-002 | AT-01, AT-02 |
| Process lifetime identity | Platform contract, process discovery, data lifecycle | AT-06, AT-07, PT-02 |
| Alias deduplication | Process discovery, architecture | AT-05 |
| Shared host sampling | Architecture, telemetry model, ADR-003 | AT-12 |
| PolyStrata/llama.cpp parsing | Engine adapter contract | Versioned fixture tests |
| Unknown fallback | Process discovery | AT-08 |
| Endpoint failure isolation | Architecture, API | AT-04, AT-13 |
| JSONL durability | Data lifecycle, history ADR | AT-10, AT-11, AT-14 |
| Null/missing semantics | Telemetry model | AT-09, GT-04 |
| Local-only default | Security | AT-16 |
| Browser-independent collection | Architecture, PRD | AT-10 |
| Config validation | Configuration | AT-15 |
| Plugin registration and unique IDs (REQ-PLUG-01,05) | Plugin architecture, ADR-004 | PL-01 |
| Required/optional dependency resolution (REQ-PLUG-02) | Plugin architecture | PL-02, PL-03 |
| Lifecycle and deterministic cleanup (REQ-PLUG-03,10) | Plugin architecture | PL-04 |
| Failure isolation (REQ-PLUG-04) | Plugin architecture, system architecture | PL-05 |
| Scheduler-owned polling (REQ-PLUG-06) | Plugin architecture, system architecture | PL-06 |
| Built-in allow-list / no arbitrary loading (REQ-PLUG-08) | Plugin architecture, security | PL-07 |
| Plugin health/diagnostics (REQ-PLUG-09) | Plugin architecture | PL-08 |
| OS abstraction (REQ-PLAT-01..12) | Platform provider contract, ADR-005 | PT-01..PT-06 |
| Stable GPU identity (REQ-GPU-01..04,13,18) | GPU provider contract, telemetry model | GT-01, GT-02 |
| Partial metric capabilities (REQ-GPU-05..08) | GPU provider contract, telemetry model | GT-03, GT-04 |
| GPU sample deduplication (REQ-GPU-09,18) | GPU provider contract, architecture | GT-05 |
| GPU provenance and optional dependencies (REQ-GPU-10..16) | GPU provider contract, plugin architecture | GT-06, GT-07 |
| Memory attribution semantics (REQ-GPU-17, REQ-MEM-01..08) | GPU provider contract, telemetry model | GT-08 |

## New contract test groups

### Plugin lifecycle (PL)
- **PL-01:** duplicate plugin IDs and exclusive service registrations are rejected.
- **PL-02:** missing required dependency prevents dependent plugin activation.
- **PL-03:** missing optional dependency yields DEGRADED state; unrelated plugins start.
- **PL-04:** dependency order starts correctly; reverse cleanup is attempted for every disposer.
- **PL-05:** one provider failure does not stop other providers or endpoints.
- **PL-06:** providers do not create polling loops; scheduler invokes bounded collection.
- **PL-07:** unlisted/dynamic plugin modules are not loaded from configuration.
- **PL-08:** plugin health exposes ID, version, lifecycle state and diagnostic reason.

### Platform provider (PT)
- **PT-01:** host OS/release/architecture are reported with provenance.
- **PT-02:** PID plus changed process start time creates a new identity/session.
- **PT-03:** permission denial and process-exit races are explicit, not zero/absent guesses.
- **PT-04:** host sample occurs once per cycle regardless of endpoint count.
- **PT-05:** platform provider failure does not prevent engine HTTP telemetry.
- **PT-06:** Linux/Windows/macOS implementations pass the same contract suite before support is claimed.

### GPU provider (GT)
- **GT-01:** device identity remains stable when enumeration order changes where stable IDs exist.
- **GT-02:** two or more devices and mixed vendors are represented independently.
- **GT-03:** unavailable optional metric does not disable other metrics.
- **GT-04:** unsupported, permission denied, temporarily unavailable and provider error are distinct.
- **GT-05:** duplicate providers do not create duplicate physical-device samples.
- **GT-06:** provider/device/driver/library provenance is captured.
- **GT-07:** missing vendor library does not prevent companion startup.
- **GT-08:** physical VRAM, process GPU memory and engine cache/arena metrics are not incorrectly summed.

## Existing acceptance tests

| ID | Scenario | Expected result |
|---|---|---|
| AT-01 | PolyStrata on 8080 | Detected only when validated signature matches |
| AT-02 | Replace PolyStrata with llama.cpp on 8080 | New engine/session; no mixed history |
| AT-03 | Three supported servers on separate ports | All independently visible |
| AT-04 | One target times out | Other targets continue |
| AT-05 | Two endpoint aliases resolve to same process | Process collection deduplicated where valid |
| AT-06 | PID same, process start time changes | New session |
| AT-07 | PID changes | New session |
| AT-08 | Unknown HTTP 200 service | Unknown, not guessed |
| AT-09 | Metric absent | Null with reason, not zero |
| AT-10 | Browser closed | Collector/history continue |
| AT-11 | Companion restarted | History recovered; server identity reconfirmed |
| AT-12 | Three targets in one cycle | Exactly one host sample |
| AT-13 | Malformed exposition | Adapter error isolated |
| AT-14 | Partial trailing JSONL record | Prior valid records readable |
| AT-15 | More than three enabled endpoints | Configuration rejected |
| AT-16 | Remote bind attempt | Not enabled by default; requires future security design |

## Evidence and release policy

A requirement is not considered implemented merely because a document describes it. Each engine/platform/GPU provider must pass fixtures and integration tests against recorded versions. Release notes must distinguish designed, implemented, locally tested and officially supported states.
