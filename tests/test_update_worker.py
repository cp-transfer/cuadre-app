from pathlib import Path

import cuadre.update_worker as worker_module
from cuadre.update_worker import UpdateWorker
from cuadre.updater import UpdateInfo, UpdateCheckError


def test_worker_cleans_temp_directory_when_download_fails(monkeypatch):
    update = UpdateInfo(
        installed_version="1.0.0",
        latest_version="1.0.1",
        release_url="https://github.com/cp-transfer/cuadre-app/releases/tag/v1.0.1",
        release_notes="",
        wheel_url="https://github.com/cp-transfer/cuadre-app/releases/download/v1.0.1/wheel.whl",
        checksum_url="https://github.com/cp-transfer/cuadre-app/releases/download/v1.0.1/SHA256SUMS",
        wheel_name="cuadre_app-1.0.1-py3-none-any.whl",
    )

    temp_dir = Path("/tmp/cuadre-worker-test")
    temp_dir.mkdir(exist_ok=True)

    monkeypatch.setattr(worker_module, "check_for_updates", lambda: update)
    monkeypatch.setattr(worker_module.tempfile, "mkdtemp", lambda **kwargs: str(temp_dir))
    monkeypatch.setattr(
        worker_module,
        "download_update",
        lambda *args: (_ for _ in ()).throw(UpdateCheckError("download failed")),
    )

    worker = UpdateWorker()
    errors = []
    worker.failed.connect(errors.append)
    worker.run()

    assert errors == ["download failed"]
    assert not temp_dir.exists()
