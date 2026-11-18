
"""Cash verification screen for a calculated reconciliation."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from cuadre.calculations import format_cop
from cuadre.validation import validate_cash_verification


class CashVerificationWidget(QWidget):
    """Display expected cash and collect the employee's confirmation."""

    completed = Signal(object)

    def __init__(
        self,
        expected_cash: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.expected_cash = expected_cash
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(18)

        title = QLabel("Verificación de efectivo")
        title.setObjectName("questionLabel")
        title.setAlignment(
            __import__("PySide6.QtCore", fromlist=["Qt"]).Qt.AlignmentFlag.AlignCenter
        )
        layout.addWidget(title)

        self.expected_label = QLabel(
            f"El efectivo en caja debe ser: {format_cop(self.expected_cash)}"
        )
        self.expected_label.setObjectName("expectedCash")
        self.expected_label.setWordWrap(True)
        self.expected_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        layout.addWidget(self.expected_label)

        self.warning_label = QLabel()
        self.warning_label.setObjectName("questionFeedback")
        self.warning_label.setWordWrap(True)
        self.warning_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        layout.addWidget(self.warning_label)

        self.choice_widget = QWidget()
        choice_layout = QHBoxLayout(self.choice_widget)
        choice_layout.setContentsMargins(0, 0, 0, 0)

        self.match_button = QPushButton("Sí, coincide")
        self.mismatch_button = QPushButton("No coincide")

        for button in (self.match_button, self.mismatch_button):
            button.setAutoDefault(False)
            button.setDefault(False)

        self.match_button.clicked.connect(self._confirm_match)
        self.mismatch_button.clicked.connect(self._show_discrepancy)

        choice_layout.addWidget(self.match_button)
        choice_layout.addWidget(self.mismatch_button)
        layout.addWidget(self.choice_widget)

        self.discrepancy_widget = QWidget()
        discrepancy_layout = QVBoxLayout(self.discrepancy_widget)
        discrepancy_layout.setContentsMargins(0, 0, 0, 0)

        self.discrepancy_label = QLabel(
            "Explique la diferencia encontrada:"
        )
        self.discrepancy_label.setWordWrap(True)
        discrepancy_layout.addWidget(self.discrepancy_label)

        self.discrepancy_input = QTextEdit()
        self.discrepancy_input.setPlaceholderText(
            "Describa el error o la diferencia..."
        )
        self.discrepancy_input.setMinimumHeight(110)
        discrepancy_layout.addWidget(self.discrepancy_input)

        self.submit_button = QPushButton("Confirmar diferencia")
        self.submit_button.setAutoDefault(False)
        self.submit_button.setDefault(False)
        self.submit_button.clicked.connect(self._confirm_mismatch)
        discrepancy_layout.addWidget(self.submit_button)

        self.discrepancy_widget.hide()
        layout.addWidget(self.discrepancy_widget)

        self.feedback_label = QLabel()
        self.feedback_label.setObjectName("questionFeedback")
        self.feedback_label.setWordWrap(True)
        layout.addWidget(self.feedback_label)

        layout.addStretch(1)

        if self.expected_cash < 0:
            self.warning_label.setText(
                "Error: el efectivo esperado es negativo. "
                "Revise los datos ingresados y explique la situación "
                "para continuar. El valor calculado no se modificará."
            )
            self.choice_widget.hide()
            self.discrepancy_widget.show()

    def _confirm_match(self) -> None:
        verification = validate_cash_verification(
            expected_cash=self.expected_cash,
            matches_expected=True,
        )
        self.completed.emit(verification)

    def _show_discrepancy(self) -> None:
        self.choice_widget.hide()
        self.discrepancy_widget.show()
        self.discrepancy_input.setFocus()

    def _confirm_mismatch(self) -> None:
        note = self.discrepancy_input.toPlainText().strip()

        if not note:
            self.feedback_label.setText(
                "Debe explicar la diferencia antes de continuar."
            )
            self.discrepancy_input.setFocus()
            return

        try:
            verification = validate_cash_verification(
                expected_cash=self.expected_cash,
                matches_expected=False,
                discrepancy_note=note,
            )
        except (TypeError, ValueError):
            self.feedback_label.setText(
                "No fue posible validar la explicación ingresada."
            )
            return

        self.completed.emit(verification)
