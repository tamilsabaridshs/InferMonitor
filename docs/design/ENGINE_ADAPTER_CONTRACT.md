# Engine Adapter Contract

## Purpose
Translate engine-specific telemetry into canonical metric DTOs. Adapters do not own polling schedules, host sampling, persistence or UI.

## Illustrative interface
```python
class EngineAdapter:
    engine_id: str

    def fingerprint(self, probe_evidence):
        """Return match/no-match/ambiguous plus supporting evidence."""

    def collect(self, endpoint, http_client):
        """Return normalised engine telemetry and source provenance."""

    def health(self, endpoint, http_client):
        """Return engine health separately from TCP reachability."""
```
Conceptual contract; implementation details may vary.

## Rules
- No independent polling loop inside an adapter.
- No host GPU/CPU collection in engine adapters.
- Preserve original metric names, units and labels in provenance.
- Validate numeric types and reject NaN/Infinity.
- Bound response sizes and timeouts.
- Distinguish unreachable, HTTP error, unsupported endpoint, parse error and missing metric.
- Do not collect prompts/completions.
- Fixture-test each declared supported engine version family.

## Initial adapters
**PolyStrata:** use supported health/properties/metrics interfaces; confirm exact response schema and metric semantics against target releases.

**llama.cpp:** use metrics exposition when enabled; optional metadata endpoints only when available. Confirm names/labels against tested builds.

## Compatibility
Record observed engine version if available. Unknown future fields should not break parsing. Missing required fingerprint evidence downgrades detection rather than inviting a guess.