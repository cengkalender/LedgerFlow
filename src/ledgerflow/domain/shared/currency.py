"""Currency value object."""

from __future__ import annotations

from dataclasses import dataclass

from .exceptions import InvalidCurrencyError


@dataclass(frozen=True, slots=True)
class Currency:
    """Represents a ISO-like currency code without conversion logic."""

    code: str

    def __post_init__(self) -> None:
        normalized = self.code.strip().upper()
        if not normalized or len(normalized) != 3 or not normalized.isalpha():
            raise InvalidCurrencyError(f"Invalid currency code: {self.code!r}")
        object.__setattr__(self, "code", normalized)

    def __str__(self) -> str:
        return self.code
