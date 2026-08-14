"""Payable aggregate for supplier obligations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from .ledger.financial_transaction import FinancialTransaction
from .ledger.transaction_type import TransactionType
from .shared.clock import SystemClock
from .shared.currency import Currency
from .shared.exceptions import ValidationError
from .shared.identifiers import Identifier
from .shared.money import Money


class PayableStatus(str, Enum):
    OPEN = "OPEN"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    OVERDUE = "OVERDUE"


@dataclass(slots=True)
class Payable:
    """Supplier payable obligation with history-derived settlement state."""

    id: Identifier
    supplier_id: Identifier
    original_amount: Money
    currency: Currency
    issued_at: datetime
    due_date: datetime
    created_at: datetime = field(default_factory=lambda: SystemClock().now())

    def __post_init__(self) -> None:
        self._validate_amount()
        self._validate_currency()
        self._validate_dates()

    @classmethod
    def create(
        cls,
        *,
        supplier_id: Identifier,
        original_amount: Money,
        due_date: datetime,
        payable_id: Identifier | None = None,
        issued_at: datetime | None = None,
        created_at: datetime | None = None,
    ) -> "Payable":
        if original_amount.is_zero() or not original_amount.is_positive():
            raise ValidationError("Payable amount must be positive")

        if issued_at is None:
            issued_at = SystemClock().now()

        if created_at is None:
            created_at = SystemClock().now()

        return cls(
            id=payable_id or Identifier.generate(),
            supplier_id=supplier_id,
            original_amount=original_amount,
            currency=original_amount.currency,
            issued_at=issued_at,
            due_date=due_date,
            created_at=created_at,
        )

    def _validate_amount(self) -> None:
        if not isinstance(self.original_amount, Money):
            raise ValidationError("Payable amount must be a Money value object")
        if self.original_amount.is_zero() or not self.original_amount.is_positive():
            raise ValidationError("Payable amount must be positive")

    def _validate_currency(self) -> None:
        if not isinstance(self.currency, Currency):
            raise ValidationError("Payable currency must be a Currency value object")
        if self.original_amount.currency != self.currency:
            raise ValidationError("Payable currency must match original_amount currency")

    def _validate_dates(self) -> None:
        if self.issued_at.tzinfo is None:
            object.__setattr__(self, "issued_at", self.issued_at.replace(tzinfo=timezone.utc))
        if self.due_date.tzinfo is None:
            object.__setattr__(self, "due_date", self.due_date.replace(tzinfo=timezone.utc))
        if self.due_date < self.issued_at:
            raise ValidationError("Payable due_date cannot be before issued_at")

    def outstanding(self, transaction_history: list[FinancialTransaction]) -> Money:
        total_paid = Money.zero(self.currency)
        for transaction in transaction_history:
            if transaction.payable_id != self.id:
                continue
            if transaction.is_currency(self.currency) is False:
                raise ValidationError("Payable transaction currency must match payable currency")
            if transaction.type == TransactionType.PAYMENT:
                total_paid += transaction.amount
            elif transaction.type == TransactionType.REVERSAL:
                if transaction.related_transaction_id is not None:
                    total_paid -= transaction.amount
        return self.original_amount - total_paid

    def status_for(self, transaction_history: list[FinancialTransaction], as_of: datetime | None = None) -> PayableStatus:
        outstanding = self.outstanding(transaction_history)
        if outstanding.is_zero():
            return PayableStatus.PAID

        if as_of is None:
            as_of = SystemClock().now()
        if as_of.tzinfo is None:
            as_of = as_of.replace(tzinfo=timezone.utc)
        if as_of > self.due_date:
            return PayableStatus.OVERDUE

        if outstanding < self.original_amount:
            return PayableStatus.PARTIALLY_PAID

        return PayableStatus.OPEN

    def can_accept_payment(self, amount: Money, transaction_history: list[FinancialTransaction]) -> bool:
        if amount.currency != self.currency:
            raise ValidationError("Payment currency must match payable currency")
        return self.outstanding(transaction_history) >= amount

    def is_overdue(self, as_of: datetime | None = None) -> bool:
        if as_of is None:
            as_of = SystemClock().now()
        if as_of.tzinfo is None:
            as_of = as_of.replace(tzinfo=timezone.utc)
        return as_of > self.due_date
