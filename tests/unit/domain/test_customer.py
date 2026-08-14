from datetime import datetime, timezone

import pytest

from ledgerflow.domain.customer import ContactInfo, Customer, CustomerStatus
from ledgerflow.domain.shared.currency import Currency
from ledgerflow.domain.shared.exceptions import DomainError, ValidationError
from ledgerflow.domain.shared.identifiers import Identifier
from ledgerflow.domain.shared.money import Money


def test_create_customer_defaults_to_active_status() -> None:
    customer = Customer.create(name="Aylin Demo")
    assert customer.status == CustomerStatus.ACTIVE
    assert customer.id is not None


def test_customer_requires_name() -> None:
    with pytest.raises(ValidationError):
        Customer.create(name="   ")


def test_customer_rejects_negative_credit_limit() -> None:
    with pytest.raises(ValidationError):
        Customer.create(name="John", credit_limit=Money(-1, Currency("TRY")))


def test_customer_block_and_activate_cycle() -> None:
    customer = Customer.create(name="John")
    customer.block()
    assert customer.status == CustomerStatus.BLOCKED
    customer.activate()
    assert customer.status == CustomerStatus.ACTIVE


def test_customer_can_be_archived() -> None:
    customer = Customer.create(name="John")
    customer.archive()
    assert customer.status == CustomerStatus.ARCHIVED


def test_archived_customer_cannot_be_activated() -> None:
    customer = Customer.create(name="John")
    customer.archive()
    with pytest.raises(DomainError):
        customer.activate()


def test_archived_customer_cannot_receive_credit() -> None:
    customer = Customer.create(name="John")
    customer.archive()
    assert customer.can_receive_credit() is False


def test_blocked_customer_cannot_receive_credit() -> None:
    customer = Customer.create(name="John")
    customer.block()
    assert customer.can_receive_credit() is False


def test_active_customer_can_receive_credit() -> None:
    customer = Customer.create(name="John")
    assert customer.can_receive_credit() is True


def test_credit_limit_currency_must_match() -> None:
    customer = Customer.create(name="John", credit_limit=Money(1000, Currency("TRY")))
    with pytest.raises(ValidationError):
        customer.set_credit_limit(Money(1000, Currency("USD")))


def test_set_credit_limit_updates_value() -> None:
    customer = Customer.create(name="John", credit_limit=Money(1000, Currency("TRY")))
    customer.set_credit_limit(Money(2000, Currency("TRY")))
    assert customer.credit_limit == Money(2000, Currency("TRY"))


def test_contact_info_is_immutable() -> None:
    contact = ContactInfo(phone=" +90 555 123 45 67 ", email="  USER@EXAMPLE.COM  ")
    assert contact.phone == "+90 555 123 45 67"
    assert contact.email == "user@example.com"


def test_customer_identity_is_stable() -> None:
    customer_id = Identifier.generate()
    customer = Customer(
        id=customer_id,
        name="Melis",
        status=CustomerStatus.ACTIVE,
        credit_limit=Money.zero(Currency("TRY")),
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    assert customer.id == customer_id
