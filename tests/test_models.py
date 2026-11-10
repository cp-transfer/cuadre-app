
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
