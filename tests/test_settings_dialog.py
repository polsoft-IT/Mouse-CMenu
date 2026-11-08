import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint
from PySide6.QtGui import QIcon, QPixmap, QShowEvent
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtWidgets import QWidget

from settings_dialog import EditApplicationDialog, SettingsDialog
from settings_store import AppSettings, MenuEntry, SettingsStore


class FakeMouseService:
    def set_shortcut(self, shortcut: str) -> None:
        pass

    def set_enabled(self, enabled: bool) -> None:
        pass


class SettingsDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def _dialog(self, store: SettingsStore) -> SettingsDialog:
        return SettingsDialog(store.load(), store, FakeMouseService())

    def test_language_change_keeps_menu_entries(self) -> None:
        with TemporaryDirectory() as directory:
            store = SettingsStore(Path(directory) / "settings.json")
            store.save(
                AppSettings(
                    show_app_icons=True,
                    run_at_startup=True,
                    menu_entries=(MenuEntry(kind="app", label="Paint", command="C:/Windows/mspaint.exe"),)
                )
            )
            dialog = self._dialog(store)
            self.assertEqual(dialog.language_combo.currentIndex(), 0)

            dialog.language_combo.setCurrentIndex(1)

            self.assertEqual(store.load().language, "pl")
            self.assertEqual(store.load().menu_entries[0].label, "Paint")
            self.assertTrue(store.load().show_app_icons)
            self.assertTrue(store.load().run_at_startup)

    def test_show_icons_checkbox_persists_setting(self) -> None:
        with TemporaryDirectory() as directory:
            store = SettingsStore(Path(directory) / "settings.json")
            dialog = self._dialog(store)

            self.assertFalse(dialog.show_icons_checkbox.isChecked())
            dialog.show_icons_checkbox.setChecked(True)

            self.assertTrue(store.load().show_app_icons)

    def test_startup_checkbox_persists_and_registers_setting(self) -> None:
        with TemporaryDirectory() as directory:
            store = SettingsStore(Path(directory) / "settings.json")
            dialog = self._dialog(store)

            with patch("settings_dialog.set_run_at_startup") as set_autostart:
                dialog.startup_checkbox.setChecked(True)

            set_autostart.assert_called_once_with(True)
            self.assertTrue(store.load().run_at_startup)

    def test_application_context_menu_offers_edit(self) -> None:
        with TemporaryDirectory() as directory:
            store = SettingsStore(Path(directory) / "settings.json")
            store.save(
                AppSettings(
                    menu_entries=(MenuEntry(kind="app", label="Example", command="example.exe"),)
                )
            )
            dialog = self._dialog(store)
            item = dialog.menu_tree.topLevelItem(0)
            fake_menu = unittest.mock.Mock()

            with patch.object(dialog.menu_tree, "itemAt", return_value=item):
                with patch("settings_dialog.QMenu", return_value=fake_menu):
                    dialog._show_item_context_menu(QPoint(1, 1))

            fake_menu.addAction.assert_called_once_with("Edit application")
            fake_menu.exec.assert_called_once()

    def test_edit_application_updates_and_persists_fields(self) -> None:
        with TemporaryDirectory() as directory:
            store = SettingsStore(Path(directory) / "settings.json")
            store.save(
                AppSettings(
                    menu_entries=(MenuEntry(kind="app", label="Old", command="old.exe"),)
                )
            )
            dialog = self._dialog(store)
            item = dialog.menu_tree.topLevelItem(0)
            values = ("New name", "D:/Apps/new.exe", "D:/Icons/new.png")

            with patch("settings_dialog.EditApplicationDialog") as editor_type:
                editor = editor_type.return_value
                editor.exec.return_value = QDialog.DialogCode.Accepted
                editor.values = values
                with patch.object(dialog, "_set_application_icon"):
                    dialog._edit_application(item)

            self.assertEqual(item.text(0), values[0])
            saved_entry = store.load().menu_entries[0]
            self.assertEqual(saved_entry.label, values[0])
            self.assertEqual(saved_entry.command, values[1])
            self.assertEqual(saved_entry.icon, values[2])

    def test_shortcut_change_keeps_menu_entries(self) -> None:
        with TemporaryDirectory() as directory:
            store = SettingsStore(Path(directory) / "settings.json")
            store.save(
                AppSettings(
                    menu_entries=(MenuEntry(kind="app", label="Paint", command="C:/Windows/mspaint.exe"),)
                )
            )
            dialog = self._dialog(store)
            self.assertEqual(dialog.shortcut_combo.currentData(), "middle")

            dialog.shortcut_combo.setCurrentIndex(
                dialog.shortcut_combo.findData("wheel_up")
            )

            self.assertEqual(store.load().shortcut, "wheel_up")
            self.assertEqual(store.load().menu_entries[0].label, "Paint")

    def test_show_event_uses_dialog_event_handler(self) -> None:
        with TemporaryDirectory() as directory:
            store = SettingsStore(Path(directory) / "settings.json")
            dialog = self._dialog(store)

            self.assertTrue(dialog.event(QShowEvent()))

    def test_application_entries_display_file_icons(self) -> None:
        command = "C:/Applications/example.exe"
        icon = QIcon(QPixmap(16, 16))
        with TemporaryDirectory() as directory:
            store = SettingsStore(Path(directory) / "settings.json")
            store.save(
                AppSettings(
                    menu_entries=(MenuEntry(kind="app", label="Example", command=command),)
                )
            )
            with patch("settings_dialog.QFileIconProvider") as provider_type:
                provider_type.return_value.icon.return_value = icon
                dialog = self._dialog(store)

            item = dialog.menu_tree.topLevelItem(0)
            self.assertFalse(item.icon(0).isNull())
            icon_path = provider_type.return_value.icon.call_args.args[0].filePath()
            self.assertEqual(icon_path, command)

    def test_edit_dialog_initializes_path_fields(self) -> None:
        parent = QWidget()
        dialog = EditApplicationDialog(
            parent,
            "en",
            "Example",
            "C:/Apps/example.exe",
            "C:/Icons/example.png",
        )

        self.assertEqual(
            dialog.values,
            ("Example", "C:/Apps/example.exe", "C:/Icons/example.png"),
        )
        dialog.close()
        parent.close()

if __name__ == "__main__":
    unittest.main()
