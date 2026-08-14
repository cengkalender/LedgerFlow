"""Shared domain exceptions."""


class DomainError(Exception):
    """Base class for domain-layer validation and invariant errors."""


class ValidationError(DomainError):
    """Raised when a domain value violates invariants."""


class InvalidCurrencyError(ValidationError):
    """Raised when a currency value is invalid."""


class CurrencyMismatchError(ValidationError):
    """Raised when arithmetic is attempted across different currencies."""


class InvalidMoneyOperation(ValidationError):
    """Raised when a money operation is invalid."""
