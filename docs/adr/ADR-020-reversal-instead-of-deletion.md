# ADR-020: Reversal instead of deletion or mutation

Date: 2026-08-15

## Status

Accepted

## Context

Financial events are historical facts. Deleting or mutating them would erase auditability and create a misleading report.

## Decision

Corrections are represented as explicit reversal transactions that point to the original transaction via `related_transaction_id`.

## Consequences

- Historical record integrity is preserved.
- Future auditing remains possible.
- Net balances remain correct without destroying original facts.
