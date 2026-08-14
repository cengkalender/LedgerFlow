# ADR-018: FinancialTransaction as source of truth

Date: 2026-08-15

## Status

Accepted

## Context

LedgerFlow needs an immutable and auditable financial record model. Mutable balance fields on Account, Receivable, and Payable would drift over time and create inconsistent historical data.

## Decision

We will treat FinancialTransaction as the canonical source of truth for all financial history.

## Consequences

- Historical facts are immutable.
- Reversal and adjustment are explicit operations.
- Reporting and balances are derived from transactions.
- Outstanding values are derived, not stored.
- The system remains auditable and testable.
