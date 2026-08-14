from datetime import datetime, timedelta, timezone

import pytest

from ledgerflow.domain.ledger.financial_transaction import FinancialTransaction
from ledgerflow.domain.ledger.transaction_type import TransactionType
from ledgerflow.domain.receivable import Receivable, ReceivableStatus
from ledgerflow.domain.shared.currency import Currency
from ledgerflow.domain.shared.exceptions import ValidationError
from ledgerflow.domain.shared.identifiers import Identifier
from ledgerflow.domain.shared.money import Money


def test_create_receivable_requires_positive_amount() -> None:
    with pytest.raises(ValidationError):
        Receivable.create(
            customer_id=Identifier.generate(),
            original_amount=Money(0, Currency("TRY")),
            due_date=datetime(2026, 8, 20, tzinfo=timezone.utc),
        )


def test_create_receivable_accepts_valid_value() -> None:
    receivable = Receivable.create(
        customer_id=Identifier.generate(),
        original_amount=Money(1000, Currency("TRY")),
        due_date=datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert receivable.original_amount == Money(1000, Currency("TRY"))
    assert receivable.currency == Currency("TRY")


def test_outstanding_is_derived_from_transaction_history() -> None:
    receivable = Receivable.create(
        customer_id=Identifier.generate(),
        original_amount=Money(1000, Currency("TRY")),
        due_date=datetime(2026, 8, 20, tzinfo=timezone.utc),
    )

    payment_a = FinancialTransaction.create(
        transaction_type=TransactionType.PAYMENT,
        amount=Money(300, Currency("TRY")),
        receivable_id=receivable.id,
        description="Partial payment",
    )
    payment_b = FinancialTransaction.create(
        transaction_type=TransactionType.PAYMENT,
        amount=Money(200, Currency("TRY")),
        receivable_id=receivable.id,
        description="Partial payment",
    )

    assert receivable.outstanding([payment_a, payment_b]) == Money(500, Currency("TRY"))


def test_receivable_becomes_paid_when_history_covers_full_amount() -> None:
    receivable = Receivable.create(
        customer_id=Identifier.generate(),
        original_amount=Money(1000, Currency("TRY")),
        due_date=datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    payment = FinancialTransaction.create(
        transaction_type=TransactionType.PAYMENT,
        amount=Money(1000, Currency("TRY")),
        receivable_id=receivable.id,
        description="Full payment",
    )

    assert receivable.status_for([payment], as_of=datetime(2026, 8, 15, tzinfo=timezone.utc)) == ReceivableStatus.PAID


def test_receivable_becomes_overdue_after_due_date() -> None:
    receivable = Receivable.create(
        customer_id=Identifier.generate(),
        original_amount=Money(1000, Currency("TRY")),
        issued_at=datetime(2026, 7, 15, tzinfo=timezone.utc),
        due_date=datetime(2026, 8, 1, tzinfo=timezone.utc),
    )

    assert receivable.status_for([], as_of=datetime(2026, 8, 15, tzinfo=timezone.utc)) == ReceivableStatus.OVERDUE


def test_receivable_status_is_partially_paid_when_amount_remains() -> None:
    receivable = Receivable.create(
        customer_id=Identifier.generate(),
        original_amount=Money(1000, Currency("TRY")),
        due_date=datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    payment = FinancialTransaction.create(
        transaction_type=TransactionType.PAYMENT,
        amount=Money(300, Currency("TRY")),
        receivable_id=receivable.id,
        description="Partial payment",
    )

    assert receivable.status_for([payment], as_of=datetime(2026, 8, 10, tzinfo=timezone.utc)) == ReceivableStatus.PARTIALLY_PAID


def test_write_off_marks_receivable_written_off() -> None:
    receivable = Receivable.create(
        customer_id=Identifier.generate(),
        original_amount=Money(1000, Currency("TRY")),
        due_date=datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    write_off = FinancialTransaction.create(
        transaction_type=TransactionType.WRITE_OFF,
        amount=Money(1000, Currency("TRY")),
        receivable_id=receivable.id,
        description="Write off",
    )

    assert receivable.status_for([write_off], as_of=datetime(2026, 8, 15, tzinfo=timezone.utc)) == ReceivableStatus.WRITTEN_OFF


def test_payment_validation_rejects_overpayment() -> None:
    receivable = Receivable.create(
        customer_id=Identifier.generate(),
        original_amount=Money(1000, Currency("TRY")),
        due_date=datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    payment = Money(1100, Currency("TRY"))

    assert receivable.can_accept_payment(payment, []) is False
