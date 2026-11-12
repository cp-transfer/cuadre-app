from datetime import date

import pytest

from cuadre.models import (
    CashVerification,
    Reconciliation,
    ReconciliationAmounts,
)


def test_reconciliation_creation():
    reconciliation = Reconciliation(
        date=date(2026, 11, 10),
        store_code="11",
        store_name="HIPER",
        amounts=ReconciliationAmounts(net_sales=100000),
    )

    assert reconciliation.date == date(2026, 11, 10)
    assert reconciliation.store_code == "11"
    assert reconciliation.store_name == "HIPER"
    assert reconciliation.amounts.net_sales == 100000
    assert reconciliation.cash_verification is None


def test_reconciliation_requires_valid_date():
    with pytest.raises(TypeError):
        Reconciliation(
            date="2026-11-10",
            store_code="11",
            store_name="HIPER",
            amounts=ReconciliationAmounts(),
        )


def test_reconciliation_rejects_datetime():
    from datetime import datetime

    with pytest.raises(TypeError):
        Reconciliation(
            date=datetime(2026, 11, 10),
            store_code="11",
            store_name="HIPER",
            amounts=ReconciliationAmounts(),
        )


@pytest.mark.parametrize(
    ("store_code", "store_name"),
    [
        ("", "HIPER"),
        ("11", ""),
        ("   ", "HIPER"),
        ("11", "   "),
    ],
)


def test_reconciliation_rejects_empty_store_identity(
    store_code,
    store_name,
):
    with pytest.raises(ValueError):
        Reconciliation(
            date=date(2026, 11, 10),
            store_code=store_code,
            store_name=store_name,
            amounts=ReconciliationAmounts(),
        )


def test_reconciliation_rejects_invalid_amounts():
    with pytest.raises(TypeError):
        Reconciliation(
            date=date(2026, 11, 10),
            store_code="11",
            store_name="HIPER",
            amounts={"net_sales": 100000},
        )


def test_store_identity_is_trimmed():
    reconciliation = Reconciliation(
        date=date(2026, 11, 10),
        store_code=" 11 ",
        store_name=" HIPER ",
        amounts=ReconciliationAmounts(),
    )

    assert reconciliation.store_code == "11"
    assert reconciliation.store_name == "HIPER"


def test_reconciliation_is_immutable():
    reconciliation = Reconciliation(
        date=date(2026, 11, 10),
        store_code="11",
        store_name="HIPER",
        amounts=ReconciliationAmounts(),
    )

    with pytest.raises(AttributeError):
        reconciliation.store_name = "JORDAN"


def test_cash_verification_rejects_mismatch_without_note():
    with pytest.raises(ValueError):
        CashVerification(matches_expected=False)


def test_cash_verification_trims_note():
    verification = CashVerification(
        matches_expected=False,
        discrepancy_note="  Diferencia identificada  ",
    )

    assert verification.discrepancy_note == "Diferencia identificada"


def test_cash_verification_allows_match_without_note():
    verification = CashVerification(matches_expected=True)

    assert verification.matches_expected is True
    assert verification.discrepancy_note == ""


def test_field_notes_require_mapping():
    with pytest.raises(TypeError):
        ReconciliationAmounts(field_notes=None)


def test_field_notes_reject_invalid_note_values():
    with pytest.raises(TypeError):
        ReconciliationAmounts(
            field_notes={"net_sales": 1000},
        )

def test_reconciliation_is_incomplete_without_cash_verification():
    reconciliation = Reconciliation(
        date=date(2026, 11, 10),
        store_code="11",
        store_name="HIPER",
        amounts=ReconciliationAmounts(net_sales=100000),
    )

    assert reconciliation.is_complete is False


def test_reconciliation_requires_cash_verification_for_submission():
    reconciliation = Reconciliation(
        date=date(2026, 11, 10),
        store_code="11",
        store_name="HIPER",
        amounts=ReconciliationAmounts(net_sales=100000),
    )

    with pytest.raises(ValueError, match="Cash verification is required"):
        reconciliation.validate_for_submission()


def test_reconciliation_is_complete_with_cash_verification():
    reconciliation = Reconciliation(
        date=date(2026, 11, 10),
        store_code="11",
        store_name="HIPER",
        amounts=ReconciliationAmounts(net_sales=100000),
        cash_verification=CashVerification(matches_expected=True),
    )

    assert reconciliation.is_complete is True
    reconciliation.validate_for_submission()


def test_reconciliation_rejects_negative_expected_cash_confirmed_as_match():
    with pytest.raises(ValueError, match="cannot be confirmed as a match"):
        Reconciliation(
            date=date(2026, 11, 10),
            store_code="11",
            store_name="HIPER",
            amounts=ReconciliationAmounts(
                net_sales=10000,
                cards=20000,
            ),
            cash_verification=CashVerification(matches_expected=True),
        )


def test_reconciliation_allows_negative_expected_cash_with_discrepancy_note():
    reconciliation = Reconciliation(
        date=date(2026, 11, 10),
        store_code="11",
        store_name="HIPER",
        amounts=ReconciliationAmounts(
            net_sales=10000,
            cards=20000,
        ),
        cash_verification=CashVerification(
            matches_expected=False,
            discrepancy_note="Revisar ventas y medios de pago",
        ),
    )

    assert reconciliation.is_complete is True
    reconciliation.validate_for_submission()


def test_reconciliation_amounts_are_hashable():
    amounts = ReconciliationAmounts(
        net_sales=100000,
        field_notes={"net_sales": "Valor verificado"},
    )

    assert isinstance(hash(amounts), int)


def test_field_notes_remain_part_of_equality():
    first = ReconciliationAmounts(
        net_sales=100000,
        field_notes={"net_sales": "Nota A"},
    )
    second = ReconciliationAmounts(
        net_sales=100000,
        field_notes={"net_sales": "Nota B"},
    )

    assert first != second


from cuadre.models import MONETARY_FIELDS


@pytest.mark.parametrize("field", MONETARY_FIELDS)
def test_all_monetary_fields_reject_negative_values(field):
    with pytest.raises(ValueError):
        ReconciliationAmounts(**{field: -1})


def test_field_notes_reject_unknown_fields():
    with pytest.raises(ValueError):
        ReconciliationAmounts(
            field_notes={"unknown_field": "Invalid note"},
        )


def test_field_notes_copy_source_mapping():
    source_notes = {"net_sales": "POS"}

    amounts = ReconciliationAmounts(field_notes=source_notes)
    source_notes["net_sales"] = "Changed"

    assert amounts.field_notes["net_sales"] == "POS"
