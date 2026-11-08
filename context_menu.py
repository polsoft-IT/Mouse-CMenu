from __future__ import annotations

import logging

from PySide6.QtCore import QFileInfo, QPoint, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFileIconProvider,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QStyle,
    QStyleOptionMenuItem,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)

from app_launcher import launch_application
from app_icon import gear_icon

logger = logging.getLogger(__name__)

ICON_TEXT_GAP = "  "


class ContextMenu:
    def __init__(self, controller: object) -> None:
        self.controller = controller
        self.menu = QMenu()
        self.file_icon_provider = QFileIconProvider()

    def show_at(self, position: QPoint) -> None:
        settings = self.controller.settings
        polish = settings.language == "pl"
        self.menu.clear()
        self._add_entries(self.menu, settings.menu_entries, settings.show_app_icons)
        if settings.menu_entries:
            self.menu.addSeparator()
        if settings.show_toolbar:
            self._add_divided_spacer()
        self._add_settings_entry("Ustawienia" if polish else "Settings")
        self.menu.popup(position)

    def _row_height(self) -> int:
        option = QStyleOptionMenuItem()
        option.menuItemType = QStyleOptionMenuItem.MenuItemType.Normal
        option.font = self.menu.font()
        return self.menu.style().sizeFromContents(
            QStyle.ContentsType.CT_MenuItem, option, QSize(0, 0), self.menu
        ).height()

    def _add_divided_spacer(self) -> None:
        widget = QWidget(self.menu)
        height = self._row_height()
        widget.setFixedHeight(height)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Styl dla przycisków wewnątrz menu
        button_style = """
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.08);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.15);
            }
        """
        
        for index in range(4):
            if index > 0:
                line = QFrame(widget)
                line.setFrameShape(QFrame.Shape.VLine)
                line.setFrameShadow(QFrame.Shadow.Sunken)
                line.setFixedWidth(1)
                line.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
                layout.addWidget(line)
            
            btn = QPushButton("", widget)
            btn.setFlat(True)
            btn.setFixedHeight(height)
            btn.setStyleSheet(button_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # Każdy przycisk może mieć w przyszłości inną funkcję
            btn.clicked.connect(self.menu.close)
            layout.addWidget(btn, 1)

        action = QWidgetAction(self.menu)
        action.setDefaultWidget(widget)
        self.menu.addAction(action)

    def _add_settings_entry(self, label: str) -> None:
        widget = QWidget(self.menu)
        widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(4)
        layout.addStretch(1)
        icon_label = QLabel(widget)
        icon_label.setPixmap(gear_icon().pixmap(16, 16))
        layout.addWidget(icon_label)
        layout.addWidget(QLabel(label, widget))
        layout.addStretch(1)

        action = QWidgetAction(self.menu)
        action.setDefaultWidget(widget)
        self.menu.addAction(action)
        action.triggered.connect(self.controller.open_settings)

    def contains(self, position: QPoint) -> bool:
        return self._menu_contains(self.menu, position)

    def _menu_contains(self, menu: QMenu, position: QPoint) -> bool:
        if menu.isVisible() and menu.frameGeometry().contains(position):
            return True
        for action in menu.actions():
            submenu = action.menu()
            if submenu is not None and self._menu_contains(submenu, position):
                return True
        return False

    def _add_entries(
        self,
        parent_menu: QMenu,
        entries: tuple[object, ...],
        show_app_icons: bool,
    ) -> None:
        for entry in entries:
            if entry.kind == "submenu":
                submenu = parent_menu.addMenu(entry.label)
                self._add_entries(submenu, entry.children, show_app_icons)
            else:
                label = f"{ICON_TEXT_GAP}{entry.label}" if show_app_icons else entry.label
                action = parent_menu.addAction(label)
                if show_app_icons:
                    icon = QIcon(entry.icon) if entry.icon else QIcon()
                    if icon.isNull():
                        icon = self.file_icon_provider.icon(QFileInfo(entry.command))
                    action.setIcon(icon)
                action.triggered.connect(
                    lambda _checked=False, command=entry.command: self._launch_application(command)
                )

    def _launch_application(self, command: str) -> None:
        try:
            launch_application(command)
        except (OSError, ValueError):
            logger.exception("Could not launch menu application: %s", command)