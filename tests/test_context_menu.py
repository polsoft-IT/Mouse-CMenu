import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QMenu

from context_menu import ContextMenu
from settings_store import MenuEntry


class ContextMenuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_icon_setting_controls_application_actions_in_submenus(self) -> None:
        entries = (
            MenuEntry(
                kind="submenu",
                label="Tools",
                children=(MenuEntry(kind="app", label="Example", command="example.exe"),),
            ),
        )
        icon = QIcon(QPixmap(16, 16))

        for show_icons in (False, True):
            with self.subTest(show_icons=show_icons):
                with patch("context_menu.QFileIconProvider") as provider_type:
                    provider_type.return_value.icon.return_value = icon
                    context_menu = ContextMenu(object())
                    menu = QMenu()
                    context_menu._add_entries(menu, entries, show_icons)

                action = menu.actions()[0].menu().actions()[0]
                self.assertEqual(action.icon().isNull(), not show_icons)
                self.assertEqual(provider_type.return_value.icon.called, show_icons)
                menu.deleteLater()

    def test_custom_icon_is_used_in_context_menu(self) -> None:
        with TemporaryDirectory() as directory:
            icon_path = Path(directory) / "custom.png"
            QPixmap(16, 16).save(str(icon_path))
            entry = MenuEntry(
                kind="app",
                label="Example",
                command="example.exe",
                icon=str(icon_path),
            )
            with patch("context_menu.QFileIconProvider") as provider_type:
                context_menu = ContextMenu(object())
                menu = QMenu()
                context_menu._add_entries(menu, (entry,), True)

            self.assertFalse(menu.actions()[0].icon().isNull())
            provider_type.return_value.icon.assert_not_called()
            menu.deleteLater()


if __name__ == "__main__":
    unittest.main()