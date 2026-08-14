"""Clock abstraction for deterministic time-aware domain logic."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol


class Clock(Protocol):
    """Abstracts current time for domain logic and tests."""

    def now(self) -> datetime:
        """Return the current time."""


class FakeClock:
    """Simple deterministic clock used in tests and domain-level scenarios."""

    def __init__(self, current_time: datetime | None = None) -> None:
        if current_time is None:
            current_time = datetime.now(timezone.utc)
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)
        self._current_time = current_time

    def now(self) -> datetime:
        return self._current_time

    def set_time(self, current_time: datetime) -> None:
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)
        self._current_time = current_time
