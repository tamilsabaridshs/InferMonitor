# InferMonitor

A lightweight local monitoring companion for self-hosted inference servers. It observes up to three endpoints, identifies the process and engine serving each endpoint, collects engine telemetry, and correlates it with shared host hardware telemetry. Initial engines: PolyStrata and llama.cpp.

**Status:** Documentation baseline only; implementation has not started. The repository initially contained only the MIT license.

## Documentation
- [BRD](docs/requirements/BRD.md) | [PRD](docs/requirements/PRD.md) | [Scope](docs/requirements/SCOPE.md)
- [System architecture](docs/architecture/SYSTEM_ARCHITECTURE.md) | [Component design](docs/architecture/COMPONENT_DESIGN.md)
- [Process discovery](docs/design/PROCESS_DISCOVERY.md) | [Telemetry model](docs/design/TELEMETRY_MODEL.md) | [Adapter contract](docs/design/ENGINE_ADAPTER_CONTRACT.md) | [Data lifecycle](docs/design/DATA_LIFECYCLE.md)
- [API](docs/api/API_SPECIFICATION.md) | [Configuration](docs/operations/CONFIGURATION.md) | [Security](docs/operations/SECURITY.md)
- [Test strategy](docs/quality/TEST_STRATEGY.md) | [Traceability](docs/quality/REQUIREMENTS_TRACEABILITY.md) | [Roadmap](docs/management/ROADMAP.md) | [ADRs](docs/decisions/README.md)

## Principles
KISS, DRY and POLA. Reuse existing HTTP endpoints and OS facilities. One local companion process, a simple browser UI and JSONL history initially. No mandatory database, broker, container platform or heavyweight framework. Linux-first; AMD ROCm is the initial hardware reference. InferMonitor does not manage or modify inference servers, proxy inference requests, or upload telemetry. See [LICENSE](LICENSE).