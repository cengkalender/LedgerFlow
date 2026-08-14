from ledgerflow.domain.shared.identifiers import Identifier


def test_identifier_can_be_generated() -> None:
    value = Identifier.generate()
    assert isinstance(value.value, str)
    assert len(value.value) > 0


def test_identifier_is_string_like() -> None:
    value = Identifier("123e4567-e89b-12d3-a456-426614174000")
    assert str(value) == "123e4567-e89b-12d3-a456-426614174000"
