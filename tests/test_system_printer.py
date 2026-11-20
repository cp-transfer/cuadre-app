from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import cuadre.printing.system_printer as system_printer
from cuadre.printing.system_printer import print_reconciliation


def make_pdf(tmp_path):
    pdf_path = tmp_path / "report.pdf"
    pdf_path.write_bytes(b"%PDF-test")
    return pdf_path


def test_print_reconciliation_sends_pdf_to_lp(tmp_path, monkeypatch):
    pdf_path = make_pdf(tmp_path)
    monkeypatch.setattr(system_printer.sys, "platform", "linux")

    with patch("cuadre.printing.system_printer.subprocess.run") as run:
        run.return_value.returncode = 0
        run.return_value.stdout = "request id is printer-123"
        run.return_value.stderr = ""

        result = print_reconciliation(pdf_path)

    assert result == "request id is printer-123"
    run.assert_called_once_with(
        ["lp", str(pdf_path)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_print_reconciliation_handles_missing_lp(tmp_path, monkeypatch):
    pdf_path = make_pdf(tmp_path)
    monkeypatch.setattr(system_printer.sys, "platform", "linux")

    with patch(
        "cuadre.printing.system_printer.subprocess.run",
        side_effect=FileNotFoundError,
    ):
        with pytest.raises(RuntimeError, match="CUPS"):
            print_reconciliation(pdf_path)


def test_print_reconciliation_handles_lp_error(tmp_path, monkeypatch):
    pdf_path = make_pdf(tmp_path)
    monkeypatch.setattr(system_printer.sys, "platform", "linux")

    with patch("cuadre.printing.system_printer.subprocess.run") as run:
        run.return_value.returncode = 1
        run.return_value.stdout = ""
        run.return_value.stderr = "No default destination"

        with pytest.raises(RuntimeError, match="No default destination"):
            print_reconciliation(pdf_path)


def test_print_reconciliation_rejects_missing_pdf(tmp_path):
    with pytest.raises(FileNotFoundError, match="No existe"):
        print_reconciliation(tmp_path / "missing.pdf")


def test_windows_print_uses_registered_pdf_application(tmp_path, monkeypatch):
    pdf_path = make_pdf(tmp_path)
    monkeypatch.setattr(system_printer.sys, "platform", "win32")

    calls = []

    def shell_execute(*args):
        calls.append(args)
        return 33

    shell32 = SimpleNamespace(ShellExecuteW=shell_execute)
    monkeypatch.setattr(
        system_printer.ctypes,
        "WinDLL",
        lambda *args, **kwargs: shell32,
        raising=False,
    )

    result = print_reconciliation(pdf_path)

    assert "Solicitud de impresión" in result
    assert calls == [
        (None, "print", str(pdf_path), None, None, 0)
    ]


def test_windows_print_reports_shell_execute_error(tmp_path, monkeypatch):
    pdf_path = make_pdf(tmp_path)
    monkeypatch.setattr(system_printer.sys, "platform", "win32")

    def shell_execute(*args):
        return 31

    shell32 = SimpleNamespace(ShellExecuteW=shell_execute)
    monkeypatch.setattr(
        system_printer.ctypes,
        "WinDLL",
        lambda *args, **kwargs: shell32,
        raising=False,
    )

    with pytest.raises(RuntimeError, match="ShellExecute: 31"):
        print_reconciliation(pdf_path)
