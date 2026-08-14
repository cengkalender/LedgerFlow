"""Immutable financial transaction model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ledgerflow.domain.shared.clock import SystemClock
from ledgerflow.domain.shared.currency import Currency
from ledgerflow.domain.shared.exceptions import DomainError, ValidationError
from ledgerflow.domain.shared.identifiers import Identifier
from ledgerflow.domain.shared.money import Money

from .transaction_type import TransactionType


@dataclass(frozen=True, slots=True)
class FinancialTransaction:
    """Immutable record representing a financial event."""

    id: Identifier
    type: TransactionType
    amount: Money
    account_id: Identifier | None = None
    receivable_id: Identifier | None = None
    payable_id: Identifier | None = None
    transfer_id: Identifier | None = None
    related_transaction_id: Identifier | None = None
    description: str = ""
    occurred_at: datetime = field(default_factory=lambda: SystemClock().now())
    created_at: datetime = field(default_factory=lambda: SystemClock().now())
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._validate_amount()
        self._validate_transaction_type_consistency()
        self._validate_description()

    def _validate_amount(self) -> None:
        if not isinstance(self.amount, Money):
            raise ValidationError("Transaction amount must be a Money value object")
        if self.amount.is_zero():
            raise ValidationError("Transaction amount cannot be zero")

    def _validate_description(self) -> None:
        if self.description is None:
            raise ValidationError("Transaction description cannot be null")
        if not isinstance(self.description, str):
            raise ValidationError("Transaction description must be a string")
        object.__setattr__(self, "description", self.description.strip())

    def _validate_transaction_type_consistency(self) -> None:
        if not isinstance(self.type, TransactionType):
            raise ValidationError("Transaction type must be a valid TransactionType")

        required_account = {
            TransactionType.INCOME,
            TransactionType.EXPENSE,
            TransactionType.TRANSFER_OUT,
            TransactionType.TRANSFER_IN,
            TransactionType.ADJUSTMENT,
        }

        if self.type in required_account and self.account_id is None:
            raise ValidationError(f"{self.type.value} transaction requires an account_id")

        if self.type in {TransactionType.CREDIT, TransactionType.PAYMENT, TransactionType.WRITE_OFF, TransactionType.REVERSAL}:
            if self.account_id is None and self.receivable_id is None and self.payable_id is None:
                raise ValidationError(
                    f"{self.type.value} transaction requires at least one related account, receivable, or payable"
                )

        if self.type == TransactionType.CREDIT and self.receivable_id is None:
            raise ValidationError("CREDIT transactions require a receivable_id")

        if self.type == TransactionType.PAYMENT and not (self.receivable_id or self.payable_id):
            raise ValidationError("PAYMENT transactions require a receivable_id or payable_id")

        if self.type in {TransactionType.TRANSFER_OUT, TransactionType.TRANSFER_IN}:
            if self.transfer_id is None:
                raise ValidationError(f"{self.type.value} transaction requires a transfer_id")

        if self.type == TransactionType.REVERSAL and self.related_transaction_id is None:
            raise ValidationError("REVERSAL transactions require related_transaction_id")

    @classmethod
    def create(
        cls,
        *,
        transaction_type: TransactionType,
        amount: Money,
        account_id: Identifier | None = None,
        receivable_id: Identifier | None = None,
        payable_id: Identifier | None = None,
        transfer_id: Identifier | None = None,
        related_transaction_id: Identifier | None = None,
        description: str = "",
        occurred_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
        transaction_id: Identifier | None = None,
    ) -> "FinancialTransaction":
        if occurred_at is None:
            occurred_at = SystemClock().now()

        if metadata is None:
            metadata = {}

        return cls(
            id=transaction_id or Identifier.generate(),
            type=transaction_type,
            amount=amount,
            account_id=account_id,
            receivable_id=receivable_id,
            payable_id=payable_id,
            transfer_id=transfer_id,
            related_transaction_id=related_transaction_id,
            description=description,
            occurred_at=occurred_at,
            created_at=SystemClock().now(),
            metadata=metadata,
        )

    def is_reversal_of(self, other: "FinancialTransaction") -> bool:
        return self.related_transaction_id == other.id

    def signature(self) -> str:
        return f"{self.type.value}:{self.amount.amount}:{self.amount.currency.code}"

    def is_linked_transfer(self) -> bool:
        return self.type in {TransactionType.TRANSFER_OUT, TransactionType.TRANSFER_IN} and self.transfer_id is not None

    def is_positive(self) -> bool:
        return self.amount.is_positive()

    def amount_for_balance(self) -> int:
        if self.type in {TransactionType.EXPENSE, TransactionType.TRANSFER_OUT, TransactionType.PAYMENT, TransactionType.WRITE_OFF, TransactionType.REVERSAL}:
            return -self.amount.amount
        return self.amount.amount

    def is_currency(self, currency: Currency) -> bool:
        return self.amount.currency == currency
