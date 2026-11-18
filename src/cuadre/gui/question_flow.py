
"""Single-question reconciliation data entry widget."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from cuadre.gui.questions import QUESTION_DEFINITIONS
from cuadre.validation import parse_money, parse_quantity


class QuestionFlow(QWidget):
    """Collect reconciliation values one question at a time."""

    completed = Signal(object, object, str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.values: dict[str, int] = {}
        self.field_notes: dict[str, str] = {}
        self.other_method_details = ""

        self._question_index = 0
        self._showing_other_method_details = False
        self._completed = False

        self._build_ui()
        self._show_current_step()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(18)

        self.instruction_label = QLabel(
            "Ingrese el valor. Deje vacío cuando no haya movimiento."
        )
        self.instruction_label.setObjectName("questionInstruction")
        self.instruction_label.setWordWrap(True)
        layout.addWidget(self.instruction_label)

        self.question_label = QLabel()
        self.question_label.setObjectName("questionLabel")
        self.question_label.setWordWrap(True)
        layout.addWidget(self.question_label)

        self.answer_input = QLineEdit()
        self.answer_input.setObjectName("answerInput")
        self.answer_input.setPlaceholderText("Ingrese el valor")
        self.answer_input.returnPressed.connect(self._accept_answer)
        layout.addWidget(self.answer_input)

        self.note_button = QPushButton("Agregar nota")
        self.note_button.setObjectName("noteButton")
        self.note_button.clicked.connect(self._edit_note)
        layout.addWidget(self.note_button, 0)

        self.feedback_label = QLabel()
        self.feedback_label.setObjectName("questionFeedback")
        self.feedback_label.setWordWrap(True)
        layout.addWidget(self.feedback_label)

        layout.addStretch(1)

    def _show_current_step(self) -> None:
        self.feedback_label.clear()
        self.answer_input.clear()

        if self._showing_other_method_details:
            self.instruction_label.setText(
                "Indique los medios de pago utilizados. Este dato es obligatorio."
            )
            self.question_label.setText(
                "¿Qué medios de pago se utilizaron?"
            )
            self.answer_input.setPlaceholderText("Describa los medios de pago")
            self.note_button.hide()
        elif self._question_index < len(QUESTION_DEFINITIONS):
            question = QUESTION_DEFINITIONS[self._question_index]

            self.instruction_label.setText(
                "Ingrese el valor. Deje vacío cuando no haya movimiento."
            )
            self.question_label.setText(question.label)
            self.answer_input.setPlaceholderText(
                "Ingrese un valor entero"
            )
            self.note_button.show()
            self._update_note_button(question.field_name)
        else:
            self._finish()

        self.answer_input.setFocus()

    def _accept_answer(self) -> None:
        if self._completed:
            return

        if self._showing_other_method_details:
            details = self.answer_input.text().strip()

            if not details:
                self.feedback_label.setText(
                    "Debe indicar los medios de pago utilizados."
                )
                self.answer_input.setFocus()
                return

            self.other_method_details = details
            self._showing_other_method_details = False
            self._question_index += 1
            self._show_current_step()
            return

        if self._question_index >= len(QUESTION_DEFINITIONS):
            return

        question = QUESTION_DEFINITIONS[self._question_index]
        raw_value = self.answer_input.text()

        try:
            if question.value_type == "quantity":
                value = parse_quantity(
                    raw_value,
                    field_name=question.label,
                )
            else:
                value = parse_money(raw_value)
        except (TypeError, ValueError):
            self.feedback_label.setText(
                "Ingrese un número entero válido y no negativo."
            )
            self.answer_input.setFocus()
            self.answer_input.selectAll()
            return

        self.values[question.field_name] = value

        if (
            question.field_name == "coupons_sold_other_method"
            and value > 0
        ):
            self._showing_other_method_details = True
        else:
            self._question_index += 1

        self._show_current_step()

    def _edit_note(self) -> None:
        if (
            self._completed
            or self._showing_other_method_details
            or self._question_index >= len(QUESTION_DEFINITIONS)
        ):
            return

        question = QUESTION_DEFINITIONS[self._question_index]

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Nota: {question.label}")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        instruction = QLabel(
            "Agregue una explicación si lo considera necesario."
        )
        instruction.setWordWrap(True)
        layout.addWidget(instruction)

        editor = QTextEdit()
        editor.setPlainText(
            self.field_notes.get(question.field_name, "")
        )
        editor.setMinimumHeight(120)
        layout.addWidget(editor)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            note = editor.toPlainText().strip()

            if note:
                self.field_notes[question.field_name] = note
            else:
                self.field_notes.pop(question.field_name, None)

            self._update_note_button(question.field_name)
            self.answer_input.setFocus()

    def _update_note_button(self, field_name: str) -> None:
        if self.field_notes.get(field_name):
            self.note_button.setText("Editar nota")
        else:
            self.note_button.setText("Agregar nota")

    def _finish(self) -> None:
        if self._completed:
            return

        self._completed = True
        self.instruction_label.setText("Captura de datos completada.")
        self.question_label.setText("Datos registrados correctamente.")
        self.answer_input.hide()
        self.note_button.hide()
        self.feedback_label.clear()

        self.completed.emit(
            self.values.copy(),
            self.field_notes.copy(),
            self.other_method_details,
        )
