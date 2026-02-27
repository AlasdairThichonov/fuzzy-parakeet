# ADR 0002: LLM safety with explicit opt-in

## Status
Accepted

## Context
Security requirement: do not leak secrets and avoid external calls by default.

## Decision
- LLM is disable-able via `--no-llm`.
- Default provider is `dummy`.
- Sensitive patterns are redacted before LLM calls.
- Reports include redaction metadata and replacement count.

## Consequences
+ Aligns with secure CI baseline.
+ Reduces secret leakage risk.
- Regex-based redaction can produce false positives/negatives and should be improved over time.
