
import pytest
from PySide6.QtWidgets import QApplication

from cuadre.gui.question_flow import QuestionFlow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_invalid_answer_does_not_advance(qapp):
    flow = QuestionFlow()

    flow.answer_input.setText("abc")
    flow._accept_answer()

    assert flow._question_index == 0
    assert "número entero válido" in flow.feedback_label.text()


def test_valid_answer_advances_to_next_question(qapp):
    flow = QuestionFlow()

    flow.answer_input.setText("125000")
    flow._accept_answer()

    assert flow.values["net_sales"] == 125000
    assert flow._question_index == 1
    assert flow.question_label.text() == "Bonos vendidos en efectivo"


def test_other_method_details_are_mandatory(qapp):
    flow = QuestionFlow()

    # Advance through the first two questions.
    flow.answer_input.setText("100000")
    flow._accept_answer()
    flow.answer_input.setText("0")
    flow._accept_answer()

    # A positive amount activates the conditional question.
    flow.answer_input.setText("25000")
    flow._accept_answer()

    assert flow._showing_other_method_details
    assert flow.question_label.text() == "¿Qué medios de pago se utilizaron?"

    # Empty details must not advance.
    flow.answer_input.setText("")
    flow._accept_answer()

    assert flow._showing_other_method_details

    # Valid details allow the flow to continue.
    flow.answer_input.setText("Transferencia")
    flow._accept_answer()

    assert flow.other_method_details == "Transferencia"
    assert not flow._showing_other_method_details
    assert flow.question_label.text() == "Bonos redimidos"


def test_completion_emits_all_collected_data(qapp):
    flow = QuestionFlow()
    received = []
    flow.completed.connect(
        lambda values, notes, details: received.append(
            (values, notes, details)
        )
    )

    for _ in range(13):
        flow.answer_input.setText("")
        flow._accept_answer()

    assert flow._completed
    assert len(received) == 1

    values, notes, details = received[0]
    assert len(values) == 13
    assert all(value == 0 for value in values.values())
    assert notes == {}
    assert details == ""
