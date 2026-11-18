
from datetime import date

import pytest

from cuadre.models import (
    CashVerification,
    Reconciliation,
    ReconciliationAmounts,
)
from cuadre.reporting.pdf_report import (
    build_report_sections,
    generate_reconciliation_pdf,
)


@pytest.fixture
def reconciliation():
    amounts = ReconciliationAmounts(
        net_sales=500000,
        coupons_sold_cash=100000,
        coupons_sold_other_method=50000,
        coupons_sold_other_method_details="Transferencia",
        coupons_redeemed=20000,
        qr=100000,
        cards=100000,
        sistecredito=80000,
        addi=50000,
        expenses=30000,
        sistecredito_collections=10000,
        bags=5,
        garments=20,
        garments_exchange=2,
        field_notes={
            "net_sales": "Venta del día",
            "qr": "Pago confirmado",
        },
    )

    return Reconciliation(
        date=date(2026, 11, 18),
        store_code="05",
        store_name="LLUVIA",
        amounts=amounts,
        cash_verification=CashVerification(matches_expected=True),
    )


def test_report_sections_contain_all_required_data(reconciliation):
    sections = build_report_sections(reconciliation)

    all_entries = [
        entry
        for _, entries in sections
        for entry in entries
    ]

    assert ("Tienda", "05 · LLUVIA") in all_entries
    assert ("Fecha", "18/11/2026") in all_entries
    assert ("Ventas netas", "$500.000") in all_entries
    assert ("Bonos vendidos en efectivo", "$100.000") in all_entries
    assert ("Otros ingresos", "$50.000 (Transferencia)") in all_entries
    assert ("Bonos redimidos", "$20.000") in all_entries
    assert ("QR", "$100.000") in all_entries
    assert ("Tarjeta", "$100.000") in all_entries
    assert ("Sistecrédito", "$80.000") in all_entries
    assert ("Addi", "$50.000") in all_entries
    assert ("Gastos", "$30.000") in all_entries
    assert ("Recaudo Sistecrédito", "$10.000") in all_entries
    assert ("Bolsas", "5") in all_entries
    assert ("Prendas", "20") in all_entries
    assert ("Prendas por canje", "2") in all_entries
    assert ("Verificación", "OK") in all_entries


def test_other_income_appears_only_once(reconciliation):
    sections = build_report_sections(reconciliation)

    all_entries = [
        entry
        for _, entries in sections
        for entry in entries
    ]

    assert sum(
        1 for label, _ in all_entries if label == "Otros ingresos"
    ) == 1


def test_report_contains_notes(reconciliation):
    sections = build_report_sections(reconciliation)

    notes = dict(
        entry
        for title, entries in sections
        if title == "NOTAS"
        for entry in entries
    )

    assert notes["Ventas netas"] == "Venta del día"
    assert notes["QR"] == "Pago confirmado"


def test_pdf_is_generated(reconciliation, tmp_path):
    output = tmp_path / "conciliacion.pdf"

    result = generate_reconciliation_pdf(reconciliation, output)

    assert result == output
    assert output.exists()
    assert output.read_bytes().startswith(b"%PDF")


def test_report_requires_cash_verification():
    reconciliation = Reconciliation(
        date=date(2026, 11, 18),
        store_code="05",
        store_name="LLUVIA",
        amounts=ReconciliationAmounts(),
    )

    with pytest.raises(ValueError):
        build_report_sections(reconciliation)


def test_discrepancy_note_is_in_report(reconciliation):
    amounts = reconciliation.amounts

    incomplete = Reconciliation(
        date=reconciliation.date,
        store_code=reconciliation.store_code,
        store_name=reconciliation.store_name,
        amounts=amounts,
        cash_verification=CashVerification(
            matches_expected=False,
            discrepancy_note="Faltan $5.000.",
        ),
    )

    sections = build_report_sections(incomplete)

    notes = dict(
        entry
        for title, entries in sections
        if title == "NOTAS"
        for entry in entries
    )

    assert notes["Diferencia de efectivo"] == "Faltan $5.000."
    assert ("Verificación", "NO COINCIDE") in [
        entry for _, entries in sections for entry in entries
    ]
