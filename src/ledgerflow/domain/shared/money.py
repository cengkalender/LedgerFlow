"""Money value object for domain calculations."""

from __future__ import annotations

from dataclasses import dataclass

from .currency import Currency
from .exceptions import CurrencyMismatchError, InvalidMoneyOperation


@dataclass(frozen=True, slots=True)
class Money:
    """Immutable monetary value stored as integer minor units."""

    amount: int
    currency: Currency

    def __post_init__(self) -> None:
        if not isinstance(self.amount, int):
            raise InvalidMoneyOperation("Money amount must be an integer in minor units")
        if isinstance(self.amount, bool):
            raise InvalidMoneyOperation("Money amount cannot be boolean")

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            raise InvalidMoneyOperation("Can only add Money to Money")
        if self.currency != other.currency:
            raise CurrencyMismatchError(
                f"Cannot add different currencies: {self.currency} and {other.currency}"
            )
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            raise InvalidMoneyOperation("Can only subtract Money from Money")
        if self.currency != other.currency:
            raise CurrencyMismatchError(
                f"Cannot subtract different currencies: {self.currency} and {other.currency}"
            )
        return Money(self.amount - other.amount, self.currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other: "Money") -> bool:
        self._ensure_same_currency(other)
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        self._ensure_same_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        self._ensure_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        self._ensure_same_currency(other)
        return self.amount >= other.amount

    def __mul__(self, factor: int) -> "Money":
        if not isinstance(factor, int) or isinstance(factor, bool):
            raise InvalidMoneyOperation("Multiplier must be an integer")
        return Money(self.amount * factor, self.currency)

    __rmul__ = __mul__

    def is_zero(self) -> bool:
        return self.amount == 0

    def is_positive(self) -> bool:
        return self.amount > 0

    def is_negative(self) -> bool:
        return self.amount < 0

    def _ensure_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise CurrencyMismatchError(
                f"Cannot compare different currencies: {self.currency} and {other.currency}"
            )

    @classmethod
    def zero(cls, currency: Currency) -> "Money":
        return cls(0, currency)

    def __str__(self) -> str:
        return f"{self.amount} {self.currency.code}"
