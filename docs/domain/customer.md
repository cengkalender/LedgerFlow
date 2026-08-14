# Customer aggregate

The Customer aggregate is the core identity and credit relationship boundary in LedgerFlow.

## Responsibility

The Customer aggregate owns:

- identity
- customer name
- contact information
- lifecycle status
- credit limit
- creation time

It does not own receivable balances, payment history, ledger entries, or account balances. Those belong to their own contexts.

## Status lifecycle

Customer states are:

- ACTIVE
- BLOCKED
- ARCHIVED

Transitions:

- ACTIVE -> BLOCKED
- BLOCKED -> ACTIVE
- ACTIVE -> ARCHIVED
- BLOCKED -> ARCHIVED
- ARCHIVED -> ACTIVE is rejected
- ARCHIVED -> BLOCKED is rejected

## Credit rules

A customer may receive credit only when status is ACTIVE.

The customer's `credit_limit` is a Money value object, explicit in currency and kept in minor units.

Negative limits are rejected.

## Why not store outstanding balance here?

Outstanding receivable balance is derived from receivable and ledger activity. Keeping a separate mutable outstanding value on Customer would duplicate the same truth and create drift.

This aggregate only knows its own eligibility and limit, not the total receivable state of the business.
