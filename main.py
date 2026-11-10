from __future__ import annotations

import sys

from PySide6.QtCore import QObject, QPoint, QRectF, Qt, Slot
from PySide6.QtGui import (QColor, QCursor, QIcon, QPainter, QPainterPath, QPixmap)
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

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
        polish = self.settings.language == "pl"
        dialog = _AboutDialog(polish, self)
        dialog.exec()

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


APP_VERSION = "1.2.0"


class _IconBadge(QWidget):
    """Rounded card behind the app icon drawn with a subtle gradient."""

    def __init__(self, icon: QIcon, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._icon = icon
        self.setFixedSize(84, 84)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(1.0, 1.0, self.width() - 2.0, self.height() - 2.0)
        path = QPainterPath()
        path.addRoundedRect(rect, 22.0, 22.0)
        painter.fillPath(path, QColor("#2D4B7C"))
        size = round(min(rect.width(), rect.height()) * 0.66)
        pixmap = self._icon.pixmap(size, size)
        x = (self.width() - pixmap.width()) / 2.0
        y = (self.height() - pixmap.height()) / 2.0
        painter.drawPixmap(round(x), round(y), pixmap)
        painter.end()


class _AboutDialog(QDialog):
    def __init__(self, polish: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(("O programie Mouse CMenu" if polish else "About Mouse CMenu"))
        self.setWindowIcon(app_icon())
        self.setModal(True)
        self.setFixedWidth(420)

        version_label = QLabel("<b style='font-size:20pt'>Mouse CMenu</b>")
        version_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        version_text = QLabel(f"Wersja {APP_VERSION}" if polish else f"Version {APP_VERSION}")
        version_text.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        version_text.setStyleSheet("color: palette(mid);")

        description = QLabel(
            "Lekka aplikacja w zasobniku do uruchamiania własnego menu aplikacji skrótem myszy."
            if polish
            else "A lightweight tray app for opening a custom app menu with a mouse shortcut."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        rows = (
            (("Autor", "Author"), "Sebastian Januchowski"),
            (("Firma", "Company"), "polsoft.ITS™"),
            (("E-mail", "Email"), "polsoft.its@mail.com"),
            (("GitHub", "GitHub"), "https://github.com/polsoft-it"),
        )

        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)
        for (label_pl, label_en), value in rows:
            row = QHBoxLayout()
            name = QLabel(f"{label_pl if polish else label_en}:")
            name.setStyleSheet("font-weight: bold;")
            link = QLabel(value)
            if label_pl in ("E-mail", "GitHub"):
                if label_pl == "E-mail":
                    link.setText(f"<a href='mailto:{value}'>{value}</a>")
                else:
                    link.setText(f"<a href='{value}'>{value}</a>")
                link.setOpenExternalLinks(True)
            row.addWidget(name)
            row.addWidget(link, 1)
            info_layout.addLayout(row)

        close_button = QPushButton("Zamknij" if polish else "Close")
        close_button.setDefault(True)
        close_button.clicked.connect(self.accept)
        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(close_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(14)
        header = QHBoxLayout()
        header.addStretch(1)
        header.addWidget(_IconBadge(app_icon()))
        header.addStretch(1)
        layout.addLayout(header)
        layout.addWidget(version_label)
        layout.addWidget(version_text)
        layout.addWidget(description)
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background: palette(mid); border: none;")
        layout.addWidget(separator)
        layout.addLayout(info_layout)
        layout.addSpacing(8)
        layout.addLayout(button_row)


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