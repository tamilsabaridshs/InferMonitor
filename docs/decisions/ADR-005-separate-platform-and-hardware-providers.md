# ADR-005: Separate Platform Providers from GPU Vendor Providers

**Status:** Proposed  
**Date:** 2026-11-08

## Context

The future target includes multiple operating systems and GPU architectures. An OS may host multiple GPU vendors; one GPU vendor may support multiple OS/runtime combinations. Combining OS process discovery and GPU telemetry in a single provider would multiply implementations and create invalid assumptions (for example, Linux procfs being required for AMD GPU telemetry).

## Decision

Separate:
1. **Platform providers:** host identity, process discovery, CPU/RAM/disk and OS-specific facilities.
2. **GPU providers:** device inventory and vendor-specific device telemetry.
3. **Engine adapters:** inference endpoint detection and engine-reported metrics.

Compose them through canonical contracts and the plugin kernel.

## Rationale

- Avoid a Cartesian product of OS × GPU vendor × inference engine implementations.
- Allow AMD GPU monitoring to coexist with Linux or Windows process providers where supported.
- Allow a host with multiple GPU vendors.
- Make missing vendor tooling independent of host process monitoring.
- Keep physical hardware metrics separate from engine-internal cache/allocation metrics.

## Consequences

- Device identity and metric provenance become first-class.
- Compatibility must be validated for each actual OS/driver/runtime/device combination.
- Some metrics remain unavailable on some combinations; no universal parity is promised.
- A device may be discovered while some telemetry capabilities remain unavailable.

## Alternatives rejected

- One provider per OS/vendor combination: duplication and combinatorial growth.
- One universal GPU API pretending all metrics are equivalent: hides real semantic differences.
- Infer GPU vendor/runtime from OS or engine: unreliable.

## Acceptance

- Linux platform provider can run with AMD, NVIDIA, Intel or no supported GPU provider.
- GPU provider does not depend on process discovery.
- Engine adapters do not collect physical GPU telemetry.
- Core does not branch on vendor/OS names to interpret routine metrics.
