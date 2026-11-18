
import json
from datetime import date, datetime, timezone

import pytest

from cuadre.models import (
    CashVerification,
    Reconciliation,
    ReconciliationAmounts,
)
from cuadre.storage.history import save_submission


@pytest.fixture
def reconciliation():
    amounts = ReconciliationAmounts(
        net_sales=150000,
        cards=20000,
        qr=10000,
        coupons_sold_cash=5000,
        coupons_sold_other_method=15000,
        coupons_sold_other_method_details="Transferencia",
        expenses=3000,
        bags=12,
        garments=8,
        garments_exchange=2,
        field_notes={
            "net_sales": "Venta del día",
            "bags": "Conteo confirmado",
        },
    )

    return Reconciliation(
        date=date(2026, 11, 18),
        store_code="05",
        store_name="LLUVIA",
        amounts=amounts,
        cash_verification=CashVerification(
            matches_expected=False,
            discrepancy_note="Faltaron 2.000 pesos.",
        ),
        employee_name="Empleado de prueba",
    )


def test_save_submission_creates_complete_archive(
    tmp_path,
    reconciliation,
):
    submitted_at = datetime(
        2026, 11, 18, 16, 30, 0, tzinfo=timezone.utc
    )

    archive = save_submission(
        reconciliation,
        tmp_path / "Downloads",
        submitted_at=submitted_at,
    )

    assert archive.is_dir()
    assert (archive / "report.pdf").is_file()
    assert (archive / "metadata.json").is_file()

    metadata = json.loads(
        (archive / "metadata.json").read_text(encoding="utf-8")
    )

    assert metadata["schema_version"] == 1
    assert metadata["submitted_at"] == submitted_at.isoformat()
    assert metadata["store"] == {
        "code": "05",
        "name": "LLUVIA",
    }
    assert metadata["business_date"] == "2026-11-18"
    assert metadata["employee_name"] == "Empleado de prueba"

    assert metadata["amounts"]["net_sales"] == 150000
    assert metadata["amounts"]["bags"] == 12
    assert (
        metadata["amounts"]["coupons_sold_other_method_details"]
        == "Transferencia"
    )
    assert metadata["amounts"]["field_notes"]["net_sales"] == (
        "Venta del día"
    )

    assert metadata["cash_verification"] == {
        "matches_expected": False,
        "discrepancy_note": "Faltaron 2.000 pesos.",
    }

    assert metadata["submission_id"] in archive.name


def test_multiple_submissions_create_separate_archives(
    tmp_path,
    reconciliation,
):
    downloads = tmp_path / "Downloads"
    submitted_at = datetime(
        2026, 11, 18, 16, 30, 0, tzinfo=timezone.utc
    )

    first = save_submission(
        reconciliation,
        downloads,
        submitted_at=submitted_at,
    )
    second = save_submission(
        reconciliation,
        downloads,
        submitted_at=submitted_at,
    )

    assert first != second
    assert first.is_dir()
    assert second.is_dir()

    first_metadata = json.loads(
        (first / "metadata.json").read_text(encoding="utf-8")
    )
    second_metadata = json.loads(
        (second / "metadata.json").read_text(encoding="utf-8")
    )

    assert first_metadata["submission_id"] != (
        second_metadata["submission_id"]
    )


def test_incomplete_reconciliation_cannot_be_saved(tmp_path):
    reconciliation = Reconciliation(
        date=date(2026, 11, 18),
        store_code="05",
        store_name="LLUVIA",
        amounts=ReconciliationAmounts(),
    )

    with pytest.raises(ValueError, match="Cash verification"):
        save_submission(reconciliation, tmp_path / "Downloads")

    assert not (tmp_path / "Downloads" / "Cuadre" / "Historial").exists()


def test_naive_submission_timestamp_is_rejected(
    tmp_path,
    reconciliation,
):
    submitted_at = datetime(2026, 11, 18, 16, 30, 0)

    with pytest.raises(ValueError, match="timezone-aware"):
        save_submission(
            reconciliation,
            tmp_path / "Downloads",
            submitted_at=submitted_at,
        )


def test_failed_pdf_generation_does_not_publish_archive(
    tmp_path,
    reconciliation,
    monkeypatch,
):
    import cuadre.storage.history as history

    def fail_pdf(*args, **kwargs):
        raise RuntimeError("PDF generation failed")

    monkeypatch.setattr(history, "generate_reconciliation_pdf", fail_pdf)

    downloads = tmp_path / "Downloads"

    with pytest.raises(RuntimeError, match="PDF generation failed"):
        history.save_submission(reconciliation, downloads)

    history_dir = downloads / "Cuadre" / "Historial"

    assert not list(history_dir.glob("*"))
