# Business Requirements Document (BRD)

**Product:** InferMonitor | **Version:** 1.0 proposed baseline | **Date:** 2026-11-08 | **Status:** For review

## Executive summary
InferMonitor is a local companion for observing self-hosted LLM inference servers. It unifies engine-level inference telemetry and host-level resource measurements without modifying inference engines. Runtimes expose different metrics, dashboards are runtime-specific, and GPU/CPU/memory data must be correlated manually. A port may be reused by different processes; port-only identification can misattribute telemetry.

## Business objectives
1. One local dashboard for multiple inference processes.
2. Identify the engine actually serving each endpoint.
3. Detect process replacement/restart and port reuse without mixing sessions.
4. Correlate per-engine metrics with one shared host sample per cycle.
5. Persist local history beyond browser closure and companion restart.
6. Reuse existing HTTP endpoints and OS facilities.

## Stakeholders
| Stakeholder | Need |
|---|---|
| Local inference operator | Throughput, health and resource-pressure visibility |
| Runtime/model experimenter | Compare runtime behaviour and configurations |
| Maintainer | Lightweight, testable and maintainable implementation |

## Current-state problem
- PolyStrata and llama.cpp expose different telemetry formats.
- Either engine may use port 8080 at different times.
- Multiple servers may run simultaneously on separate ports.
- Browser-only views do not guarantee persistent history.
- Physical GPU metrics are host-level and should not be duplicated per endpoint.
- Ports can be rebound and PIDs reused.

## Proposed capability
An independent local process probes configured endpoints, fingerprints HTTP responses, supplements identification with local process identity, selects an engine adapter, samples host telemetry once per cycle, and serves a local dashboard/API. Initial limit: three enabled endpoints.

## Outcomes and measures
| Outcome | Measure |
|---|---|
| Correct engine identification | Supported fingerprint tests pass; unknown services remain Unknown |
| Lifecycle awareness | Changed process identity creates a new session |
| Multi-target monitoring | Three endpoints observed in one instance |
| Shared host sampling | One host sample per collector cycle |
| Durable history | Data remains after browser closure and companion restart |
| Low operating burden | No mandatory database, broker, container or external service |

Detection latency and monitoring overhead budgets will be measured during MVP; no unmeasured performance claims are made.

## Scope
**In:** Linux-first local monitoring, PolyStrata and llama.cpp, auto-detection/manual override, maximum three endpoints, shared host telemetry, process-session awareness, dashboard/API, JSONL history, diagnostics.

**Out:** server lifecycle management, model management, inference routing, load balancing, training orchestration, GPU tuning, engine modification, cloud upload and remote fleet monitoring.

## Assumptions and constraints
- Linux is initial platform; AMD ROCm is the reference hardware environment.
- Engines are accessed through existing HTTP interfaces.
- Local process inspection may be unavailable for remote endpoints or restricted permissions.
- Metric availability varies by engine version, flags and hardware provider.
- Missing measurements are null/N/A, never fabricated as zero.

## Risks
| Risk | Mitigation |
|---|---|
| Fingerprints change across versions | Versioned fixtures, multiple signals, Unknown fallback |
| Metrics endpoint stalls | Bounded timeouts and per-endpoint failure isolation |
| PID reuse/port handoff | PID plus process start time and session boundaries |
| Hardware provider unavailable | Provider abstraction and explicit N/A |
| Polling overhead | Configurable interval and measured overhead |
| Memory metrics overlap | Document scopes; do not sum overlapping figures |

## Business acceptance
Demonstrate same-port PolyStrata/llama.cpp distinction; up to three concurrent endpoints; new session after process replacement; one shared host sample; correct N/A semantics; and continued operation when one target is unavailable.

## Governance
Proposed baseline for review. Scope or architecture changes update relevant requirements and ADRs.