"""Account aggregate root for LedgerFlow."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .shared.clock import SystemClock
from .shared.currency import Currency
from .shared.exceptions import DomainError, ValidationError
from .shared.identifiers import Identifier


class AccountType(str, Enum):
    CASH = "CASH"
    BANK = "BANK"
    OTHER = "OTHER"


class AccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


@dataclass(slots=True)
class Account:
    """Account aggregate root for internal cash storage and movement."""

    id: Identifier
    name: str
    account_type: AccountType
    currency: Currency
    status: AccountStatus = AccountStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: SystemClock().now())

    def __post_init__(self) -> None:
        self._validate_name()
        self._validate_account_type()
        self._validate_status()

    @classmethod
    def create(
        cls,
        *,
        name: str,
        account_type: AccountType,
        currency: Currency,
        account_id: Identifier | None = None,
        created_at: datetime | None = None,
    ) -> "Account":
        normalized_name = name.strip()
        if not normalized_name:
            raise ValidationError("Account name is required")

        if created_at is None:
            created_at = SystemClock().now()

        return cls(
            id=account_id or Identifier.generate(),
            name=normalized_name,
            account_type=account_type,
            currency=currency,
            status=AccountStatus.ACTIVE,
            created_at=created_at,
        )

    def _validate_name(self) -> None:
        if not self.name or not self.name.strip():
            raise ValidationError("Account name cannot be blank")
        self.name = self.name.strip()

    def _validate_account_type(self) -> None:
        if not isinstance(self.account_type, AccountType):
            raise ValidationError("Account type must be a valid AccountType value")

    def _validate_status(self) -> None:
        if not isinstance(self.status, AccountStatus):
            raise ValidationError("Account status must be a valid AccountStatus value")

    def archive(self) -> None:
        if self.status == AccountStatus.ARCHIVED:
            return
        self.status = AccountStatus.ARCHIVED

    def activate(self) -> None:
        if self.status == AccountStatus.ACTIVE:
            return
        self.status = AccountStatus.ACTIVE

    def can_accept_transfer(self) -> bool:
        return self.status == AccountStatus.ACTIVE

    def can_be_source_for_transfer(self) -> bool:
        return self.status == AccountStatus.ACTIVE

    def is_same_currency(self, other: "Account") -> bool:
        return self.currency == other.currency

    def __str__(self) -> str:
        return f"{self.name} ({self.account_type.value})"
