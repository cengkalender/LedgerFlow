from datetime import datetime, timezone

import pytest

from ledgerflow.domain.ledger.financial_transaction import FinancialTransaction
from ledgerflow.domain.ledger.transaction_type import TransactionType
from ledgerflow.domain.payable import Payable, PayableStatus
from ledgerflow.domain.shared.currency import Currency
from ledgerflow.domain.shared.exceptions import ValidationError
from ledgerflow.domain.shared.identifiers import Identifier
from ledgerflow.domain.shared.money import Money


def test_create_payable_requires_positive_amount() -> None:
    with pytest.raises(ValidationError):
        Payable.create(
            supplier_id=Identifier.generate(),
            original_amount=Money(0, Currency("TRY")),
            due_date=datetime(2026, 8, 20, tzinfo=timezone.utc),
        )


def test_create_payable_accepts_valid_value() -> None:
    payable = Payable.create(
        supplier_id=Identifier.generate(),
        original_amount=Money(1500, Currency("TRY")),
        due_date=datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    assert payable.original_amount == Money(1500, Currency("TRY"))
    assert payable.currency == Currency("TRY")


def test_outstanding_is_derived_from_transaction_history() -> None:
    payable = Payable.create(
        supplier_id=Identifier.generate(),
        original_amount=Money(1000, Currency("TRY")),
        due_date=datetime(2026, 8, 20, tzinfo=timezone.utc),
    )

    payment_a = FinancialTransaction.create(
        transaction_type=TransactionType.PAYMENT,
        amount=Money(200, Currency("TRY")),
        payable_id=payable.id,
        description="Supplier partial payment",
    )
    payment_b = FinancialTransaction.create(
        transaction_type=TransactionType.PAYMENT,
        amount=Money(300, Currency("TRY")),
        payable_id=payable.id,
        description="Supplier partial payment",
    )

    assert payable.outstanding([payment_a, payment_b]) == Money(500, Currency("TRY"))


def test_payable_becomes_paid_when_history_covers_full_amount() -> None:
    payable = Payable.create(
        supplier_id=Identifier.generate(),
        original_amount=Money(1000, Currency("TRY")),
        due_date=datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    payment = FinancialTransaction.create(
        transaction_type=TransactionType.PAYMENT,
        amount=Money(1000, Currency("TRY")),
        payable_id=payable.id,
        description="Full supplier payment",
    )

    assert payable.status_for([payment], as_of=datetime(2026, 8, 15, tzinfo=timezone.utc)) == PayableStatus.PAID


def test_payable_becomes_overdue_after_due_date() -> None:
    payable = Payable.create(
        supplier_id=Identifier.generate(),
        original_amount=Money(1000, Currency("TRY")),
        issued_at=datetime(2026, 7, 15, tzinfo=timezone.utc),
        due_date=datetime(2026, 8, 1, tzinfo=timezone.utc),
    )

    assert payable.status_for([], as_of=datetime(2026, 8, 15, tzinfo=timezone.utc)) == PayableStatus.OVERDUE


def test_payable_status_is_partially_paid_when_amount_remains() -> None:
    payable = Payable.create(
        supplier_id=Identifier.generate(),
        original_amount=Money(1000, Currency("TRY")),
        due_date=datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    payment = FinancialTransaction.create(
        transaction_type=TransactionType.PAYMENT,
        amount=Money(300, Currency("TRY")),
        payable_id=payable.id,
        description="Supplier partial payment",
    )

    assert payable.status_for([payment], as_of=datetime(2026, 8, 10, tzinfo=timezone.utc)) == PayableStatus.PARTIALLY_PAID


def test_payment_validation_rejects_overpayment() -> None:
    payable = Payable.create(
        supplier_id=Identifier.generate(),
        original_amount=Money(1000, Currency("TRY")),
        due_date=datetime(2026, 8, 20, tzinfo=timezone.utc),
    )
    payment = Money(1100, Currency("TRY"))

    assert payable.can_accept_payment(payment, []) is False
