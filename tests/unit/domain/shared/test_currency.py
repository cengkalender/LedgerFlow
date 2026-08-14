from ledgerflow.domain.shared.currency import Currency
from ledgerflow.domain.shared.exceptions import InvalidCurrencyError


def test_currency_normalizes_to_uppercase() -> None:
    assert str(Currency("try")) == "TRY"


def test_currency_rejects_invalid_values() -> None:
    for value in ("", "TR", "123", "TURKEY"):
        try:
            Currency(value)
        except InvalidCurrencyError:
            pass
        else:
            raise AssertionError(f"Expected InvalidCurrencyError for {value!r}")


def test_currency_is_immutable() -> None:
    currency = Currency("USD")
    assert currency.code == "USD"
