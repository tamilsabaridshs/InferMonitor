# ADR-003: Telemetry Scopes and Shared Host Sampling

**Status:** Proposed | **Date:** 2026-11-08

## Context
GPU/CPU/RAM readings describe host resources, not separate resources per endpoint. Repeating host collection per endpoint is wasteful and can mislead.

## Decision
Sample host telemetry once per collector cycle. Collect engine metrics per endpoint/process adapter context. Link observations to host sample ID. Keep physical GPU memory separate from potentially overlapping engine caches/allocations.

## Consequences
The dashboard has one host panel and separate endpoint cards. Memory totals are not summed unless sources guarantee non-overlap.

## Revisit
When multi-host or per-device sampling is introduced; maintain once-per-physical-host/device-per-cycle semantics.