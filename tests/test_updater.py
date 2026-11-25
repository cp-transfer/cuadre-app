import json
from io import BytesIO

import pytest

from cuadre import updater


def release_payload(version):
    return {
        "tag_name": f"v{version}",
        "html_url": (
            f"https://github.com/cp-transfer/cuadre-app/releases/tag/v{version}"
        ),
        "body": "Correcciones y mejoras.",
        "draft": False,
        "prerelease": False,
        "assets": [
            {
                "name": f"cuadre_app-{version}-py3-none-any.whl",
                "browser_download_url": (
                    f"https://github.com/cp-transfer/cuadre-app/releases/download/"
                    f"v{version}/cuadre_app-{version}-py3-none-any.whl"
                ),
            },
            {
                "name": "SHA256SUMS",
                "browser_download_url": (
                    f"https://github.com/cp-transfer/cuadre-app/releases/download/"
                    f"v{version}/SHA256SUMS"
                ),
            },
        ],
    }


def mock_release(monkeypatch, payload):
    monkeypatch.setattr(
        updater,
        "urlopen",
        lambda request, timeout: BytesIO(json.dumps(payload).encode()),
    )


def test_detects_newer_release(monkeypatch):
    monkeypatch.setattr(updater, "get_installed_version", lambda: "1.0.0")
    mock_release(monkeypatch, release_payload("1.1.0"))

    result = updater.check_for_updates()

    assert result.installed_version == "1.0.0"
    assert result.latest_version == "1.1.0"
    assert result.available is True
    assert result.wheel_name == "cuadre_app-1.1.0-py3-none-any.whl"
    assert result.release_notes == "Correcciones y mejoras."


def test_reports_when_already_on_latest_release(monkeypatch):
    monkeypatch.setattr(updater, "get_installed_version", lambda: "1.0.0")
    mock_release(monkeypatch, release_payload("1.0.0"))

    result = updater.check_for_updates()

    assert result.installed_version == "1.0.0"
    assert result.latest_version == "1.0.0"
    assert result.available is False


def test_rejects_release_without_assets(monkeypatch):
    monkeypatch.setattr(updater, "get_installed_version", lambda: "1.0.0")
    payload = release_payload("1.1.0")
    payload["assets"] = []
    mock_release(monkeypatch, payload)

    with pytest.raises(updater.UpdateCheckError):
        updater.check_for_updates()


def test_rejects_release_without_checksum(monkeypatch):
    monkeypatch.setattr(updater, "get_installed_version", lambda: "1.0.0")
    payload = release_payload("1.1.0")
    payload["assets"] = payload["assets"][:1]
    mock_release(monkeypatch, payload)

    with pytest.raises(updater.UpdateCheckError):
        updater.check_for_updates()


def test_rejects_release_assets_from_external_urls(monkeypatch):
    release = release_payload("1.0.1")
    for asset in release["assets"]:
        asset["browser_download_url"] = (
            "https://example.com/" + asset["name"]
        )

    monkeypatch.setattr(
        "cuadre.updater.get_installed_version",
        lambda: "1.0.0",
    )
    monkeypatch.setattr(
        "cuadre.updater._request_bytes",
        lambda *args, **kwargs: json.dumps(release).encode(),
    )

    with pytest.raises(updater.UpdateCheckError):
        updater.check_for_updates()


def test_rejects_rollback_release_with_mismatched_tag(monkeypatch, tmp_path):
    release = release_payload("1.0.0")
    release["tag_name"] = "v9.9.9"

    monkeypatch.setattr(
        "cuadre.updater._request_bytes",
        lambda *args, **kwargs: json.dumps(release).encode(),
    )

    with pytest.raises(updater.UpdateCheckError):
        updater.download_version_wheel("1.0.0", tmp_path)
