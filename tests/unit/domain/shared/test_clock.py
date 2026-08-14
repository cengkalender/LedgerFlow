from datetime import datetime, timezone

from ledgerflow.domain.shared.clock import FakeClock


def test_fake_clock_returns_configured_time() -> None:
    value = datetime(2024, 1, 1, tzinfo=timezone.utc)
    clock = FakeClock(value)
    assert clock.now() == value


def test_fake_clock_can_be_updated() -> None:
    clock = FakeClock()
    updated = datetime(2025, 5, 5, tzinfo=timezone.utc)
    clock.set_time(updated)
    assert clock.now() == updated
