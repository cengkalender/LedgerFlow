"""Transaction type definitions for immutable financial records."""

from __future__ import annotations

from enum import Enum


class TransactionType(str, Enum):
    """Canonical financial event types."""

    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    CREDIT = "CREDIT"
    PAYMENT = "PAYMENT"
    TRANSFER_OUT = "TRANSFER_OUT"
    TRANSFER_IN = "TRANSFER_IN"
    ADJUSTMENT = "ADJUSTMENT"
    WRITE_OFF = "WRITE_OFF"
    REVERSAL = "REVERSAL"
