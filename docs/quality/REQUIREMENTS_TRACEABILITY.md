# Requirements Traceability Matrix

| Requirement | Design reference | Test |
|---|---|---|
| Three endpoint maximum | PRD, config, architecture | AT-03, AT-15 |
| Same-port runtime switching | Process discovery, ADR-002 | AT-01, AT-02 |
| Process lifetime identity | Process discovery, data lifecycle | AT-06, AT-07 |
| Alias deduplication | Process discovery | AT-05 |
| Shared host sampling | Architecture, telemetry model, ADR-003 | AT-12 |
| PolyStrata/llama.cpp parsing | Adapter contract | Versioned fixture tests |
| Unknown fallback | Process discovery | AT-08 |
| Endpoint failure isolation | Architecture, API | AT-04, AT-13 |
| JSONL durability | ADR-004, data lifecycle | AT-10, AT-11, AT-14 |
| Null/missing semantics | Telemetry model | AT-09 |
| Local-only default | Security, ADR-005 | AT-16 |
| Browser-independent collection | Architecture, PRD | AT-10 |
| Config validation | Configuration | AT-15 |