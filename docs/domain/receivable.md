# Receivable aggregate

The Receivable aggregate represents an obligation owed by a customer to the business.

## Responsibility

The Receivable aggregate owns:

- identity
- customer reference
- original amount
- currency
- issue date
- due date
- creation time

It does not own the canonical financial history. The truth is stored in FinancialTransaction records.

## Derived state

The following values are derived from transaction history:

- outstanding amount
- paid amount
- partial payment status
- full paid status
- overdue status
- write-off status

This keeps the model consistent and avoids stale duplicate balances.

## Invariants

- original amount must be positive
- receivable currency must match the original amount currency
- due date cannot be before issued_at
- payment amount cannot exceed outstanding amount in a domain check
- write-off produces a historical event, not a mutable state mutation

## Status semantics

Possible states are:

- OPEN
- PARTIALLY_PAID
- PAID
- OVERDUE
- WRITTEN_OFF

These are business interpretations of the transaction history, not stored source-of-truth state.
