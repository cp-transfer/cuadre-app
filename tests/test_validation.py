
import pytest

from cuadre.validation import (
    parse_money,
    parse_quantity,
    validate_cash_verification,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", 0),
        ("   ", 0),
        (None, 0),
        ("0", 0),
        ("150000", 150000),
        ("150.000", 150000),
        ("1.250.000", 1250000),
        (150000, 150000),
    ],
)
def test_parse_valid_money(value, expected):
    assert parse_money(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "-100",
        "1.5",
        "150,50",
        "12.34",
        "abc",
        "1.000.00",
        150.5,
        True,
    ],
)
def test_parse_invalid_money(value):
    with pytest.raises(ValueError):
        parse_money(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", 0),
        (None, 0),
        ("15", 15),
        (15, 15),
        ("1.000", 1000),
    ],
)
def test_parse_valid_quantity(value, expected):
    assert parse_quantity(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "-1",
        "1.5",
        "abc",
        1.5,
        True,
    ],
)
def test_parse_invalid_quantity(value):
    with pytest.raises(ValueError):
        parse_quantity(value)


def test_cash_matches_expected_without_note():
    result = validate_cash_verification(100000, True)
    assert result.matches_expected is True
    assert result.discrepancy_note == ""


def test_cash_mismatch_requires_note():
    with pytest.raises(ValueError):
        validate_cash_verification(100000, False)


def test_cash_mismatch_with_note_is_valid():
    result = validate_cash_verification(
        100000,
        False,
        "Faltan 20.000 pesos en caja",
    )
    assert result.matches_expected is False
    assert result.discrepancy_note == "Faltan 20.000 pesos en caja"


def test_negative_expected_cash_requires_note():
    with pytest.raises(ValueError):
        validate_cash_verification(-50000, False)


def test_negative_expected_cash_with_note_is_valid():
    result = validate_cash_verification(
        -50000,
        False,
        "Revisar ventas y medios de pago",
    )
    assert result.matches_expected is False


def test_note_is_trimmed():
    result = validate_cash_verification(
        100000,
        False,
        "  Diferencia identificada  ",
    )
    assert result.discrepancy_note == "Diferencia identificada"

def test_negative_expected_cash_cannot_be_confirmed_as_match():
    with pytest.raises(ValueError):
        validate_cash_verification(
            -50000,
            True,
            "Revisar contabilidad",
        )
