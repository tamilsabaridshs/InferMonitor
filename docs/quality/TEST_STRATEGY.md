# Test Strategy and Acceptance Criteria

## Test layers
- Unit: endpoint normalization, fingerprints, sessions, metric parsing, null/unit semantics.
- Contract: version-labelled payload fixtures from actual runtimes.
- Integration: local test servers reproducing supported engine endpoints.
- System: collector, API/UI, JSONL persistence/recovery.
- Performance: sampling cost with one, two and three targets.
- Resilience: timeouts, malformed payloads, process restart, unknown engine.

## Acceptance scenarios
| ID | Scenario | Expected result |
|---|---|---|
| AT-01 | PolyStrata on 8080 | Detected only when validated signature matches |
| AT-02 | Replace PolyStrata with llama.cpp on 8080 | New engine/session; no mixed history |
| AT-03 | Three supported servers on separate ports | All independently visible |
| AT-04 | One target times out | Other targets continue |
| AT-05 | Two endpoint aliases resolve to same process | Process collection deduplicated where valid |
| AT-06 | PID same, process start time changes | New session |
| AT-07 | PID changes | New session |
| AT-08 | Unknown HTTP 200 service | Unknown, not guessed |
| AT-09 | Metric absent | Null with reason, not zero |
| AT-10 | Browser closed | Collector/history continue |
| AT-11 | Companion restarted | History recovered; server identity reconfirmed |
| AT-12 | Three targets in one cycle | Exactly one host sample |
| AT-13 | Malformed exposition | Adapter error isolated |
| AT-14 | Partial trailing JSONL record | Prior valid records readable |
| AT-15 | More than three enabled endpoints | Configuration rejected |
| AT-16 | Remote bind attempt | Not enabled by default; requires future security design |

## Fixture policy
Capture payloads from actual supported engine versions, remove sensitive fields, and annotate version, path, flags and capture date. Do not invent fixture metric names.

## Metric correctness
Test types/finite values, units, counter/gauge distinction, escaped Prometheus labels, monotonic counter rates, missing/stale values, source timestamps, session IDs and non-additive memory accounting.

## Performance
Compare baseline without monitoring against one/two/three endpoints at the proposed 1-second interval. Record cycle duration, missed/overlapping cycles, CPU/RAM overhead, HTTP latency and host sampler cost. Set budgets after reference-machine measurements.

## Release gate
Do not claim an engine adapter is supported until fixture and integration tests pass against a recorded runtime version.