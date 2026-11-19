
"""Read-only reconciliation preview widget."""

from PySide6.QtCore import Qt, QStandardPaths
from cuadre.storage.history import save_submission
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QPushButton,
)

from cuadre.calculations import calculate_expected_cash, format_cop
from cuadre.gui.questions import QUESTION_DEFINITIONS
from cuadre.models import Reconciliation


class ReconciliationPreview(QWidget):
    """Display a completed reconciliation for employee inspection."""

    def __init__(
        self,
        reconciliation: Reconciliation,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        if not reconciliation.is_complete:
            raise ValueError(
                "Cash verification is required for reconciliation preview."
            )

        self.reconciliation = reconciliation
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Vista previa de conciliación")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("screenTitle")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(10)

        self._add_section_title(content_layout, "Información de la tienda")

        reconciliation = self.reconciliation

        self._add_row(
            content_layout,
            "Tienda",
            f"{reconciliation.store_code} · {reconciliation.store_name}",
        )
        self._add_row(
            content_layout,
            "Fecha",
            reconciliation.date.strftime("%d/%m/%Y"),
        )

        if reconciliation.employee_name:
            self._add_row(
                content_layout,
                "Empleado",
                reconciliation.employee_name,
            )

        self._add_section_title(content_layout, "Detalle de la conciliación")

        amounts = reconciliation.amounts

        for question in QUESTION_DEFINITIONS:
            field_name = question.field_name
            value = getattr(amounts, field_name)

            if field_name == "coupons_sold_other_method":
                details = amounts.coupons_sold_other_method_details
                self._add_row(
                    content_layout,
                    "Otros ingresos",
                    f"{format_cop(value)} — {details}",
                )
            elif question.value_type == "money":
                self._add_row(
                    content_layout,
                    question.label,
                    format_cop(value),
                )
            else:
                self._add_row(
                    content_layout,
                    question.label,
                    str(value),
                )

            note = amounts.field_notes.get(field_name, "")
            if note:
                self._add_note(content_layout, note)

        self._add_section_title(content_layout, "Verificación de efectivo")

        expected_cash = calculate_expected_cash(amounts)
        self._add_row(
            content_layout,
            "Efectivo esperado",
            format_cop(expected_cash),
        )

        verification = reconciliation.cash_verification

        if verification.matches_expected:
            self._add_row(
                content_layout,
                "Verificación",
                "El efectivo coincide con el valor esperado.",
            )
        else:
            self._add_row(
                content_layout,
                "Verificación",
                "El efectivo NO coincide con el valor esperado.",
            )
            self._add_note(
                content_layout,
                f"Explicación de la diferencia: "
                f"{verification.discrepancy_note}",
            )

        content_layout.addStretch(1)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        self.print_button = QPushButton("Imprimir")
        self.print_button.clicked.connect(self._print_reconciliation)
        layout.addWidget(self.print_button)

    def _print_reconciliation(self) -> None:
        from cuadre.printing.system_printer import print_reconciliation

        self.print_button.setEnabled(False)

        try:
            try:
                downloads_dir = QStandardPaths.writableLocation(
                    QStandardPaths.StandardLocation.DownloadLocation
                )

                if not downloads_dir:
                    raise RuntimeError(
                        "No fue posible localizar la carpeta de Descargas."
                    )

                archive_path = save_submission(
                    self.reconciliation,
                    downloads_dir,
                )

            except (RuntimeError, ValueError, OSError) as error:
                QMessageBox.critical(
                    self,
                    "Error al guardar el historial",
                    str(error),
                )
                return

            try:
                result = print_reconciliation(self.reconciliation)

            except (RuntimeError, ValueError, OSError) as error:
                QMessageBox.critical(
                    self,
                    "Error de impresión",
                    f"El historial se guardó correctamente en:\n"
                    f"{archive_path}\n\n"
                    f"Pero no fue posible imprimir:\n{error}",
                )

            else:
                QMessageBox.information(
                    self,
                    "Impresión",
                    f"El documento se envió a la cola de impresión.\n\n"
                    f"Historial guardado en:\n{archive_path}\n\n"
                    f"{result}",
                )

        finally:
            self.print_button.setEnabled(True)

    @staticmethod
    def _add_section_title(layout: QVBoxLayout, text: str) -> None:
        label = QLabel(text)
        label.setObjectName("screenTitle")
        layout.addWidget(label)

    @staticmethod
    def _add_row(
        layout: QVBoxLayout,
        label_text: str,
        value_text: str,
    ) -> None:
        row = QFrame()
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(10, 6, 10, 6)
        row_layout.setSpacing(2)

        label = QLabel(label_text)
        value = QLabel(value_text)
        value.setWordWrap(True)

        row_layout.addWidget(label)
        row_layout.addWidget(value)
        layout.addWidget(row)

    @staticmethod
    def _add_note(layout: QVBoxLayout, note: str) -> None:
        label = QLabel(f"Nota: {note}")
        label.setWordWrap(True)
        label.setObjectName("metadata")
        layout.addWidget(label)
