# ADR-022: Derive outstanding from ledger history

Date: 2026-08-15

## Status

Accepted

## Context

If outstanding values are stored as mutable state, they will drift from historical payment records and create inconsistent business data.

## Decision

Outstanding values for receivables and payables are derived from FinancialTransaction history rather than stored as canonical state.

## Consequences

- Payment history is the single source of truth.
- Future reconciliation remains safer.
- The domain avoids hidden drift between state and facts.
