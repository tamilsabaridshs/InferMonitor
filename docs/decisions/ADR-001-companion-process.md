# ADR-001: Companion Process

**Status:** Proposed | **Date:** 2026-11-08

## Context
Observe independent runtimes, support three endpoints, continue sampling without a browser tab, and avoid modifying either engine.

## Options
Modify each runtime; build a separate monitor per runtime; or build an independent local companion with adapters.

## Decision
Choose an independent companion. One local process owns discovery, collection, snapshot publication, API, UI serving and history.

## Consequences
Engines remain independently deployable. Adapters isolate differences. One collector avoids duplicate polls from multiple browser clients. The companion is an additional process. A modular monolith is sufficient.

## Revisit
When remote multi-host monitoring or independently scalable collectors become a real requirement.