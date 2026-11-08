# Scope, Use Cases and Constraints

## Product boundary
InferMonitor observes inference servers; it does not manage them.

```text
PolyStrata ----\
llama.cpp ------> InferMonitor companion ---> Browser dashboard
Other endpoint-/         |                  ---> JSONL history
                          +--> shared host sampler
```

## MVP scope
- Linux local endpoint probing and process discovery.
- HTTP engine fingerprinting.
- PolyStrata and llama.cpp adapters.
- Up to three enabled endpoint configurations.
- Shared host telemetry sampling.
- Live dashboard and local JSON API.
- JSONL history, process sessions, retention and diagnostics.

## Non-goals
No server start/stop, runtime configuration, model downloads, inference scheduling, request proxy, benchmark orchestration, distributed discovery, remote telemetry upload or alert subsystem.

## Use cases
| ID | Actor | Use case | Result |
|---|---|---|---|
| UC-01 | Operator | Monitor server on 8080 | Active engine and metrics shown |
| UC-02 | Operator | Replace runtime on same port | New session; no mixed history |
| UC-03 | Operator | Monitor three separate ports | Three independent cards |
| UC-04 | Operator | Configure aliases to same process | Duplicate process collection avoided |
| UC-05 | Operator | Monitor unknown service | Safe Unknown state |
| UC-06 | Operator | Close browser | Background collection continues |
| UC-07 | Operator | Restart companion | Valid history remains readable |
| UC-08 | Operator | Disable one endpoint | Others continue |
| UC-09 | Operator | Manual adapter override | Override visibly labelled |

## Constraints
- Maximum three enabled endpoints in initial release.
- Initial polling interval proposal: 1000 ms, configurable.
- Companion default bind: 127.0.0.1:8090.
- Inference endpoints configurable; 127.0.0.1:8080 is a common default.
- Linux first; hardware telemetry is provider-dependent.