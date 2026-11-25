from pathlib import Path

from cuadre import update_installer


def test_install_success(monkeypatch, tmp_path):
    calls = []

    class Result:
        returncode = 0

    def fake_run(command, **kwargs):
        calls.append(command)
        return Result()

    monkeypatch.setattr(update_installer.subprocess, "run", fake_run)

    wheel = tmp_path / "update.whl"
    wheel.touch()

    with (tmp_path / "install.log").open("w") as log:
        assert update_installer.install(wheel, log) is True

    assert calls[0][-1] == str(wheel)


def test_install_failure(monkeypatch, tmp_path):
    class Result:
        returncode = 1

    monkeypatch.setattr(
        update_installer.subprocess,
        "run",
        lambda *args, **kwargs: Result(),
    )

    wheel = tmp_path / "update.whl"
    wheel.touch()

    with (tmp_path / "install.log").open("w") as log:
        assert update_installer.install(wheel, log) is False


def test_main_rolls_back_and_restarts(monkeypatch, tmp_path):
    temp_dir = tmp_path / "update"
    temp_dir.mkdir()

    wheel = temp_dir / "new.whl"
    rollback = temp_dir / "old.whl"
    wheel.touch()
    rollback.touch()

    monkeypatch.setattr(
        update_installer,
        "wait_for_process",
        lambda pid: None,
    )
    monkeypatch.setattr(
        update_installer.Path,
        "home",
        lambda: tmp_path,
    )

    install_results = iter([False, True])
    installed = []

    def fake_install(path, log):
        installed.append(path)
        return next(install_results)

    monkeypatch.setattr(update_installer, "install", fake_install)

    restarted = []
    monkeypatch.setattr(
        update_installer.subprocess,
        "Popen",
        lambda command: restarted.append(command),
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "update_installer",
            "--pid", "1234",
            "--wheel", str(wheel),
            "--rollback-wheel", str(rollback),
            "--temp-dir", str(temp_dir),
        ],
    )

    result = update_installer.main()

    assert result == 1
    assert installed == [wheel, rollback]
    assert len(restarted) == 1
    assert not temp_dir.exists()
