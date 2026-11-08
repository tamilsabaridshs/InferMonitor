# Process Discovery and Engine Identification

## Objective
Determine which service is actually serving each endpoint now. A port is an address, not process identity.

## Discovery sequence
1. Check TCP/HTTP reachability.
2. Fetch low-cost identification endpoints with bounded timeouts and response sizes.
3. Inspect response content/shape fingerprints.
4. Resolve local listening PID where permissions/platform allow.
5. Read process start time, executable and only necessary command-line evidence.
6. Combine evidence and select a supported adapter only when fingerprint rules match.
7. Otherwise report Unknown/ambiguous with diagnostics.

## Candidate fingerprints
**PolyStrata:** validate expected response fields from health, properties and metrics interfaces, including distinctive Strata fields where applicable.

**llama.cpp:** validate known metric families/labels from Prometheus exposition when enabled; optional metadata endpoints may supplement it.

Schemas and metric names vary by release/build/options. Exact signatures must be validated against captured fixtures before implementation is supported. HTTP 200 alone is not a fingerprint.

## Evidence policy
HTTP contract fingerprints are primary; local process information corroborates. Material conflicts produce Unknown/ambiguous. Manual override is allowed but visibly labelled and subject to adapter parse errors.

## Identity
Preferred local identity: machine identity, PID, process start time (e.g. procfs starttime), and executable identity if available. PID alone is insufficient. Endpoint identity is normalized scheme/host/port/base path and is distinct from process identity.

Remote endpoints have no local PID/start time; use HTTP fingerprints and endpoint-scoped sessions without claiming OS-process certainty.

## Session boundaries
Create a new session when PID changes, process start time changes, engine changes, or an incompatible manual override is applied. Timeout alone does not prove replacement. Preserve last-known session as stale for a defined grace interval; close only after expiry or confirmed identity change.

## Deduplication
When endpoints resolve to the same process identity, collect process-specific telemetry once where adapter semantics allow. Preserve separate endpoint observations. Never deduplicate solely by engine name. Sample host once per cycle regardless of endpoint count.

## Diagnostics
Expose endpoint, probe status, matched signals, engine state, PID source, identity availability, manual override, last success and last error. Do not persist secrets or full request payloads.