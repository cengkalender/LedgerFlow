# ADR-021: Payment is a transaction type

Date: 2026-08-15

## Status

Accepted

## Context

A payment is not a separate mutable business record in the core domain. It is a special financial event that settles an obligation.

## Decision

Payment is represented as a FinancialTransaction with type `PAYMENT` and an optional `receivable_id` or `payable_id` reference.

## Consequences

- No duplicate payment state is stored separately.
- Report generation and settlement logic remain based on transaction history.
- Domain logic stays smaller and easier to reason about.
