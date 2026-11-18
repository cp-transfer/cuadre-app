
import pytest
from PySide6.QtWidgets import QApplication

from cuadre.gui.cash_verification import CashVerificationWidget


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_expected_cash_is_displayed(qapp):
    widget = CashVerificationWidget(125000)

    assert "$125.000" in widget.expected_label.text()


def test_employee_can_confirm_matching_cash(qapp):
    widget = CashVerificationWidget(125000)
    received = []
    widget.completed.connect(received.append)

    widget.match_button.click()

    assert len(received) == 1
    assert received[0].matches_expected is True


def test_mismatch_requires_explanation(qapp):
    widget = CashVerificationWidget(125000)
    received = []
    widget.completed.connect(received.append)

    widget.mismatch_button.click()
    widget.submit_button.click()

    assert received == []
    assert "Debe explicar" in widget.feedback_label.text()

    widget.discrepancy_input.setPlainText("Faltan $5.000 en caja.")
    widget.submit_button.click()

    assert len(received) == 1
    assert received[0].matches_expected is False
    assert received[0].discrepancy_note == "Faltan $5.000 en caja."


def test_negative_expected_cash_requires_explanation(qapp):
    widget = CashVerificationWidget(-25000)
    received = []
    widget.completed.connect(received.append)

    assert widget.choice_widget.isHidden()
    assert not widget.discrepancy_widget.isHidden()
    assert "-$25.000" in widget.expected_label.text()

    widget.discrepancy_input.setPlainText(
        "Se debe revisar el registro de gastos."
    )
    widget.submit_button.click()

    assert len(received) == 1
    assert received[0].matches_expected is False
    assert received[0].discrepancy_note == (
        "Se debe revisar el registro de gastos."
    )

