# InferMonitor

A lightweight local monitoring companion for self-hosted inference servers. It observes up to three endpoints, identifies the process and engine serving each endpoint, collects engine telemetry, and correlates it with shared host hardware telemetry. Initial engines: PolyStrata and llama.cpp.

**Status:** Documentation baseline only; implementation has not started.

## Documentation
- [BRD](docs/requirements/BRD.md) | [PRD](docs/requirements/PRD.md) | [Scope](docs/requirements/SCOPE.md)
- [System architecture](docs/architecture/SYSTEM_ARCHITECTURE.md) | [Component design](docs/architecture/COMPONENT_DESIGN.md) | [Plugin architecture](docs/architecture/PLUGIN_ARCHITECTURE.md)
- [Process discovery](docs/design/PROCESS_DISCOVERY.md) | [Platform provider contract](docs/design/PLATFORM_PROVIDER_CONTRACT.md) | [GPU provider contract](docs/design/GPU_PROVIDER_CONTRACT.md)
- [Telemetry model](docs/design/TELEMETRY_MODEL.md) | [Engine adapter contract](docs/design/ENGINE_ADAPTER_CONTRACT.md) | [Data lifecycle](docs/design/DATA_LIFECYCLE.md)
- [API](docs/api/API_SPECIFICATION.md) | [Configuration](docs/operations/CONFIGURATION.md) | [Security](docs/operations/SECURITY.md)
- [Test strategy](docs/quality/TEST_STRATEGY.md) | [Traceability](docs/quality/REQUIREMENTS_TRACEABILITY.md) | [Roadmap](docs/management/ROADMAP.md) | [ADRs](docs/decisions/README.md)

## Architectural direction
InferMonitor is a modular monolith with a small Cordis-inspired in-process composition kernel. Engine adapters, OS/platform providers and GPU-vendor providers are independent extension dimensions. Core services depend on capabilities and canonical telemetry contracts, not vendor libraries or OS APIs.

The plugin kernel provides explicit registration, dependency validation, lifecycle, health and cleanup. The application scheduler owns polling cadence; plugins do not create recurring loops. Initial plugins are built-in and allow-listed. No arbitrary dynamic loading, hot reload, distributed plugin host or mandatory framework is planned.

## Principles
KISS, DRY and POLA. Reuse existing engine HTTP endpoints, OS facilities and vendor-supported telemetry APIs. One local companion process, a simple browser UI and JSONL history initially. No mandatory database, broker, container platform or heavyweight framework. Linux-first; AMD GPU telemetry is the initial hardware reference. InferMonitor does not manage or modify inference servers, proxy inference requests, collect prompts/completions or upload telemetry.

**Status note:** All documents describe proposed architecture and requirements. No implementation or provider compatibility is implied until contract and integration tests pass for a declared OS/device/driver/runtime combination.
