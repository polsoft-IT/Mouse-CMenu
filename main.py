from __future__ import annotations

import sys

from PySide6.QtCore import QObject, QPoint, Qt, Slot
from PySide6.QtGui import QCursor, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon

from app_icon import app_icon
from context_menu import ContextMenu
from mouse_shortcut import MouseShortcutService
from settings_dialog import SettingsDialog
from settings_store import SettingsStore
from single_instance import SingleInstanceGuard


class TrayApplication(QObject):
    def __init__(self, app: QApplication) -> None:
        super().__init__(app)
        self.app = app
        self.store = SettingsStore()
        self.settings = self.store.load()
        self.tray = QSystemTrayIcon(self._icon(), app)
        self.tray.setToolTip("Mouse CMenu")
        self.tray_menu = QMenu()
        self.settings_action = self.tray_menu.addAction("Settings")
        self.about_action = self.tray_menu.addAction("About")
        self.tray_menu.addSeparator()
        self.exit_action = self.tray_menu.addAction("Exit")
        self.tray.setContextMenu(self.tray_menu)
        self.settings_action.triggered.connect(self.open_settings)
        self.about_action.triggered.connect(self.show_about)
        self.exit_action.triggered.connect(self.quit)
        self.tray.activated.connect(self._tray_activated)
        self.context_menu = ContextMenu(self)
        self.context_menu.menu.setWindowIcon(self._icon())
        self.mouse_service = MouseShortcutService(self.settings.shortcut)
        self._skip_next_request = False
        self.mouse_service.menu_requested.connect(
            self.show_context_menu,
            Qt.ConnectionType.QueuedConnection,
        )
        self.mouse_service.mouse_pressed.connect(
            self._on_mouse_pressed,
            Qt.ConnectionType.QueuedConnection,
        )
        self.mouse_service.start()
        self._refresh_tray_menu()
        self.tray.show()

    def _icon(self) -> QIcon:
        return app_icon()

    def _tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.open_settings()

    def _refresh_tray_menu(self) -> None:
        polish = self.settings.language != "en"
        self.settings_action.setText("Ustawienia" if polish else "Settings")
        self.about_action.setText("O programie" if polish else "About")
        self.exit_action.setText("Zamknij" if polish else "Exit")

    def open_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self.store, self.mouse_service)
        dialog.exec()
        self.settings = self.store.load()
        self._refresh_tray_menu()

    def show_about(self) -> None:
        polish = self.settings.language == "pl"
        title = "O programie Mouse CMenu" if polish else "About Mouse CMenu"
        description = (
            "Lekka aplikacja w zasobniku do uruchamiania własnego menu aplikacji skrótem myszy."
            if polish
            else "A lightweight tray app for opening a custom app menu with a mouse shortcut."
        )
        details = (
            "Autor: Sebastian Januchowski\n"
            "Firma: polsoft.ITS™\n"
            "E-mail: polsoft.its@mail.com\n"
            "GitHub: https://github.com/polsoft-it"
            if polish
            else "Author: Sebastian Januchowski\n"
            "Company: polsoft.ITS™\n"
            "Email: polsoft.its@mail.com\n"
            "GitHub: https://github.com/polsoft-it"
        )
        QMessageBox.about(None, title, f"{description}\n\n{details}")

    @Slot(int, int, bool)
    def _on_mouse_pressed(self, x: int, y: int, triggered: bool) -> None:
        menu = self.context_menu.menu
        if not menu.isVisible():
            return
        position = QPoint(x, y)
        if self.context_menu.contains(position):
            return
        menu.hide()
        if triggered:
            self._skip_next_request = True

    @Slot()
    def show_context_menu(self) -> None:
        if self._skip_next_request:
            self._skip_next_request = False
            return
        if self.context_menu.menu.isVisible():
            return
        self.context_menu.show_at(QCursor.pos())

    def quit(self) -> None:
        self.tray.hide()
        self.app.quit()

    def shutdown(self) -> None:
        self.mouse_service.stop()


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Mouse CMenu")
    app.setWindowIcon(app_icon())
    app.setQuitOnLastWindowClosed(False)

    instance_guard = SingleInstanceGuard()
    if not instance_guard.acquire():
        return 0

    try:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "Mouse CMenu", "The Windows system tray is unavailable.")
            return 1

        tray_app = TrayApplication(app)
        app.aboutToQuit.connect(tray_app.shutdown)
        return app.exec()
    finally:
        instance_guard.close()


if __name__ == "__main__":
    raise SystemExit(main())