import pytest
from PySide6.QtWidgets import QApplication

from cuadre.gui.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_update_action_is_inside_configuration_menu(qapp):
    window = MainWindow("05", "LLUVIA")

    settings_menu = next(
        action.menu()
        for action in window.menuBar().actions()
        if action.text() == "Configuración"
    )

    action_names = [
        action.text()
        for action in settings_menu.actions()
        if not action.isSeparator()
    ]

    assert action_names == [
        "Cambiar tienda",
        "Buscar actualizaciones",
    ]

    window.close()
