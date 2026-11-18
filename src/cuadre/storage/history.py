
"""Local submission archive storage."""

import json
import os
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from cuadre.calculations import calculate_expected_cash
from cuadre.models import ALL_FIELDS, Reconciliation
from cuadre.reporting.pdf_report import generate_reconciliation_pdf


def _safe_name(value: str) -> str:
    """Return a filesystem-safe name component."""
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    return cleaned.strip("_") or "unknown"


def _build_metadata(
    reconciliation: Reconciliation,
    submission_id: str,
    submitted_at: datetime,
) -> dict:
    """Serialize a complete reconciliation submission."""

    amounts = reconciliation.amounts
    verification = reconciliation.cash_verification

    return {
        "schema_version": 1,
        "submission_id": submission_id,
        "submitted_at": submitted_at.isoformat(),
        "store": {
            "code": reconciliation.store_code,
            "name": reconciliation.store_name,
        },
        "business_date": reconciliation.date.isoformat(),
        "employee_name": reconciliation.employee_name,
        "amounts": {
            **{
                field_name: getattr(amounts, field_name)
                for field_name in ALL_FIELDS
            },
            "coupons_sold_other_method_details": (
                amounts.coupons_sold_other_method_details
            ),
            "field_notes": dict(amounts.field_notes),
        },
        "expected_cash": calculate_expected_cash(amounts),
        "cash_verification": {
            "matches_expected": verification.matches_expected,
            "discrepancy_note": verification.discrepancy_note,
        },
    }


def save_submission(
    reconciliation: Reconciliation,
    downloads_dir: str | Path,
    submitted_at: datetime | None = None,
) -> Path:
    """Save a complete submission under Downloads/Cuadre/Historial.

    Returns the final submission archive directory.
    """

    if not isinstance(reconciliation, Reconciliation):
        raise TypeError("reconciliation must be a Reconciliation instance.")

    reconciliation.validate_for_submission()

    if submitted_at is None:
        submitted_at = datetime.now().astimezone()

    if not isinstance(submitted_at, datetime):
        raise TypeError("submitted_at must be a datetime.")

    if submitted_at.tzinfo is None or submitted_at.utcoffset() is None:
        raise ValueError("submitted_at must be timezone-aware.")

    downloads_dir = Path(downloads_dir).expanduser()
    history_dir = downloads_dir / "Cuadre" / "Historial"
    history_dir.mkdir(parents=True, exist_ok=True)

    submission_id = str(uuid4())
    timestamp = submitted_at.astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    store_code = _safe_name(reconciliation.store_code)

    archive_name = (
        f"{timestamp}_{store_code}_{submission_id}"
    )
    archive_path = history_dir / archive_name

    temporary_dir = Path(
        tempfile.mkdtemp(prefix=".pending-", dir=history_dir)
    )

    try:
        pdf_path = temporary_dir / "report.pdf"
        generate_reconciliation_pdf(reconciliation, pdf_path)

        metadata = _build_metadata(
            reconciliation,
            submission_id,
            submitted_at,
        )

        metadata_path = temporary_dir / "metadata.json"

        with metadata_path.open("w", encoding="utf-8") as file:
            json.dump(
                metadata,
                file,
                ensure_ascii=False,
                indent=2,
            )
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())

        # Publish the complete archive only after both files exist.
        os.rename(temporary_dir, archive_path)

    except Exception:
        shutil.rmtree(temporary_dir, ignore_errors=True)
        raise

    return archive_path
