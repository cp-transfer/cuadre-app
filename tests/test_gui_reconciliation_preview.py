
from datetime import date

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QLabel

from cuadre.gui.reconciliation_preview import ReconciliationPreview
from cuadre.models import (
    CashVerification,
    Reconciliation,
    ReconciliationAmounts,
)


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def make_reconciliation(
    amounts=None,
    verification=None,
):
    if amounts is None:
        amounts = ReconciliationAmounts(
            net_sales=500000,
            coupons_sold_other_method=20000,
            coupons_sold_other_method_details="Transferencia",
            bags=5,
            garments=12,
            field_notes={"net_sales": "Venta del día"},
        )

    if verification is None:
        verification = CashVerification(matches_expected=True)

    return Reconciliation(
        date=date(2026, 11, 18),
        store_code="05",
        store_name="LLUVIA",
        amounts=amounts,
        cash_verification=verification,
    )


def all_label_text(widget):
    return [label.text() for label in widget.findChildren(QLabel)]


def test_preview_displays_store_and_date(qapp):
    widget = ReconciliationPreview(make_reconciliation())

    texts = all_label_text(widget)

    assert any("05 · LLUVIA" in text for text in texts)
    assert "18/11/2026" in texts


def test_preview_displays_amounts_notes_and_other_income(qapp):
    widget = ReconciliationPreview(make_reconciliation())

    texts = all_label_text(widget)

    assert "Ventas netas" in texts
    assert "$500.000" in texts
    assert "Otros ingresos" in texts
    assert "$20.000 — Transferencia" in texts
    assert "Nota: Venta del día" in texts
    assert "Bolsas" in texts
    assert "5" in texts
    assert "Prendas" in texts
    assert "12" in texts


def test_preview_displays_cash_verification(qapp):
    widget = ReconciliationPreview(make_reconciliation())

    texts = all_label_text(widget)

    assert "Efectivo esperado" in texts
    assert "Verificación" in texts
    assert "El efectivo coincide con el valor esperado." in texts


def test_preview_displays_discrepancy_note(qapp):
    verification = CashVerification(
        matches_expected=False,
        discrepancy_note="Faltan $5.000 en caja.",
    )
    widget = ReconciliationPreview(
        make_reconciliation(verification=verification)
    )

    texts = all_label_text(widget)

    assert "El efectivo NO coincide con el valor esperado." in texts
    assert (
        "Nota: Explicación de la diferencia: Faltan $5.000 en caja."
        in texts
    )


def test_preview_requires_cash_verification(qapp):
    reconciliation = Reconciliation(
        date=date(2026, 11, 18),
        store_code="05",
        store_name="LLUVIA",
        amounts=ReconciliationAmounts(),
    )

    with pytest.raises(ValueError):
        ReconciliationPreview(reconciliation)

