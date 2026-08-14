# Payable aggregate

The Payable aggregate represents an obligation owed by the business to a supplier.

## Responsibility

The Payable aggregate owns:

- identity
- supplier reference
- original amount
- currency
- issue date
- due date
- creation time

It does not store the canonical payment history. Payment history lives in FinancialTransaction records.

## Derived state

The following values are derived from transaction history:

- outstanding amount
- paid amount
- partial payment status
- full paid status
- overdue status

This keeps the domain consistent and avoids stale duplicate balances.

## Invariants

- original amount must be positive
- payable currency must match the original amount currency
- due date cannot be before issued_at
- payment amount cannot exceed outstanding amount in a domain check

## Status semantics

Possible states are:

- OPEN
- PARTIALLY_PAID
- PAID
- OVERDUE

These are business interpretations of the transaction history, not stored source-of-truth state.
