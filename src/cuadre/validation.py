import re

from cuadre.models import CashVerification


_INTEGER_PATTERN = re.compile(r"^[0-9]+$")
_GROUPED_INTEGER_PATTERN = re.compile(r"^[0-9]{1,3}(?:\.[0-9]{3})+$")


def _parse_nonnegative_integer(value: object, field_name: str) -> int:
    if value is None:
        return 0

    if isinstance(value, bool):
        raise ValueError(
            f"{field_name} must be a valid nonnegative integer."
        )

    if isinstance(value, int):
        if value < 0:
            raise ValueError(f"{field_name} cannot be negative.")
        return value

    if not isinstance(value, str):
        raise ValueError(
            f"{field_name} must be a valid nonnegative integer."
        )

    normalized = value.strip()

    if not normalized:
        return 0

    if _INTEGER_PATTERN.fullmatch(normalized):
        return int(normalized)

    if _GROUPED_INTEGER_PATTERN.fullmatch(normalized):
        return int(normalized.replace(".", ""))

    raise ValueError(f"{field_name} must be a valid nonnegative integer.")


def parse_money(value: object) -> int:
    """Parse a monetary amount expressed in whole COP."""
    return _parse_nonnegative_integer(value, "Monetary amount")


def parse_quantity(value: object, field_name: str = "Quantity") -> int:
    """Parse a nonnegative whole-number quantity."""
    return _parse_nonnegative_integer(value, field_name)


def validate_cash_verification(
    expected_cash: int,
    matches_expected: bool,
    discrepancy_note: str = "",
) -> CashVerification:
    """
    Validate employee cash confirmation against calculated expected cash.

    A mismatch always requires a note.
    Negative expected cash cannot be confirmed as a match.
    """

    if isinstance(expected_cash, bool) or not isinstance(expected_cash, int):
        raise TypeError("Expected cash must be an integer.")

    if not isinstance(matches_expected, bool):
        raise TypeError("Cash confirmation must be True or False.")

    if not isinstance(discrepancy_note, str):
        raise TypeError("Discrepancy note must be text.")

    note = discrepancy_note.strip()

    if expected_cash < 0 and matches_expected:
        raise ValueError(
            "Negative expected cash cannot be confirmed as a match."
        )

    if not matches_expected and not note:
        raise ValueError(
            "A discrepancy note is required when cash does not match."
        )

    if expected_cash < 0 and not note:
        raise ValueError(
            "A note is required when expected cash is negative."
        )

    return CashVerification(
        matches_expected=matches_expected,
        discrepancy_note=note,
    )
