# Financial transaction core

FinancialTransaction is the canonical historical fact of LedgerFlow.

## Why it is canonical

The system stores financial history as immutable transaction records rather than mutable balance fields. This prevents drift and makes reversal, audit, and reporting trustworthy.

## Core rule

Every monetary movement is represented as a FinancialTransaction.

Examples:

- INCOME
- EXPENSE
- CREDIT
- PAYMENT
- TRANSFER_OUT
- TRANSFER_IN
- ADJUSTMENT
- WRITE_OFF
- REVERSAL

## Linked transfer transactions

Transfers are not treated as a double-entry accounting abstraction in the MVP domain model. Instead, a single business transfer creates two linked transaction records with the same `transfer_id`:

- TRANSFER_OUT for the source account
- TRANSFER_IN for the destination account

This keeps the domain model simpler while still preserving auditability and balance derivation.

## Reversal rule

Historical records are never deleted or mutated. If a transaction is incorrect, a new REVERSAL transaction is created with `related_transaction_id` referencing the original transaction.

## Payment rule

Payment is a FinancialTransaction type, not a separate stack of mutable payment state fields.

## Outstanding values

Outstanding balances for receivables and payables are derived from transaction history and are not stored as canonical state.

## Balance rule

Account balance is derived from the set of relevant transactions. Account does not store a mutable balance field.
