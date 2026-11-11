
import pytest

from cuadre.validation import (
    build_reconciliation_amounts,
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
        ("150,000", 150000),
        ("1.250.000", 1250000),
        ("1,250,000", 1250000),
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
        "1.000,000",
        "1,000.000",
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
        ("1,000", 1000),
        ("1.250.000", 1250000),
        ("1,250,000", 1250000),
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
        "1.000,000",
        "1,000.000",
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

ALL_RAW_VALUES = {
    "net_sales": "150.000",
    "cards": "20.000",
    "qr": "10.000",
    "sistecredito": "",
    "addi": None,
    "coupons_redeemed": "5.000",
    "coupons_sold_cash": "500",
    "coupons_sold_other_method": "1,000",
    "expenses": "2.000",
    "sistecredito_collections": "1.000",
    "bags": "10",
    "garments": "25",
    "garments_exchange": "2",
}


def test_build_reconciliation_amounts():
    amounts = build_reconciliation_amounts(
        ALL_RAW_VALUES,
        coupons_sold_other_method_details="Tarjeta y QR",
    )

    assert amounts.net_sales == 150000
    assert amounts.cards == 20000
    assert amounts.qr == 10000
    assert amounts.sistecredito == 0
    assert amounts.addi == 0
    assert amounts.coupons_redeemed == 5000
    assert amounts.coupons_sold_cash == 500
    assert amounts.coupons_sold_other_method == 1000
    assert amounts.coupons_sold_other_method_details == "Tarjeta y QR"
    assert amounts.expenses == 2000
    assert amounts.sistecredito_collections == 1000
    assert amounts.bags == 10
    assert amounts.garments == 25
    assert amounts.garments_exchange == 2


def test_build_reconciliation_amounts_preserves_field_notes():
    amounts = build_reconciliation_amounts(
        ALL_RAW_VALUES,
        field_notes={"expenses": "Gasto autorizado"},
        coupons_sold_other_method_details="Tarjeta",
    )

    assert amounts.field_notes["expenses"] == "Gasto autorizado"


def test_build_reconciliation_amounts_requires_other_method_details():
    with pytest.raises(ValueError, match="Payment method details are required"):
        build_reconciliation_amounts(
            ALL_RAW_VALUES,
            coupons_sold_other_method_details="",
        )


def test_build_reconciliation_amounts_rejects_missing_fields():
    with pytest.raises(ValueError, match="Missing reconciliation fields"):
        build_reconciliation_amounts({"net_sales": "100000"})


def test_build_reconciliation_amounts_rejects_unknown_fields():
    with pytest.raises(ValueError, match="Unknown reconciliation fields"):
        build_reconciliation_amounts({
            **ALL_RAW_VALUES,
            "unknown_field": "100",
        })


def test_build_reconciliation_amounts_rejects_invalid_values():
    raw_values = {
        **ALL_RAW_VALUES,
        "net_sales": "abc",
    }

    with pytest.raises(ValueError):
        build_reconciliation_amounts(raw_values)
