"""Main application shell for the Cuadre GUI (Phase 3.1)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import sys

from cuadre.calculations import calculate_expected_cash
from cuadre.gui.reconciliation_preview import ReconciliationPreview
from cuadre.gui.cash_verification import CashVerificationWidget
from cuadre.models import Reconciliation
from cuadre.validation import build_reconciliation_amounts
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from cuadre.gui.scaling import (
    DEFAULT_ZOOM,
    MAX_ZOOM,
    MIN_ZOOM,
    ZOOM_STEP,
    clamp_zoom,
    scaled,
)
from cuadre.gui.styles import build_stylesheet
from cuadre.store_config import (
    StoreConfigError,
    load_store_identity,
    save_store_identity,
)
from cuadre.gui.question_flow import QuestionFlow
from cuadre.update_worker import UpdateTaskResult, UpdateWorker


class MainWindow(QMainWindow):
    """Persistent application shell; workflow screens are added in later milestones."""

    def __init__(self, store_code: str, store_name: str) -> None:
        super().__init__()
        self.store_code = store_code
        self.store_name = store_name
        self.zoom = DEFAULT_ZOOM
        self.reconciliation_values = None
        self.reconciliation_notes = None
        self.other_method_details = ""
        self.reconciliation_amounts = None
        self.expected_cash = None
        self.reconciliation = None
        self.cash_verification_widget = None
        self.preview_widget = None

        self.setWindowTitle("Cuadre · C.P. COMPANY")
        self.resize(1180, 780)
        self.setMinimumSize(960, 640)
        self._build_menu()
        self._build_ui()
        self._apply_zoom()

    def _build_menu(self) -> None:
        settings_menu = self.menuBar().addMenu("Configuración")
        change_store = QAction("Cambiar tienda", self)
        change_store.triggered.connect(self._change_store)
        settings_menu.addAction(change_store)

        settings_menu.addSeparator()
        self.update_action = QAction("Buscar actualizaciones", self)
        self.update_action.triggered.connect(self._check_for_updates)
        settings_menu.addAction(self.update_action)

    def _build_ui(self) -> None:
        root = QWidget(self)
        root_layout = QVBoxLayout(root)
        self.root_layout = root_layout
        root_layout.setContentsMargins(24, 20, 24, 20)
        root_layout.setSpacing(16)

        header = QFrame()
        header.setObjectName("header")
        header_layout = QVBoxLayout(header)
        self.header_layout = header_layout
        header_layout.setContentsMargins(20, 16, 20, 16)
        header_layout.setSpacing(7)

        self.brand_label = QLabel()
        self.brand_label.setObjectName("brandPlaceholder")
        self.brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_logo = Path(__file__).resolve().parents[1] / "assets" / "logos" / "logo_header.png"
        if header_logo.is_file():
            pixmap = QPixmap(str(header_logo))
            if not pixmap.isNull():
                self.brand_label.setPixmap(
                    pixmap.scaled(
                        200,
                        80,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
        else:
            self.brand_label.setText("C.P. COMPANY")

        header_layout.addWidget(self.brand_label)

        self.store_label = QLabel()
        self.store_label.setObjectName("storeLine")
        self.store_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.store_label)

        self.screen_title = QLabel("Reporte cuadre de caja")
        self.screen_title.setObjectName("screenTitle")
        self.screen_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.screen_title)

        metadata_row = QHBoxLayout()
        metadata_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label = QLabel()
        self.time_label = QLabel()
        self.employee_label = QLabel("Nombre: —")
        for label in (self.date_label, self.time_label, self.employee_label):
            label.setObjectName("metadata")
            metadata_row.addWidget(label)
        header_layout.addLayout(metadata_row)
        root_layout.addWidget(header)

        content = QFrame()
        content.setObjectName("contentSurface")
        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content_layout = QVBoxLayout(content)
        self.content_layout = content_layout
        content_layout.setContentsMargins(28, 28, 28, 28)
        self.question_flow = QuestionFlow(content)
        self.question_flow.completed.connect(self._on_questions_completed)
        content_layout.addWidget(self.question_flow)
        root_layout.addWidget(content, 1)

        footer_frame = QFrame ()
        footer_frame.setObjectName("footer")

        footer = QGridLayout(footer_frame)
        self.footer_layout = footer
        footer.setContentsMargins(16, 8, 16, 8)
        footer.setColumnStretch(0, 1)
        footer.setColumnStretch(2, 1)

        footer_center = QWidget()
        footer_center.setObjectName("footerCenter")
        footer_center_layout = QVBoxLayout(footer_center)
        footer_center_layout.setContentsMargins(0, 0, 0, 0)
        footer_center_layout.setSpacing(2)

        self.footer_logo_label = QLabel()
        self.footer_logo_label.setObjectName("footerLogo")
        self.footer_logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_logo = Path(__file__).resolve().parents[1] / "assets" / "logos" / "logo_w_footer.png"
        if footer_logo.is_file():
            pixmap = QPixmap(str(footer_logo))
            if not pixmap.isNull():
                self.footer_logo_label.setPixmap(
                    pixmap.scaledToWidth(
                        200,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
        footer_center_layout.addWidget(self.footer_logo_label)

        self.footer_text_label = QLabel(
            "C . P .  C O M P A N Y - 1 9 8 5"
        )
        self.footer_text_label.setObjectName("footerText")
        self.footer_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_center_layout.addWidget(self.footer_text_label)

        footer.addWidget(
            footer_center,
            0,
            1,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        zoom_controls = QWidget()
        zoom_controls.setObjectName("zoomControls")
        zoom_controls_layout = QHBoxLayout(zoom_controls)
        zoom_controls_layout.setContentsMargins(0, 0, 0, 0)
        zoom_controls_layout.setSpacing(8)

        self.zoom_out_button = QPushButton("−")
        self.zoom_out_button.setToolTip("Reducir tamaño de interfaz")
        self.zoom_out_button.clicked.connect(
            lambda: self._set_zoom(self.zoom - ZOOM_STEP)
        )
        self.zoom_label = QLabel("100 %")
        self.zoom_label.setObjectName("zoomLabel")
        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.setToolTip("Aumentar tamaño de interfaz")
        self.zoom_in_button.clicked.connect(
            lambda: self._set_zoom(self.zoom + ZOOM_STEP)
        )

        zoom_controls_layout.addWidget(self.zoom_out_button)
        zoom_controls_layout.addWidget(self.zoom_label)
        zoom_controls_layout.addWidget(self.zoom_in_button)
        footer.addWidget(
            zoom_controls,
            0,
            2,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )

        root_layout.addWidget(footer_frame)

        self.setCentralWidget(root)
        self._refresh_header_metadata()

    def _refresh_header_metadata(self) -> None:
        now = datetime.now().astimezone()
        self.store_label.setText(
            f"C.P. COMPANY  ·  {self.store_code}  ·  {self.store_name}"
        )
        self.date_label.setText(now.strftime("Fecha: %d/%m/%Y"))
        self.time_label.setText(now.strftime("Hora: %H:%M"))

    def _on_questions_completed(
        self,
        values: dict[str, int],
        notes: dict[str, str],
        other_method_details: str,
    ) -> None:
        self.reconciliation_values = values
        self.reconciliation_notes = notes
        self.other_method_details = other_method_details

        try:
            self.reconciliation_amounts = build_reconciliation_amounts(
                raw_values=values,
                field_notes=notes,
                coupons_sold_other_method_details=other_method_details,
            )
            self.expected_cash = calculate_expected_cash(
                self.reconciliation_amounts
            )
        except (TypeError, ValueError) as error:
            QMessageBox.critical(
                self,
                "Error en los datos",
                f"No fue posible preparar la conciliación: {error}",
            )
            return

        self.question_flow.hide()
        self.content_layout.removeWidget(self.question_flow)
        self.question_flow.deleteLater()

        self.cash_verification_widget = CashVerificationWidget(
            self.expected_cash,
            self,
        )
        self.cash_verification_widget.completed.connect(
            self._on_cash_verification_completed
        )
        self.content_layout.addWidget(self.cash_verification_widget)

    def _on_cash_verification_completed(self, verification) -> None:
        self.reconciliation = Reconciliation(
            date=datetime.now().astimezone().date(),
            store_code=self.store_code,
            store_name=self.store_name,
            amounts=self.reconciliation_amounts,
            cash_verification=verification,
        )

        self.cash_verification_widget.hide()
        self.content_layout.removeWidget(self.cash_verification_widget)
        self.cash_verification_widget.deleteLater()

        self.preview_widget = ReconciliationPreview(
            self.reconciliation,
            self,
        )
        self.content_layout.addWidget(self.preview_widget)

    def _set_zoom(self, value: int) -> None:
        self.zoom = clamp_zoom(value)
        self._apply_zoom()

    def _apply_zoom(self) -> None:
        self.setStyleSheet(build_stylesheet(self.zoom))
        self.root_layout.setContentsMargins(
            scaled(24, self.zoom), scaled(20, self.zoom),
            scaled(24, self.zoom), scaled(20, self.zoom),
        )
        self.root_layout.setSpacing(scaled(16, self.zoom))
        self.header_layout.setContentsMargins(
            scaled(20, self.zoom), scaled(16, self.zoom),
            scaled(20, self.zoom), scaled(16, self.zoom),
        )
        self.header_layout.setSpacing(scaled(7, self.zoom))
        self.content_layout.setContentsMargins(
            scaled(28, self.zoom), scaled(28, self.zoom),
            scaled(28, self.zoom), scaled(28, self.zoom),
        )
        self.footer_layout.setSpacing(scaled(8, self.zoom))
        self.zoom_label.setText(f"{self.zoom} %")
        self.zoom_out_button.setEnabled(self.zoom > MIN_ZOOM)
        self.zoom_in_button.setEnabled(self.zoom < MAX_ZOOM)

    def _check_for_updates(self) -> None:
        self.update_action.setEnabled(False)
        self.update_action.setText("Buscando actualizaciones…")

        self._update_worker = UpdateWorker(self)
        self._update_worker.completed.connect(self._update_check_completed)
        self._update_worker.failed.connect(self._update_check_failed)
        self._update_worker.start()

    def _update_check_failed(self, message: str) -> None:
        self.update_action.setEnabled(True)
        self.update_action.setText("Buscar actualizaciones")
        QMessageBox.warning(
            self,
            "Actualizaciones de Cuadre",
            message,
        )

    def _update_check_completed(self, result: UpdateTaskResult) -> None:
        self.update_action.setEnabled(True)
        self.update_action.setText("Buscar actualizaciones")

        update = result.update

        if not update.available:
            QMessageBox.information(
                self,
                "Cuadre actualizado",
                f"Ya tienes instalada la última versión "
                f"({update.installed_version}).",
            )
            return

        answer = QMessageBox.question(
            self,
            "Actualización disponible",
            f"Está disponible la versión {update.latest_version}.\n\n"
            "¿Deseas instalarla ahora? Cuadre se cerrará y volverá "
            "a abrirse automáticamente.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if answer != QMessageBox.StandardButton.Yes:
            if result.temp_dir:
                shutil.rmtree(result.temp_dir, ignore_errors=True)
            return

        try:
            subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "cuadre.update_installer",
                    "--pid",
                    str(__import__("os").getpid()),
                    "--wheel",
                    str(result.new_wheel),
                    "--rollback-wheel",
                    str(result.rollback_wheel),
                    "--temp-dir",
                    str(result.temp_dir),
                ],
                close_fds=True,
                start_new_session=(sys.platform != "win32"),
                creationflags=(
                    subprocess.DETACHED_PROCESS
                    | subprocess.CREATE_NEW_PROCESS_GROUP
                    if sys.platform == "win32"
                    else 0
                ),
            )
        except OSError as error:
            shutil.rmtree(result.temp_dir, ignore_errors=True)
            QMessageBox.critical(
                self,
                "Error de actualización",
                f"No fue posible iniciar el instalador: {error}",
            )
            return

        from PySide6.QtWidgets import QApplication
        QApplication.quit()

    def _change_store(self) -> None:
        from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit

        dialog = QDialog(self)
        dialog.setWindowTitle("Cambiar tienda")
        form = QFormLayout(dialog)
        code_input = QLineEdit(self.store_code)
        name_input = QLineEdit(self.store_name)
        form.addRow("Código de tienda:", code_input)
        form.addRow("Nombre de tienda:", name_input)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            save_store_identity(code_input.text(), name_input.text())
        except (StoreConfigError, ValueError) as error:
            QMessageBox.critical(self, "Error de configuración", str(error))
            return

        self.store_code = code_input.text().strip()
        self.store_name = name_input.text().strip()
        self._refresh_header_metadata()


def load_or_request_store_identity(parent: QWidget | None = None) -> tuple[str, str] | None:
    """Load the configured store or request it on first launch."""
    try:
        identity = load_store_identity()
    except StoreConfigError as error:
        QMessageBox.critical(parent, "Error de configuración", str(error))
        return None

    if identity is not None:
        return identity

    from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit

    dialog = QDialog(parent)
    dialog.setWindowTitle("Configuración inicial")
    dialog.setModal(True)
    form = QFormLayout(dialog)
    code_input = QLineEdit()
    name_input = QLineEdit()
    form.addRow("Código de tienda:", code_input)
    form.addRow("Nombre de tienda:", name_input)
    buttons = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
    )
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    form.addRow(buttons)

    while dialog.exec() == QDialog.DialogCode.Accepted:
        try:
            save_store_identity(code_input.text(), name_input.text())
        except (StoreConfigError, ValueError) as error:
            QMessageBox.warning(dialog, "Datos no válidos", str(error))
            continue
        return code_input.text().strip(), name_input.text().strip()

    return None
