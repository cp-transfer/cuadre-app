
from datetime import date
from unittest.mock import patch

import pytest

from cuadre.models import CashVerification, Reconciliation, ReconciliationAmounts
from cuadre.printing.system_printer import print_reconciliation


@pytest.fixture
def reconciliation():
    return Reconciliation(
        date=date(2026, 11, 18),
        store_code="05",
        store_name="LLUVIA",
        amounts=ReconciliationAmounts(net_sales=500000),
        cash_verification=CashVerification(matches_expected=True),
    )


def test_print_reconciliation_sends_pdf_to_lp(reconciliation):
    with patch("cuadre.printing.system_printer.subprocess.run") as run:
        run.return_value.returncode = 0
        run.return_value.stdout = "request id is printer-123"
        run.return_value.stderr = ""

        result = print_reconciliation(reconciliation)

    assert result == "request id is printer-123"
    run.assert_called_once()

    command = run.call_args.args[0]
    assert command[0] == "lp"
    assert command[1].endswith("conciliacion.pdf")


def test_print_reconciliation_handles_missing_lp(reconciliation):
    with patch(
        "cuadre.printing.system_printer.subprocess.run",
        side_effect=FileNotFoundError,
    ):
        with pytest.raises(RuntimeError, match="CUPS"):
            print_reconciliation(reconciliation)


def test_print_reconciliation_handles_lp_error(reconciliation):
    with patch("cuadre.printing.system_printer.subprocess.run") as run:
        run.return_value.returncode = 1
        run.return_value.stdout = ""
        run.return_value.stderr = "No default destination"

        with pytest.raises(RuntimeError, match="No default destination"):
            print_reconciliation(reconciliation)
