"""Check and download verified Cuadre releases from GitHub."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REPOSITORY = "cp-transfer/cuadre-app"
RELEASE_API = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
USER_AGENT = "Cuadre-App-Updater"
WHEEL_PATTERN = re.compile(r"cuadre_app-(\d+\.\d+\.\d+)-py3-none-any\.whl")


class UpdateCheckError(Exception):
    """Raised when a release cannot be checked or verified."""


@dataclass(frozen=True)
class UpdateInfo:
    installed_version: str
    latest_version: str
    release_url: str
    release_notes: str
    wheel_url: str
    checksum_url: str
    wheel_name: str

    @property
    def available(self) -> bool:
        return _version_tuple(self.latest_version) > _version_tuple(
            self.installed_version
        )


def _version_tuple(value: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", value.strip())
    if not match:
        raise UpdateCheckError(f"Formato de versión no válido: {value}")
    return tuple(int(part) for part in match.groups())


def get_installed_version() -> str:
    try:
        return version("cuadre-app")
    except PackageNotFoundError as error:
        raise UpdateCheckError(
            "No se pudo determinar la versión instalada de Cuadre."
        ) from error


def _request_bytes(url: str, timeout: int = 20) -> bytes:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read()
    except HTTPError as error:
        raise UpdateCheckError(
            f"GitHub respondió con el error HTTP {error.code}."
        ) from error
    except (URLError, TimeoutError, OSError) as error:
        raise UpdateCheckError(
            f"No fue posible conectar con GitHub: {error}"
        ) from error


def check_for_updates(timeout: int = 10) -> UpdateInfo:
    installed = get_installed_version()

    try:
        release = json.loads(_request_bytes(RELEASE_API, timeout).decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise UpdateCheckError(
            "GitHub devolvió una respuesta que no se pudo interpretar."
        ) from error

    if not isinstance(release, dict) or release.get("draft") or release.get("prerelease"):
        raise UpdateCheckError("No se encontró una versión estable válida.")

    tag = release.get("tag_name")
    release_url = release.get("html_url")
    assets = release.get("assets")

    if not isinstance(tag, str) or not isinstance(release_url, str):
        raise UpdateCheckError("La publicación no contiene datos válidos.")

    latest = tag.removeprefix("v")
    _version_tuple(installed)
    _version_tuple(latest)

    if not isinstance(assets, list):
        raise UpdateCheckError("La publicación no contiene archivos descargables.")

    wheel = None
    checksum = None
    trusted_prefix = (
        f"https://github.com/{REPOSITORY}/releases/download/{tag}/"
    )

    for asset in assets:
        if not isinstance(asset, dict):
            continue
        name = asset.get("name")
        url = asset.get("browser_download_url")
        if not isinstance(name, str) or not isinstance(url, str):
            continue
        if not url.startswith(trusted_prefix):
            continue
        if WHEEL_PATTERN.fullmatch(name):
            wheel = (name, url)
        elif name == "SHA256SUMS":
            checksum = url

    if wheel is None or checksum is None:
        raise UpdateCheckError(
            "La versión publicada no incluye el paquete o su checksum."
        )

    wheel_version = WHEEL_PATTERN.fullmatch(wheel[0]).group(1)
    if wheel_version != latest:
        raise UpdateCheckError(
            "La versión del paquete no coincide con la versión publicada."
        )

    return UpdateInfo(
        installed_version=installed,
        latest_version=latest,
        release_url=release_url,
        release_notes=release.get("body") or "",
        wheel_url=wheel[1],
        checksum_url=checksum,
        wheel_name=wheel[0],
    )


def download_update(update: UpdateInfo, destination: Path) -> Path:
    """Download a release wheel and verify it against its SHA256SUMS entry."""
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)

    checksum_data = _request_bytes(update.checksum_url).decode("utf-8")
    expected_hash = None

    for line in checksum_data.splitlines():
        parts = line.strip().split()
        if len(parts) == 2 and parts[1].lstrip("*") == update.wheel_name:
            expected_hash = parts[0].lower()
            break

    if not expected_hash or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
        raise UpdateCheckError("No se encontró un SHA-256 válido para el paquete.")

    wheel_data = _request_bytes(update.wheel_url)
    actual_hash = hashlib.sha256(wheel_data).hexdigest()

    if actual_hash != expected_hash:
        raise UpdateCheckError(
            "El paquete descargado no superó la verificación SHA-256."
        )

    wheel_path = destination / update.wheel_name
    wheel_path.write_bytes(wheel_data)
    return wheel_path


def download_version_wheel(release_version: str, destination: Path) -> Path:
    """Download and verify the wheel for a specific published release."""
    release_url = (
        f"https://api.github.com/repos/{REPOSITORY}/releases/tags/v{release_version}"
    )

    try:
        release = json.loads(_request_bytes(release_url).decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise UpdateCheckError(
            f"No se pudo recuperar la versión anterior {release_version}."
        ) from error

    if not isinstance(release, dict) or release.get("draft") or release.get("prerelease"):
        raise UpdateCheckError(
            f"La versión anterior {release_version} no está disponible."
        )

    tag = release.get("tag_name")
    if tag not in {release_version, f"v{release_version}"}:
        raise UpdateCheckError("La etiqueta de la versión anterior no coincide.")

    assets = release.get("assets")
    if not isinstance(assets, list):
        raise UpdateCheckError("La versión anterior no contiene archivos.")

    wheel = None
    checksum_url = None

    for asset in assets:
        if not isinstance(asset, dict):
            continue

        name = asset.get("name")
        url = asset.get("browser_download_url")

        if not isinstance(name, str) or not isinstance(url, str):
            continue

        trusted_prefix = (
            f"https://github.com/{REPOSITORY}/releases/download/"
        )
        if not url.startswith(trusted_prefix):
            continue

        if name == f"cuadre_app-{release_version}-py3-none-any.whl":
            wheel = (name, url)
        elif name == "SHA256SUMS":
            checksum_url = url

    if wheel is None or checksum_url is None:
        raise UpdateCheckError(
            f"La versión {release_version} no tiene paquete y checksum válidos."
        )

    update = UpdateInfo(
        installed_version=release_version,
        latest_version=release_version,
        release_url=release.get("html_url", ""),
        release_notes="",
        wheel_url=wheel[1],
        checksum_url=checksum_url,
        wheel_name=wheel[0],
    )

    return download_update(update, destination)
