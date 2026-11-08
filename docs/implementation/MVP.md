# MVP implementation notes

## Target profile
Native Ubuntu 26.04.1 on Ryzen 7 9700X and Radeon RX 9070 16 GB (gfx1201), ROCm/HIP. This is the intended test matrix, not a claim that this GitHub editing environment ran on that PC.

## Current implementation
- Python 3.11+ standard-library companion, in-process allow-listed plugin registry.
- Linux procfs CPU/RAM/disk throughput, local TCP listener-to-process lookup, PID plus process start time.
- AMD SMI integration: runs amd-smi metric --json and amd-smi list --json; maps fields only when their source name/unit is recognised; retains unknown values with source names.
- PolyStrata JSON health/metrics adapter: /health, /props, /metrics, optional /metrics/prometheus.
- llama.cpp Prometheus /metrics adapter.
- Up to three local endpoints, same-port process/engine sessions, JSONL persistence and local dashboard/API.

## Compatibility and evidence boundaries
- The user's supplied Strata notes report /health, /props, /metrics and /metrics/prometheus, plus fields such as engine.version, max_context, expert_cache_mib, arena_mib, vram_free_mib, request decode_tok_s, prompt_read, prompt_ms, hit_rate, pcie_share and drafts counters. The adapter retains numeric leaves with original dotted paths; units and semantics are not guessed.
- llama.cpp metrics are parsed from the Prometheus exposition. Source names, labels and numeric values remain intact; the adapter does not calculate counter rates or claim slot/context metrics without a fixture.
- AMD SMI JSON schema differs across ROCm releases. The provider reads AMD SMI field values and explicit units when present; unrecognised fields remain source-labelled. Validate on the installed ROCm 7.16/HIP setup.
- Process-to-socket ownership may require permissions. If PID/start time cannot be established, identity is not considered strong.
- JSONL retention pruning occurs at startup; automatic online rotation and crash-safe compaction are follow-up work.

## Security
Loopback API and inference URLs only; no URL credentials; bounded read-only GET requests; no prompts/completions, remote telemetry, inference control, or arbitrary plugin loading.

## Test gate
Run python -m unittest discover -s tests -v, then verify real integrations on Ubuntu 26.04.1/kernel 7.0.0-38, ROCm 7.16/HIP, RX 9070 gfx1201, the currently installed PolyStrata build and the user's llama.cpp build. Do not declare supported until these tests pass.
