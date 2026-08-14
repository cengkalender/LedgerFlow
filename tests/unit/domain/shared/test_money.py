import pytest

from ledgerflow.domain.shared.currency import Currency
from ledgerflow.domain.shared.exceptions import CurrencyMismatchError, InvalidMoneyOperation
from ledgerflow.domain.shared.money import Money


def test_money_creation_uses_minor_units() -> None:
    money = Money(12550, Currency("TRY"))
    assert money.amount == 12550
    assert str(money.currency) == "TRY"


def test_money_same_currency_addition() -> None:
    total = Money(100, Currency("TRY")) + Money(50, Currency("TRY"))
    assert total == Money(150, Currency("TRY"))


def test_money_same_currency_subtraction() -> None:
    result = Money(100, Currency("TRY")) - Money(25, Currency("TRY"))
    assert result == Money(75, Currency("TRY"))


def test_money_currency_mismatch_raises_error() -> None:
    with pytest.raises(CurrencyMismatchError):
        Money(100, Currency("TRY")) + Money(100, Currency("USD"))


def test_money_equality_works() -> None:
    assert Money(100, Currency("TRY")) == Money(100, Currency("TRY"))
    assert Money(100, Currency("TRY")) != Money(101, Currency("TRY"))


def test_money_comparison_works() -> None:
    assert Money(100, Currency("TRY")) < Money(200, Currency("TRY"))
    assert Money(200, Currency("TRY")) >= Money(200, Currency("TRY"))


def test_money_zero_and_sign_checks() -> None:
    assert Money.zero(Currency("TRY")).is_zero()
    assert Money(5, Currency("TRY")).is_positive()
    assert Money(-5, Currency("TRY")).is_negative()


def test_money_rejects_float_like_values() -> None:
    with pytest.raises(InvalidMoneyOperation):
        Money(10.5, Currency("TRY"))


def test_money_rejects_non_money_addition() -> None:
    with pytest.raises(InvalidMoneyOperation):
        Money(100, Currency("TRY")) + 50  # type: ignore[operator]
