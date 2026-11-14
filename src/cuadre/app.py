"""Cuadre desktop application entry point."""

import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from cuadre.gui.main_window import MainWindow, load_or_request_store_identity


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Cuadre")
    app.setOrganizationName("CP Company")

    identity = load_or_request_store_identity()
    if identity is None:
        return 1

    window = MainWindow(*identity)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
