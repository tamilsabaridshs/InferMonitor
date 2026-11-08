# Plugin Architecture and Composition Kernel

**Status:** Proposed architecture baseline  
**Applies to:** InferMonitor companion process  
**Related requirements:** REQ-ARCH-01..08, REQ-PLUG-01..10, REQ-SEC-01..08  
**Related decisions:** ADR-004, ADR-005

## 1. Purpose

Define a small, in-process, Cordis-inspired composition kernel so InferMonitor can add inference engines, operating systems, system telemetry sources and GPU vendors without coupling the core to a particular implementation.

This is a design pattern, not a commitment to adopt the Cordis package or reproduce its complete feature set. The first implementation remains a lightweight Python modular monolith.

## 2. Requirements

| ID | Requirement | Reason |
|---|---|---|
| REQ-PLUG-01 | Plugins register capabilities through stable contracts. | Core must depend on what a component does, not its vendor or OS. |
| REQ-PLUG-02 | Plugins declare required and optional services. | Missing optional integrations must not prevent startup. |
| REQ-PLUG-03 | Plugins have explicit start, health and stop lifecycle. | Native handles, subprocesses and library resources need deterministic cleanup. |
| REQ-PLUG-04 | A plugin failure is isolated from unrelated plugins and endpoints. | One unavailable driver must not stop engine or CPU monitoring. |
| REQ-PLUG-05 | Plugin registration is deterministic and duplicate IDs are rejected. | Avoid ambiguous provider selection. |
| REQ-PLUG-06 | The core owns scheduling and collection cycles. | Prevent provider-specific polling loops and duplicate sampling. |
| REQ-PLUG-07 | Plugins do not own persistence, dashboard or API concerns. | Preserve separation of concerns and replaceability. |
| REQ-PLUG-08 | Plugin activation is explicit and allow-listed in the initial release. | Avoid arbitrary code execution from discovered packages. |
| REQ-PLUG-09 | Plugin diagnostics expose identity, version, state and failure reason. | Make driver/API incompatibility diagnosable. |
| REQ-PLUG-10 | Plugin cleanup is attempted even if another cleanup action fails. | Prevent resource leaks during shutdown. |

## 3. Architecture decision

Use a **small internal plugin kernel** with:
- a service registry;
- capability registration;
- explicit dependency declarations;
- deterministic startup ordering;
- lifecycle states;
- event publication for lifecycle/diagnostic notifications;
- reverse-order cleanup;
- health and diagnostic reporting.

Do not initially implement:
- arbitrary third-party runtime code loading;
- hot reload or hot replacement;
- distributed plugins or RPC;
- plugin marketplaces or package installation;
- general-purpose nested plugin trees;
- an unrestricted event bus for all application communication.

The application scheduler directly invokes typed provider contracts. Events are for lifecycle and state notifications, not a replacement for ordinary method calls.

## 4. Core concepts

### Plugin
A named implementation unit with a stable ID, version, declared dependencies, provided services/capabilities and lifecycle.

### Service
An in-process object registered under a stable service key and implementing a documented contract. Service keys must be namespaced, for example `platform.process_discovery`, `system.host_telemetry`, `gpu.telemetry`, and `engine.polystrata`.

### Capability
A declared function the implementation can perform, such as `process.listener_lookup`, `gpu.memory`, `gpu.temperature`, or `engine.metrics`. Capabilities are not assumed merely because a provider implements a broad interface.

### Provider
An implementation of a capability for a specific platform/runtime/vendor combination.

## 5. Lifecycle

Recommended states:

```text
DISCOVERED -> VALIDATING -> STARTING -> ACTIVE
                  |            |
                  v            v
                FAILED <---- DEGRADED
                  |
                  v
               STOPPING -> STOPPED
```

- **DISCOVERED:** declared by built-in configuration.
- **VALIDATING:** contract/version/dependency checks.
- **STARTING:** acquire handles and initialise libraries.
- **ACTIVE:** all required startup checks passed.
- **DEGRADED:** provider is usable but one or more optional capabilities are unavailable.
- **FAILED:** cannot provide its required capabilities.
- **STOPPING/STOPPED:** cleanup in progress/completed.

A provider with a missing optional metric should be DEGRADED, not FAILED. A provider with a missing required dependency cannot become ACTIVE.

## 6. Dependency and registration rules

1. Each plugin has a unique stable ID.
2. Each service key has one owner unless the contract explicitly supports multiple providers.
3. Multi-provider capabilities (for example multiple GPU devices/providers) register as collections with stable provider IDs.
4. Required dependencies are resolved before start.
5. Optional dependencies are exposed as absent capabilities, not fake no-op implementations.
6. Circular dependencies are rejected during validation.
7. Startup order follows the dependency graph; shutdown is reverse order.
8. Plugin code cannot mutate core configuration or persistence directly.

Provider selection is explicit and deterministic. If multiple providers can report the same device, the device inventory records the source and selection policy; the collector must not silently double-count it.

## 7. Scheduling and concurrency

The application scheduler owns cadence, timeout, concurrency and cancellation. A provider exposes bounded collection operations and must not create an independent recurring loop.

- Host-wide CPU/RAM/disk sampling occurs once per cycle.
- Physical GPU devices are sampled once per cycle per selected provider/device combination.
- Engine telemetry is collected per unique engine/process context, deduplicated using process identity where valid.
- Endpoint observations reference the shared host sample ID.
- A slow or failed provider is bounded by a timeout and cannot block unrelated collection indefinitely.
- No unbounded thread/task creation.

The initial implementation may use a sequential loop or a small bounded worker pool. Choose based on measured cycle duration, not speculation.

## 8. Error model

Distinguish:
- unsupported capability;
- dependency unavailable;
- permission denied;
- temporary provider failure;
- timeout;
- malformed provider response;
- device disappeared;
- provider initialization failure.

Return structured provider results and diagnostics. Do not convert errors or absent values to numeric zero.

## 9. Security and trust

Initial plugins are built-in, reviewed code enabled by application configuration. Do not import arbitrary modules based on a user-provided path or a remote manifest. Do not execute shell commands from plugin metadata, telemetry payloads or configuration. Native vendor libraries are optional dependencies and must fail closed to an unavailable capability.

## 10. Illustrative Python contracts

Conceptual only; exact implementation may use dataclasses and typed result objects.

```python
from typing import Protocol

class Plugin(Protocol):
    plugin_id: str
    version: str
    requires: tuple[str, ...]
    optional: tuple[str, ...]

    def start(self, context) -> None: ...
    def health(self) -> dict: ...
    def stop(self) -> None: ...

class CapabilityProvider(Protocol):
    provider_id: str
    def capabilities(self) -> set[str]: ...
```

A plugin registers services during controlled startup. The registry validates ownership and dependencies before exposing them to application services.

## 11. Consequences and trade-offs

**Benefits:** vendor/OS isolation, graceful degradation, explicit lifecycle, testable contracts, controlled dependency growth.

**Costs:** additional contracts and lifecycle code; more design discipline; provider compatibility must be tested against real platforms.

**Why not full Cordis:** InferMonitor is a single-process monitoring companion, not a general bot/plugin ecosystem. A full framework would add abstraction and dependency surface beyond current requirements. Revisit only if real plugin ecosystem needs emerge.

## 12. Acceptance criteria

- Duplicate plugin IDs and conflicting exclusive service registrations are rejected.
- Required missing dependency prevents only the dependent plugin from activating.
- Optional missing dependency produces DEGRADED state.
- One provider failure does not stop other providers or endpoint collection.
- Start order respects dependencies; stop order is reversed.
- Cleanup is attempted for every registered disposer, even after one fails.
- Scheduler, not providers, controls poll cadence.
- No plugin can persist prompts/completions or send telemetry externally.
- Plugin state and capability availability are visible through diagnostics.
