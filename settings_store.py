from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QStandardPaths

from shortcut import normalize_shortcut


@dataclass(frozen=True)
class MenuEntry:
    kind: str
    label: str
    command: str = ""
    children: tuple[MenuEntry, ...] = ()
    icon: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "label": self.label,
            "command": self.command,
            "children": [child.to_dict() for child in self.children],
            "icon": self.icon,
        }

    @classmethod
    def from_dict(cls, data: object) -> MenuEntry | None:
        if not isinstance(data, dict):
            return None
        kind = data.get("kind")
        label = data.get("label")
        if not isinstance(kind, str) or kind not in {"app", "submenu"}:
            return None
        if not isinstance(label, str) or not label.strip():
            return None
        command = data.get("command", "")
        if not isinstance(command, str):
            command = ""
        icon = data.get("icon", "")
        if not isinstance(icon, str):
            icon = ""
        raw_children = data.get("children", [])
        children = ()
        if isinstance(raw_children, list):
            children = tuple(
                entry for item in raw_children if (entry := cls.from_dict(item)) is not None
            )
        if kind == "app" and not command:
            return None
        return cls(kind=kind, label=label.strip(), command=command, children=children, icon=icon)


@dataclass(frozen=True)
class AppSettings:
    language: str = "en"
    shortcut: str = "middle"
    menu_entries: tuple[MenuEntry, ...] = ()
    show_app_icons: bool = False
    run_at_startup: bool = False
    show_toolbar: bool = True


class SettingsStore:
    def __init__(self, path: Path | None = None) -> None:
        if path is None:
            config_dir = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation))
            path = config_dir / "settings.json"
        self.path = path

    def load(self) -> AppSettings:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return AppSettings()
        if not isinstance(data, dict):
            return AppSettings()

        language = data.get("language", "en")
        if not isinstance(language, str) or language not in {"en", "pl"}:
            language = "en"
        raw_entries = data.get("menu_entries", [])
        entries = ()
        if isinstance(raw_entries, list):
            entries = tuple(
                entry for item in raw_entries if (entry := MenuEntry.from_dict(item)) is not None
            )
        shortcut = data.get("shortcut", "middle")
        show_app_icons = data.get("show_app_icons", False)
        if not isinstance(show_app_icons, bool):
            show_app_icons = False
        run_at_startup = data.get("run_at_startup", False)
        if not isinstance(run_at_startup, bool):
            run_at_startup = False
        show_toolbar = data.get("show_toolbar", True)
        if not isinstance(show_toolbar, bool):
            show_toolbar = True
        return AppSettings(
            language=language,
            shortcut=normalize_shortcut(shortcut),
            menu_entries=entries,
            show_app_icons=show_app_icons,
            run_at_startup=run_at_startup,
            show_toolbar=show_toolbar,
        )

    def save(self, settings: AppSettings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "language": settings.language,
            "shortcut": normalize_shortcut(settings.shortcut),
            "menu_entries": [entry.to_dict() for entry in settings.menu_entries],
            "show_app_icons": settings.show_app_icons,
            "run_at_startup": settings.run_at_startup,
            "show_toolbar": settings.show_toolbar,
        }
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f"{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temp_file:
                temp_path = Path(temp_file.name)
                json.dump(data, temp_file, indent=2)
                temp_file.flush()
                os.fsync(temp_file.fileno())
            os.replace(temp_path, self.path)
        except OSError:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
            raise