import json
import os

import pytest

from cuadre.store_config import (
    StoreConfigError,
    get_store_config_path,
    load_store_identity,
    save_store_identity,
)


def set_test_config_home(tmp_path, monkeypatch):
    if os.name == "nt":
        monkeypatch.setenv("APPDATA", str(tmp_path))
    else:
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

def test_missing_store_config_returns_none(tmp_path, monkeypatch):
    set_test_config_home(tmp_path, monkeypatch)

    assert load_store_identity() is None


def test_store_identity_is_saved_and_loaded(tmp_path, monkeypatch):
    set_test_config_home(tmp_path, monkeypatch)

    path = save_store_identity(" 11 ", " HIPER ")

    config_dir = "Cuadre" if os.name == "nt" else "cuadre"
    assert path == tmp_path / config_dir / "store.json"

    assert json.loads(path.read_text(encoding="utf-8")) == {
        "store_code": "11",
        "store_name": "HIPER",
    }
    assert load_store_identity() == ("11", "HIPER")


def test_corrupt_store_config_raises_instead_of_resetting(
    tmp_path, monkeypatch
):
    set_test_config_home(tmp_path, monkeypatch)

    path = get_store_config_path()
    path.parent.mkdir(parents=True)
    path.write_text("{invalid", encoding="utf-8")

    with pytest.raises(StoreConfigError):
        load_store_identity()


@pytest.mark.parametrize(
    "code,name",
    [
        ("", "HIPER"),
        ("11", "  "),
    ],
)
def test_empty_store_identity_is_rejected(
    code, name, tmp_path, monkeypatch
):
    set_test_config_home(tmp_path, monkeypatch)

    with pytest.raises(ValueError):
        save_store_identity(code, name)
