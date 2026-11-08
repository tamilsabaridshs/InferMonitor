# Product Requirements Document (PRD)

**Version:** 1.0 proposed baseline

## Vision
A small local observability companion that identifies the runtime actually serving an endpoint, shows inference behaviour, and correlates it with host resources without a heavyweight monitoring stack.

## Primary users
- Local inference operator: identify server and health on a port.
- Experimenter: correlate throughput, prompt processing, GPU and memory behaviour.
- Multi-runtime user: monitor several endpoints without confusing processes.

## P0 requirements
| ID | Requirement | Acceptance condition |
|---|---|---|
| PR-001 | Up to three endpoints | More than three enabled targets rejected |
| PR-002 | Automatic engine detection | Validated PolyStrata/llama.cpp fingerprints select adapters |
| PR-003 | Port reuse | Same port identifies either runtime on separate runs |
| PR-004 | Process identity | PID and process start time when locally available |
| PR-005 | Process sessions | Replacement starts new session; samples are not mixed |
| PR-006 | Concurrent targets | Three ports monitored in one instance |
| PR-007 | Deduplication | Aliases to same process do not duplicate process collection |
| PR-008 | Shared host sample | Host metrics sampled once per cycle |
| PR-009 | Live snapshot | Dashboard reads latest companion snapshot |
| PR-010 | Persistent history | JSONL survives browser closure and companion restart |
| PR-011 | Unknown fallback | Ambiguous engine is not guessed |
| PR-012 | Failure isolation | One unavailable target does not stop others |
| PR-013 | Missing values | Unsupported metrics are null/N/A, not zero |
| PR-014 | Local-only default | API binds to loopback by default |

## P1
Configurable retention/rotation, history queries, additional adapters/providers, export and richer diagnostics.

## P2 — optional future
Remote agents, multi-host aggregation, alerts, database-backed history and Prometheus integration. Not MVP commitments.

## UX
Show up to three endpoint/process cards and one shared physical-host panel. Endpoint cards include endpoint, state, detected engine, PID/session, runtime metadata when exposed, throughput and request metrics. Host panel shows GPU/CPU/RAM/disk and provider status. History distinguishes old and current process sessions. Diagnostics explain Unknown/Unavailable states.

Status vocabulary: Detecting, Connected, Unknown engine, Unavailable, Process changed, Disabled. Units and scope must be visible. Physical VRAM must be distinct from engine-internal caches. Missing metrics must not appear as zero.

## Core journeys
**Same-port switch:** configure 8080 → detect runtime → collect → replace runtime → detect identity/engine change → create a new session without mixing history.

**Three endpoints:** configure up to three ports → poll independently → sample host once → reference same host sample ID from each endpoint observation.

**Unknown service:** service responds without confident fingerprint → show Unknown and diagnostics → optional visibly labelled manual override.

## Functional rules
- Endpoint identity: normalized scheme, host, port and optional base path.
- Local process identity: host identity + PID + process start time.
- Runtime identity: engine/adapter plus observed version when available.
- Timeout alone does not prove replacement.
- Adapter failures are isolated.
- Engine name alone is insufficient for deduplication.

## Non-functional requirements
Simplicity, low overhead, bounded requests, explicit units/provenance, fault isolation, loopback-only default, replaceable adapters/providers and Linux-specific code behind interfaces.

## MVP exit
All P0 tests pass with version-labelled fixtures and real supported engine versions. Evidence covers port switch, three targets, restart, duplicate process, endpoint outage, host sample count, history recovery and Unknown behaviour.