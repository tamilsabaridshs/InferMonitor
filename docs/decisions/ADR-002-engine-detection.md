# ADR-002: Engine Detection and Process Identity

**Status:** Proposed | **Date:** 2026-11-08

## Context
The same port (commonly 8080) can serve different engines at different times. Port-only assumptions misattribute metrics. PIDs can be reused.

## Decision
Use validated HTTP fingerprints as primary evidence, corroborate with local socket/PID/executable evidence, and identify local processes with PID plus process start time. A replacement creates a new session. Ambiguous evidence means Unknown. Manual override is explicit and visible.

## Consequences
Same-port reuse is handled. Process inspection may be unavailable for remote endpoints. Fingerprints require versioned fixture maintenance. A transient timeout is not proof of process replacement.

## Revisit
When supported runtimes add stable identification endpoints or evidence shows signatures are insufficient.