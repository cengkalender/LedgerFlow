"""Customer aggregate root for LedgerFlow."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .shared.clock import SystemClock
from .shared.currency import Currency
from .shared.exceptions import DomainError, ValidationError
from .shared.identifiers import Identifier
from .shared.money import Money


class CustomerStatus(str, Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    ARCHIVED = "ARCHIVED"


@dataclass(frozen=True, slots=True)
class ContactInfo:
    """Small immutable contact summary for customer identity."""

    phone: str | None = None
    email: str | None = None

    def __post_init__(self) -> None:
        if self.phone is not None:
            object.__setattr__(self, "phone", self.phone.strip())
        if self.email is not None:
            email = self.email.strip().lower()
            object.__setattr__(self, "email", email)


@dataclass(slots=True)
class Customer:
    """Aggregate root for customer lifecycle and credit relationship."""

    id: Identifier
    name: str
    status: CustomerStatus = CustomerStatus.ACTIVE
    credit_limit: Money = field(default_factory=lambda: Money.zero(Currency("TRY")))
    contact_info: ContactInfo | None = None
    created_at: datetime = field(default_factory=lambda: SystemClock().now())

    def __post_init__(self) -> None:
        self._validate_name()
        self._validate_credit_limit()
        self._validate_status()

    @classmethod
    def create(
        cls,
        *,
        name: str,
        credit_limit: Money | None = None,
        contact_info: ContactInfo | None = None,
        customer_id: Identifier | None = None,
        created_at: datetime | None = None,
    ) -> "Customer":
        normalized_name = name.strip()
        if not normalized_name:
            raise ValidationError("Customer name is required")

        if credit_limit is None:
            credit_limit = Money.zero(Currency("TRY"))

        if created_at is None:
            created_at = SystemClock().now()

        return cls(
            id=customer_id or Identifier.generate(),
            name=normalized_name,
            credit_limit=credit_limit,
            contact_info=contact_info,
            created_at=created_at,
            status=CustomerStatus.ACTIVE,
        )

    def _validate_name(self) -> None:
        if not self.name or not self.name.strip():
            raise ValidationError("Customer name cannot be blank")
        self.name = self.name.strip()

    def _validate_credit_limit(self) -> None:
        if self.credit_limit.is_negative():
            raise ValidationError("Credit limit cannot be negative")

    def _validate_status(self) -> None:
        if not isinstance(self.status, CustomerStatus):
            raise ValidationError("Customer status must be a valid CustomerStatus value")

    def can_receive_credit(self) -> bool:
        return self.status == CustomerStatus.ACTIVE

    def block(self) -> None:
        if self.status == CustomerStatus.ARCHIVED:
            raise DomainError("Archived customer cannot be blocked")
        self.status = CustomerStatus.BLOCKED

    def activate(self) -> None:
        if self.status == CustomerStatus.ARCHIVED:
            raise DomainError("Archived customer cannot be activated")
        self.status = CustomerStatus.ACTIVE

    def archive(self) -> None:
        if self.status == CustomerStatus.ARCHIVED:
            return
        self.status = CustomerStatus.ARCHIVED

    def set_credit_limit(self, new_limit: Money) -> None:
        if new_limit.is_negative():
            raise ValidationError("Credit limit cannot be negative")
        if self.credit_limit.currency != new_limit.currency:
            raise ValidationError("Credit limit currency must match the customer currency")
        self.credit_limit = new_limit
