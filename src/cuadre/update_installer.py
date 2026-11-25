"""Install a verified Cuadre wheel after the GUI process exits."""

from __future__ import annotations

import argparse
import ctypes
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


def wait_for_process(pid: int) -> None:
    if os.name == "nt":
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

        kernel32.OpenProcess.argtypes = [
            ctypes.c_uint32,
            ctypes.c_int,
            ctypes.c_uint32,
        ]
        kernel32.OpenProcess.restype = ctypes.c_void_p

        kernel32.WaitForSingleObject.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        kernel32.WaitForSingleObject.restype = ctypes.c_uint32

        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
        kernel32.CloseHandle.restype = ctypes.c_int

        handle = kernel32.OpenProcess(0x00100000, False, pid)

        if not handle:
            error = ctypes.get_last_error()
            raise OSError(error, "Could not open Cuadre process")

        try:
            result = kernel32.WaitForSingleObject(handle, 0xFFFFFFFF)
            if result != 0:
                raise OSError("Could not wait for Cuadre process to exit")
        finally:
            kernel32.CloseHandle(handle)

        return

    while True:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        except PermissionError as error:
            raise OSError("Cannot verify Cuadre process termination") from error
        time.sleep(0.25)


def install(wheel: Path, log) -> bool:
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--no-deps",
                "--force-reinstall",
                str(wheel),
            ],
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
        return result.returncode == 0
    except OSError as error:
        log.write(f"Installation process could not start: {error}\n")
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--rollback-wheel", type=Path, required=True)
    parser.add_argument("--temp-dir", type=Path, required=True)
    args = parser.parse_args()

    log_dir = Path.home() / ".cache" / "cuadre"
    if os.name == "nt":
        log_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Cuadre"

    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "update.log"

    try:
        wait_for_process(args.pid)
    except OSError as error:
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"Could not confirm application shutdown: {error}\n")
        return 1

    with log_path.open("a", encoding="utf-8") as log:
        log.write("\n--- Cuadre update ---\n")

        success = install(args.wheel, log)

        if success:
            log.write("Update installed successfully.\n")
        else:
            log.write("Update failed. Restoring previous version.\n")
            rollback_ok = install(args.rollback_wheel, log)
            log.write(
                "Rollback successful.\n"
                if rollback_ok
                else "CRITICAL: rollback failed.\n"
            )

    try:
        subprocess.Popen([sys.executable, "-m", "cuadre"])
    except OSError as error:
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"Could not restart Cuadre: {error}\n")

    shutil.rmtree(args.temp_dir, ignore_errors=True)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
