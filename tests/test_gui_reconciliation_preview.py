
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

def test_print_archives_before_printing(qapp, monkeypatch):
    import cuadre.gui.reconciliation_preview as preview_module
    from cuadre.printing import system_printer

    events = []
    archive_path = "/downloads/Cuadre/Historial/test-archive"

    def fake_save(reconciliation, downloads_dir):
        events.append("archive")
        assert downloads_dir
        return archive_path

    def fake_print(reconciliation):
        events.append("print")
        return "Job sent"

    monkeypatch.setattr(preview_module, "save_submission", fake_save)
    monkeypatch.setattr(
        system_printer, "print_reconciliation", fake_print
    )
    monkeypatch.setattr(
        preview_module.QMessageBox, "information", lambda *args: None
    )

    widget = ReconciliationPreview(make_reconciliation())
    widget._print_reconciliation()

    assert events == ["archive", "print"]
    assert widget.print_button.isEnabled()


def test_print_does_not_print_if_archive_fails(qapp, monkeypatch):
    import cuadre.gui.reconciliation_preview as preview_module
    from cuadre.printing import system_printer

    def fail_save(*args):
        raise OSError("Disk error")

    def unexpected_print(*args):
        pytest.fail("Printing must not happen if archiving fails")

    monkeypatch.setattr(preview_module, "save_submission", fail_save)
    monkeypatch.setattr(
        system_printer, "print_reconciliation", unexpected_print
    )
    monkeypatch.setattr(
        preview_module.QMessageBox, "critical", lambda *args: None
    )

    widget = ReconciliationPreview(make_reconciliation())
    widget._print_reconciliation()

    assert widget.print_button.isEnabled()


def test_print_failure_preserves_archive(qapp, monkeypatch):
    import cuadre.gui.reconciliation_preview as preview_module
    from cuadre.printing import system_printer

    archive_path = "/downloads/Cuadre/Historial/test-archive"
    messages = []

    def fake_save(*args):
        return archive_path

    def fail_print(*args):
        raise RuntimeError("Printer unavailable")

    monkeypatch.setattr(preview_module, "save_submission", fake_save)
    monkeypatch.setattr(
        system_printer, "print_reconciliation", fail_print
    )
    monkeypatch.setattr(
        preview_module.QMessageBox,
        "critical",
        lambda *args: messages.append(args),
    )

    widget = ReconciliationPreview(make_reconciliation())
    widget._print_reconciliation()

    assert widget.print_button.isEnabled()
    assert archive_path in messages[0][2]
    assert "Printer unavailable" in messages[0][2]


def test_notify_continues_when_printing_fails(qapp, monkeypatch):
    from pathlib import Path

    import cuadre.gui.reconciliation_preview as preview_module
    import cuadre.ntfy as ntfy_module
    from cuadre.printing import system_printer

    archive_path = Path("/downloads/Cuadre/Historial/ntfy-test")
    events = []
    dialogs = []

    def fake_save(reconciliation, downloads_dir, submitted_at=None):
        events.append("archive")
        assert submitted_at is not None
        return archive_path

    def fake_print(pdf_path):
        events.append("print")
        assert Path(pdf_path) == archive_path / "report.pdf"
        raise RuntimeError("Printer unavailable")

    def fake_notify(title, message):
        events.append("notify")
        assert title.startswith("CP COMPANY")
        assert message.strip()
        return "Notification sent"

    monkeypatch.setattr(
        preview_module.QStandardPaths,
        "writableLocation",
        lambda *args: "/downloads",
    )
    monkeypatch.setattr(
        preview_module.QInputDialog,
        "getText",
        lambda *args: ("Test Employee", True),
    )
    monkeypatch.setattr(preview_module, "save_submission", fake_save)
    monkeypatch.setattr(
        system_printer,
        "print_reconciliation",
        fake_print,
    )
    monkeypatch.setattr(
        ntfy_module,
        "send_notification",
        fake_notify,
    )
    monkeypatch.setattr(
        preview_module.QMessageBox,
        "information",
        lambda *args: dialogs.append(args),
    )
    monkeypatch.setattr(
        preview_module.QMessageBox,
        "critical",
        lambda *args: dialogs.append(args),
    )

    widget = preview_module.ReconciliationPreview(make_reconciliation())
    widget._notify_reconciliation()

    assert events == ["archive", "print", "notify"]
    assert widget.notify_button.isEnabled()
    assert widget.print_button.isEnabled()
    assert len(dialogs) == 1
    assert "Notification sent" in dialogs[0][2]
    assert "Printer unavailable" in dialogs[0][2]
    assert str(archive_path) in dialogs[0][2]
