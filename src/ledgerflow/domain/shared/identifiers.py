"""Simple identifier abstraction for domain entities."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from .exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class Identifier:
    """String-backed UUID identifier with validation and generation support."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValidationError("Identifier value cannot be empty")
        try:
            UUID(str(self.value))
        except ValueError as exc:
            raise ValidationError(f"Invalid identifier: {self.value!r}") from exc
        object.__setattr__(self, "value", str(self.value))

    @classmethod
    def generate(cls) -> "Identifier":
        return cls(str(uuid4()))

    def __str__(self) -> str:
        return self.value
