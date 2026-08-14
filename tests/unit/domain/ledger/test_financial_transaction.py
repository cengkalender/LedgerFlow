import pytest

from ledgerflow.domain.ledger.financial_transaction import FinancialTransaction
from ledgerflow.domain.ledger.transaction_type import TransactionType
from ledgerflow.domain.shared.currency import Currency
from ledgerflow.domain.shared.exceptions import ValidationError
from ledgerflow.domain.shared.identifiers import Identifier
from ledgerflow.domain.shared.money import Money


def test_income_requires_account() -> None:
    with pytest.raises(ValidationError):
        FinancialTransaction.create(
            transaction_type=TransactionType.INCOME,
            amount=Money(1000, Currency("TRY")),
            account_id=None,
        )


def test_credit_requires_receivable() -> None:
    with pytest.raises(ValidationError):
        FinancialTransaction.create(
            transaction_type=TransactionType.CREDIT,
            amount=Money(1000, Currency("TRY")),
            account_id=Identifier.generate(),
            receivable_id=None,
        )


def test_payment_requires_related_obligation() -> None:
    with pytest.raises(ValidationError):
        FinancialTransaction.create(
            transaction_type=TransactionType.PAYMENT,
            amount=Money(300, Currency("TRY")),
            account_id=Identifier.generate(),
            receivable_id=None,
            payable_id=None,
        )


def test_transfer_requires_transfer_id() -> None:
    with pytest.raises(ValidationError):
        FinancialTransaction.create(
            transaction_type=TransactionType.TRANSFER_OUT,
            amount=Money(1000, Currency("TRY")),
            account_id=Identifier.generate(),
            transfer_id=None,
        )


def test_reversal_requires_related_transaction() -> None:
    with pytest.raises(ValidationError):
        FinancialTransaction.create(
            transaction_type=TransactionType.REVERSAL,
            amount=Money(-1000, Currency("TRY")),
            account_id=Identifier.generate(),
            related_transaction_id=None,
        )


def test_amount_zero_is_rejected() -> None:
    with pytest.raises(ValidationError):
        FinancialTransaction.create(
            transaction_type=TransactionType.INCOME,
            amount=Money(0, Currency("TRY")),
            account_id=Identifier.generate(),
        )


def test_linked_transfer_is_identified() -> None:
    transfer_id = Identifier.generate()
    tx = FinancialTransaction.create(
        transaction_type=TransactionType.TRANSFER_OUT,
        amount=Money(2000, Currency("TRY")),
        account_id=Identifier.generate(),
        transfer_id=transfer_id,
        description="Transfer out",
    )
    assert tx.is_linked_transfer() is True


def test_balance_sign_for_outgoing_is_negative() -> None:
    tx = FinancialTransaction.create(
        transaction_type=TransactionType.EXPENSE,
        amount=Money(500, Currency("TRY")),
        account_id=Identifier.generate(),
    )
    assert tx.amount_for_balance() == -500


def test_balance_sign_for_incoming_is_positive() -> None:
    tx = FinancialTransaction.create(
        transaction_type=TransactionType.INCOME,
        amount=Money(500, Currency("TRY")),
        account_id=Identifier.generate(),
    )
    assert tx.amount_for_balance() == 500
