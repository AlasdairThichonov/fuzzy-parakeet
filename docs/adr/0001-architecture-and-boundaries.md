# ADR 0001: Clean-ish package architecture

## Status
Accepted

## Context
We need an extensible architecture for scanners, rules, reporting, and LLM integration.

## Decision
The project is split into focused packages:
- `scanners`: input loading (k8s/helm/tf)
- `rules`: policy and risk engine
- `reporting`: JSON/Markdown outputs
- `llm`: providers and redaction
- `cli` / `service`: orchestration layer

## Consequences
+ Easier module-level testing.
+ Clear responsibility boundaries.
- Internal contracts must be kept stable as the codebase evolves.
