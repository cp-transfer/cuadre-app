"""NTFY configuration and plain-text reconciliation notifications."""

import json
import os
import tempfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_SERVER_URL = "https://ntfy.sh"
DEFAULT_TOPIC = (
    "Cuadre-Almacen--d47c9a21-8f3b-4e12-9c8d-1a2b3c4d5e6f-store-feed"
)


def get_ntfy_config_path() -> Path:
    if os.name == "nt":
        base = os.environ.get("APPDATA")
        if not base:
            raise RuntimeError("No se encontró la carpeta APPDATA de Windows.")
        return Path(base) / "Cuadre" / "ntfy.json"

    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".config"
    return base / "cuadre" / "ntfy.json"


def load_ntfy_config() -> dict:
    path = get_ntfy_config_path()
    defaults = {
        "server_url": DEFAULT_SERVER_URL,
        "topic": DEFAULT_TOPIC,
    }

    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_name = tempfile.mkstemp(
            prefix=".ntfy-",
            suffix=".tmp",
            dir=path.parent,
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as config_file:
                json.dump(defaults, config_file, indent=2)
                config_file.write("\n")
                config_file.flush()
                os.fsync(config_file.fileno())
            os.replace(temporary_name, path)
        except Exception:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise

    try:
        with path.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(
            f"No fue posible leer la configuración NTFY:\n{path}\n{error}"
        ) from error

    if not isinstance(config, dict):
        raise RuntimeError("La configuración NTFY debe ser un objeto JSON.")

    server_url = config.get("server_url")
    topic = config.get("topic")

    if not isinstance(server_url, str) or not server_url.startswith("https://"):
        raise RuntimeError("La dirección del servidor NTFY no es válida.")

    if (
        not isinstance(topic, str)
        or not topic
        or "/" in topic
        or any(char.isspace() for char in topic)
    ):
        raise RuntimeError("El topic de NTFY no es válido.")

    return {"server_url": server_url.rstrip("/"), "topic": topic}


def send_notification(title: str, message: str) -> str:
    config = load_ntfy_config()
    url = f"{config['server_url']}/{config['topic']}"

    request = Request(
        url,
        data=message.encode("utf-8"),
        headers={
            "Title": title,
            "Priority": "high",
            "Tags": "receipt",
            "Content-Type": "text/plain; charset=utf-8",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=20) as response:
            response.read()
            return f"NTFY respondió correctamente (HTTP {response.status})."
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        raise RuntimeError(
            f"No fue posible enviar la notificación NTFY: {error}"
        ) from error
