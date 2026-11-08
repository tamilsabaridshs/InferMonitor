# Security and Privacy Design

## Posture
Local-only, read-only, least-privilege.

## Requirements
1. Bind to 127.0.0.1 by default; no 0.0.0.0 default.
2. Make read-only HTTP requests to inference endpoints.
3. Do not expose engine shutdown/load/configuration operations.
4. Do not proxy arbitrary user-supplied URLs.
5. Do not execute shell command strings derived from configuration or server responses.
6. Use fixed executable arguments; prefer procfs/sysfs for Linux inspection where practical.
7. Bound timeouts, response bytes, history query size and log growth.
8. Redact credentials from URLs and diagnostics.
9. Do not persist prompts or generated content.
10. Do not upload telemetry externally.
11. Use user-restricted data-directory permissions where supported.

## Threats
| Threat | Mitigation |
|---|---|
| Local unauthorised access | Loopback bind and OS account isolation |
| SSRF via endpoint config | Validate endpoints; no arbitrary proxy route |
| Malicious metrics payload | Size limits, strict parsers, no eval/deserialisation of executable content |
| Log injection | Structured JSON serialization and sanitised diagnostics |
| Resource exhaustion | Bounded targets, timeout, concurrency and retention |
| Sensitive prompt leakage | Aggregate metrics only |

## Privacy
History stores timestamps, endpoint IDs, process identifiers, engine metrics and host measurements. Keep process command lines minimal and avoid persisting complete command lines by default. Document history location and retention.

## Remote access
Remote binding requires a separate threat assessment, authentication, authorization, CSRF/CORS controls, transport security and documented network exposure. It is not an MVP feature.