# ADR-004: Cordis-Inspired In-Process Plugin Kernel

**Status:** Proposed  
**Date:** 2026-11-08

## Context

InferMonitor must support multiple inference engines, operating systems, CPU/system telemetry sources and GPU vendors over time. The original requirements also require a lightweight standalone companion, minimal dependencies, graceful handling of unknown engines and unavailable metrics, and no changes to inference engines.

A simple module registry is sufficient for the first two adapters but can become ambiguous as providers gain dependencies, native resources and different availability states.

## Decision

Adopt a small **Cordis-inspired in-process plugin composition kernel**, implemented initially in Python. The kernel provides:
- service/capability registry;
- required and optional dependencies;
- deterministic startup and reverse-order shutdown;
- lifecycle and health state;
- cleanup registration;
- lifecycle/diagnostic events;
- failure isolation.

The scheduler and application services remain explicit. Plugins provide bounded capabilities; they do not own recurring polling, history, API or dashboard.

## Why this architecture

1. **Dependency inversion:** core depends on stable capabilities rather than AMD SMI, NVML, procfs or a particular engine.
2. **Independent evolution:** engine, platform and GPU providers can be added separately.
3. **Graceful degradation:** missing optional GPU libraries or individual metrics do not disable unrelated monitoring.
4. **Resource safety:** native handles and provider resources have explicit cleanup.
5. **Testability:** contracts can be tested with fake providers and platform-specific integration suites.
6. **KISS:** a small internal kernel is smaller than adopting a general ecosystem framework or distributed plugin host.

## Alternatives considered

### Direct imports and conditionals
Simple initially, but platform/vendor checks spread through application code and become difficult to test.

### Plain registry without lifecycle/dependencies
Low overhead, but cleanup, activation order and partial availability become ad hoc.

### Full Cordis framework
Provides a richer plugin model, but introduces framework/language/runtime decisions not justified by the current Python, single-process, local-only requirements. Reconsider if a genuine third-party plugin ecosystem or advanced dynamic lifecycle becomes necessary.

### Separate processes per provider
Improves isolation but adds IPC, deployment and operational complexity. Not justified for trusted built-in providers in MVP.

## Consequences

**Positive**
- Stable extension points and independent providers.
- No requirement to redesign the collector for each GPU vendor/OS.
- Provider failures are contained and diagnosable.

**Negative**
- Additional contracts, lifecycle states and tests.
- In-process native-library crashes cannot be fully isolated by Python exception handling.
- Plugin compatibility/versioning needs discipline.

## Constraints

- Built-in allow-listed plugins only initially.
- No arbitrary dynamic loading, hot reload or external plugin marketplace.
- No provider-owned polling loops.
- No provider writes directly to JSONL or API.
- Optional dependencies remain optional.
- All metrics retain provenance and availability.

## Revisit triggers

Reconsider an external framework or out-of-process providers only when third-party plugin distribution, hot reload, crash isolation or independently versioned plugin deployment becomes a demonstrated requirement.
