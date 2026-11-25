import hashlib

import pytest

from cuadre import updater


def make_update():
    return updater.UpdateInfo(
        installed_version="1.0.0",
        latest_version="1.1.0",
        release_url="https://github.com/cp-transfer/cuadre-app/releases/tag/v1.1.0",
        release_notes="Test",
        wheel_url="https://github.com/cp-transfer/cuadre-app/releases/download/v1.1.0/package.whl",
        checksum_url="https://github.com/cp-transfer/cuadre-app/releases/download/v1.1.0/SHA256SUMS",
        wheel_name="cuadre_app-1.1.0-py3-none-any.whl",
    )


def test_download_update_verifies_checksum(monkeypatch, tmp_path):
    update = make_update()
    wheel_data = b"test wheel content"
    checksum = hashlib.sha256(wheel_data).hexdigest()

    responses = iter([
        f"{checksum}  {update.wheel_name}".encode(),
        wheel_data,
    ])

    monkeypatch.setattr(
        updater,
        "_request_bytes",
        lambda url, timeout=20: next(responses),
    )

    result = updater.download_update(update, tmp_path)

    assert result.read_bytes() == wheel_data
    assert result.name == update.wheel_name


def test_download_update_rejects_invalid_checksum(monkeypatch, tmp_path):
    update = make_update()

    responses = iter([
        f"{'0' * 64}  {update.wheel_name}".encode(),
        b"tampered wheel",
    ])

    monkeypatch.setattr(
        updater,
        "_request_bytes",
        lambda url, timeout=20: next(responses),
    )

    with pytest.raises(updater.UpdateCheckError, match="SHA-256"):
        updater.download_update(update, tmp_path)

    assert not (tmp_path / update.wheel_name).exists()
