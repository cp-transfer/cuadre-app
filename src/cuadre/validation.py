
import re
from dataclasses import dataclass


_INTEGER_PATTERN = re.compile(r"^\d+$")
_GROUPED_PATTERN = re.compile(r"^\d{1,3}(?:\.\d{3})+$")


def _parse_nonnegative_integer(value, field_name: str) -> int:
    if value is None:
        return 0

    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a non-negative integer.")

    if isinstance(value, int):
        if value < 0:
            raise ValueError(f"{field_name} cannot be negative.")
        return value

    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be entered as an integer.")

    value = value.strip()

    if value == "":
        return 0

    if _INTEGER_PATTERN.fullmatch(value):
        return int(value)

    if _GROUPED_PATTERN.fullmatch(value):
        return int(value.replace(".", ""))

    raise ValueError(f"Invalid value for {field_name}: {value!r}")


def parse_money(value) -> int:
    """Parse whole Colombian pesos. Empty input becomes zero."""

    return _parse_nonnegative_integer(value, "Monetary amount")


def parse_quantity(value, field_name: str = "Quantity") -> int:
    """Parse a non-negative whole-number quantity."""

    return _parse_nonnegative_integer(value, field_name)


@dataclass(frozen=True)
class CashVerification:
    matches_expected: bool
    discrepancy_note: str = ""


def validate_cash_verification(
    expected_cash: int,
    matches_expected: bool,
    discrepancy_note: str = "",
) -> CashVerification:
    """
    Validate the employee's cash confirmation.

    A mismatch always requires a note.
    Negative expected cash always requires a note.
    """

    if isinstance(expected_cash, bool) or not isinstance(expected_cash, int):
        raise TypeError("Expected cash must be an integer.")

    if not isinstance(matches_expected, bool):
        raise TypeError("Cash confirmation must be True or False.")

    if not isinstance(discrepancy_note, str):
        raise TypeError("Discrepancy note must be text.")

    note = discrepancy_note.strip()

    if not matches_expected and not note:
        raise ValueError("A discrepancy note is required when cash does not match.")

    if expected_cash < 0:
        if matches_expected:
            raise ValueError("Negative expected cash cannot be confirmed as a match.")

        if not note:
            raise ValueError("A note is required when expected cash is negative.")

    return CashVerification(
        matches_expected=matches_expected,
        discrepancy_note=note,
    )
