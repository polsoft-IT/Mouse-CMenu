from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QLockFile, QStandardPaths


class SingleInstanceGuard:
    def __init__(self, lock_path: Path | None = None) -> None:
        if lock_path is None:
            config_dir = Path(
                QStandardPaths.writableLocation(
                    QStandardPaths.StandardLocation.AppConfigLocation
                )
            )
            lock_path = config_dir / "instance.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock_file = QLockFile(str(lock_path))
        self.lock_file.setStaleLockTime(0)
        self._acquired = False

    def acquire(self) -> bool:
        if not self._acquired:
            self._acquired = self.lock_file.tryLock(0)
        return self._acquired

    def close(self) -> None:
        if self._acquired:
            self.lock_file.unlock()
            self._acquired = False