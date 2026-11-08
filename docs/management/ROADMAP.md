# Delivery Roadmap

## Phase 0 — Documentation and contracts
Review BRD/PRD/scope; capture real PolyStrata and llama.cpp fixtures; validate signatures and metric semantics; finalise telemetry DTO and JSONL schema. **Exit:** target versions and fingerprints are evidence-backed.

## Phase 1 — Companion skeleton
Configuration loader/validation; one collector loop and cycle IDs; local HTTP API and static UI shell; endpoint probing. **Exit:** UI/API report reachability.

## Phase 2 — Discovery and sessions
Linux socket/PID discovery and process start-time identity; multi-signal fingerprints; Unknown fallback; same-port switching; three endpoint maximum. **Exit:** port-switch and three-target tests pass.

## Phase 3 — Engine adapters
PolyStrata and llama.cpp adapters; version-labelled fixtures; normalised telemetry with provenance and null semantics. **Exit:** engine metrics correctly displayed.

## Phase 4 — Shared host telemetry
CPU/RAM/disk provider; AMD GPU provider where reliable tooling exists; one host sample per cycle. **Exit:** all endpoint observations reference shared host sample.

## Phase 5 — History and dashboard
JSONL persistence/recovery/retention; session-aware history; endpoint cards, host panel and diagnostics. **Exit:** browser closure does not stop recording; history survives restart.

## Phase 6 — Hardening and release
Security/resilience/performance tests; installation guidance; declare tested engine/provider versions. **Exit:** MVP acceptance suite passes.

## Deferred
SQLite, Prometheus exporter, Grafana, remote agents, distributed aggregation, alerting and additional frameworks. Reconsider only when requirements justify them.