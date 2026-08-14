# ADR-019: Linked transfer transactions instead of double-entry assumption

Date: 2026-08-15

## Status

Accepted

## Context

A cash transfer between accounts is a single business operation but must remain auditable and easy to reason about.

## Decision

Transfer is modeled as a business operation that creates two linked transaction records with the same `transfer_id`:

- TRANSFER_OUT for the source account
- TRANSFER_IN for the destination account

This is not a full double-entry accounting model. It is intentionally a practical linked-transfer design for MVP purposes.

## Consequences

- Transfer history remains auditable.
- Balance derivation remains deterministic.
- Future accounting expansion can add real double-entry layers without reinterpreting current transaction records as a full accounting system.
