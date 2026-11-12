
"""Per-user store identity configuration for Cuadre."""

import json
import os
import tempfile
from pathlib import Path


class StoreConfigError(Exception):
    """Raised when the saved store identity cannot be read or validated."""


def get_store_config_path() -> Path:
    if os.name == "nt":
        base = os.environ.get("APPDATA")
        if not base:
            raise StoreConfigError(
                "No se encontró la carpeta APPDATA de Windows."
            )
        return Path(base) / "Cuadre" / "store.json"

    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".config"
    return base / "cuadre" / "store.json"


def load_store_identity() -> tuple[str, str] | None:
    path = get_store_config_path()

    if not path.exists():
        return None

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise StoreConfigError(
            f"No se pudo leer {path}: {error}"
        ) from error

    if not isinstance(data, dict) or set(data) != {
        "store_code",
        "store_name",
    }:
        raise StoreConfigError(
            f"El archivo {path} no tiene el formato esperado. "
            "Debe contener únicamente store_code y store_name."
        )

    code = data["store_code"]
    name = data["store_name"]

    if not isinstance(code, str) or not code.strip():
        raise StoreConfigError(
            f"El código de tienda guardado en {path} no es válido."
        )

    if not isinstance(name, str) or not name.strip():
        raise StoreConfigError(
            f"El nombre de tienda guardado en {path} no es válido."
        )

    return code.strip(), name.strip()


def save_store_identity(store_code: str, store_name: str) -> Path:
    if not isinstance(store_code, str) or not store_code.strip():
        raise ValueError("El código de tienda no puede estar vacío.")

    if not isinstance(store_name, str) or not store_name.strip():
        raise ValueError("El nombre de tienda no puede estar vacío.")

    path = get_store_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "store_code": store_code.strip(),
        "store_name": store_name.strip(),
    }

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=".store-",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            json.dump(payload, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
            temporary_path = Path(temporary.name)

        temporary_path.replace(path)

    except OSError as error:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

        raise StoreConfigError(
            f"No se pudo guardar la configuración en {path}: {error}"
        ) from error

    return path
