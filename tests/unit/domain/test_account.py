import pytest

from ledgerflow.domain.account import Account, AccountStatus, AccountType
from ledgerflow.domain.shared.currency import Currency
from ledgerflow.domain.shared.exceptions import ValidationError
from ledgerflow.domain.shared.identifiers import Identifier


def test_create_account_defaults_to_active_status() -> None:
    account = Account.create(
        name="Cash Box",
        account_type=AccountType.CASH,
        currency=Currency("TRY"),
    )
    assert account.status == AccountStatus.ACTIVE
    assert account.id is not None


def test_account_requires_name() -> None:
    with pytest.raises(ValidationError):
        Account.create(name="   ", account_type=AccountType.CASH, currency=Currency("TRY"))


def test_account_rejects_invalid_type() -> None:
    with pytest.raises(ValidationError):
        Account(
            id=Identifier.generate(),
            name="Cash",
            account_type="INVALID",  # type: ignore[arg-type]
            currency=Currency("TRY"),
        )


def test_account_can_be_archived() -> None:
    account = Account.create(name="Bank", account_type=AccountType.BANK, currency=Currency("TRY"))
    account.archive()
    assert account.status == AccountStatus.ARCHIVED


def test_account_can_be_activated() -> None:
    account = Account.create(name="Safe", account_type=AccountType.OTHER, currency=Currency("TRY"))
    account.archive()
    account.activate()
    assert account.status == AccountStatus.ACTIVE


def test_archived_account_cannot_accept_transfer() -> None:
    account = Account.create(name="Bank", account_type=AccountType.BANK, currency=Currency("TRY"))
    account.archive()
    assert account.can_accept_transfer() is False
    assert account.can_be_source_for_transfer() is False


def test_active_account_can_accept_transfer() -> None:
    account = Account.create(name="Cash", account_type=AccountType.CASH, currency=Currency("TRY"))
    assert account.can_accept_transfer() is True
    assert account.can_be_source_for_transfer() is True


def test_account_currency_is_explicit() -> None:
    account = Account.create(name="Bank", account_type=AccountType.BANK, currency=Currency("USD"))
    assert account.currency == Currency("USD")


def test_same_currency_check() -> None:
    first = Account.create(name="Cash", account_type=AccountType.CASH, currency=Currency("TRY"))
    second = Account.create(name="Bank", account_type=AccountType.BANK, currency=Currency("TRY"))
    assert first.is_same_currency(second)
