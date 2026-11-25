"""Background release checking and verified package downloads."""

from dataclasses import dataclass
from pathlib import Path
import shutil
import tempfile

from PySide6.QtCore import QThread, Signal

from cuadre.updater import (
    UpdateInfo,
    check_for_updates,
    download_update,
    download_version_wheel,
)


@dataclass(frozen=True)
class UpdateTaskResult:
    update: UpdateInfo
    new_wheel: Path | None = None
    rollback_wheel: Path | None = None
    temp_dir: Path | None = None


class UpdateWorker(QThread):
    completed = Signal(object)
    failed = Signal(str)

    def run(self) -> None:
        temp_dir = None

        try:
            update = check_for_updates()

            if not update.available:
                self.completed.emit(UpdateTaskResult(update=update))
                return

            temp_dir = Path(tempfile.mkdtemp(prefix="cuadre-update-"))

            new_wheel = download_update(update, temp_dir)
            rollback_wheel = download_version_wheel(
                update.installed_version,
                temp_dir,
            )

            self.completed.emit(
                UpdateTaskResult(
                    update=update,
                    new_wheel=new_wheel,
                    rollback_wheel=rollback_wheel,
                    temp_dir=temp_dir,
                )
            )

        except Exception as error:
            if temp_dir is not None:
                shutil.rmtree(temp_dir, ignore_errors=True)
            self.failed.emit(str(error))
