# Account aggregate

The Account aggregate represents a money-holding location inside the business.

## Responsibility

The account owns:

- identity
- name
- account type
- currency
- lifecycle status
- creation time

It does not own balances. The balance is derived from ledger transaction history rather than stored as independent mutable state.

## Types

Supported account types:

- CASH
- BANK
- OTHER

## Lifecycle

The account status is:

- ACTIVE
- ARCHIVED

An archived account cannot be used as a transfer source or destination.

## Transfer rule

Transfer operations depend on account activity and currency compatibility. The account aggregate only provides eligibility checks, not the full transfer execution.

## Why no balance field?

Balance is a derived value. Duplicate mutable balance fields are a source of drift and historical inconsistency.

This keeps the domain aligned with the ledger-as-source-of-truth rule.
