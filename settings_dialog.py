from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QFileInfo, QPoint, Qt, Signal
from PySide6.QtGui import QIcon, QKeyEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFileIconProvider,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
from pynput import mouse

from app_icon import app_icon
from autostart import set_run_at_startup
from settings_store import AppSettings, MenuEntry, SettingsStore
from shortcut import SHORTCUT_OPTIONS, normalize_shortcut


TEXT = {
    "en": {
        "title": "Settings",
        "language": "Language",
        "shortcut": "Mouse shortcut",
        "record": "Record with mouse...",
        "menu_items": "Context menu items",
        "show_icons": "Show application icons",
        "show_toolbar": "Show toolbar (4 buttons)",
        "run_at_startup": "Run at system startup",
        "startup_failed": "Could not update the startup setting.",
        "add_app": "Add application",
        "add_submenu": "Add submenu",
        "remove_item": "Remove",
        "choose_app": "Choose application",
        "app_name": "Application name",
        "submenu_name": "Submenu name",
        "name_prompt": "Name:",
        "edit_app": "Edit application",
        "location": "Location",
        "icon": "Icon",
        "browse": "Browse",
        "clear": "Clear",
        "choose_icon": "Choose icon",
        "required_fields": "Name and location are required.",
        "save": "Save",
        "cancel": "Cancel",
        "invalid_app": "The selected path is not a file.",
        "record_title": "Record mouse shortcut",
        "record_message": "Click a mouse button or scroll to assign it. Press Esc to cancel.",
        "close": "Close",
        "failed": "Could not listen for mouse input.",
    },
    "pl": {
        "title": "Ustawienia",
        "language": "Język",
        "shortcut": "Skrót myszy",
        "record": "Nagraj myszą...",
        "menu_items": "Elementy menu kontekstowego",
        "show_icons": "Pokaż ikony aplikacji",
        "show_toolbar": "Pokaż pasek narzędzi (4 przyciski)",
        "run_at_startup": "Uruchamiaj przy starcie systemu",
        "startup_failed": "Nie udało się zmienić ustawienia autostartu.",
        "add_app": "Dodaj aplikację",
        "add_submenu": "Dodaj podmenu",
        "remove_item": "Usuń",
        "choose_app": "Wybierz aplikację",
        "app_name": "Nazwa aplikacji",
        "submenu_name": "Nazwa podmenu",
        "name_prompt": "Nazwa:",
        "edit_app": "Edytuj aplikację",
        "location": "Lokalizacja",
        "icon": "Ikona",
        "browse": "Przeglądaj",
        "clear": "Wyczyść",
        "choose_icon": "Wybierz ikonę",
        "required_fields": "Nazwa i lokalizacja są wymagane.",
        "save": "Zapisz",
        "cancel": "Anuluj",
        "invalid_app": "Wybrana ścieżka nie jest plikiem.",
        "record_title": "Nagraj skrót myszy",
        "record_message": "Kliknij przycisk myszy lub przewiń kółkiem. Esc anuluje.",
        "close": "Zamknij",
        "failed": "Nie można nasłuchiwać myszy.",
    },
}


class ShortcutRecorder(QDialog):
    shortcut_recorded = Signal(str)

    def __init__(self, language: str, parent: QDialog) -> None:
        super().__init__(parent)
        self.language = language
        self.result_key: str | None = None
        self.listener: mouse.Listener | None = None
        text = TEXT[language]
        self.setWindowTitle(text["record_title"])
        self.shortcut_recorded.connect(self._record)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(text["record_message"]))
        self.setModal(True)
        self.listener = mouse.Listener(on_click=self._on_click, on_scroll=self._on_scroll)
        self.listener.start()

    def _record(self, key: str) -> None:
        self.result_key = key
        self.accept()

    def _on_click(self, _x: int, _y: int, button: mouse.Button, pressed: bool) -> None:
        if pressed:
            key = str(button).split(".")[-1].lower()
            if key in {"left", "middle", "right"}:
                self.shortcut_recorded.emit(key)

    def _on_scroll(self, _x: int, _y: int, _dx: int, dy: int) -> None:
        if dy:
            self.shortcut_recorded.emit("wheel_up" if dy > 0 else "wheel_down")

    def closeEvent(self, event: object) -> None:
        if self.listener is not None:
            self.listener.stop()
            self.listener = None
        super().closeEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            return
        super().keyPressEvent(event)

    def done(self, result: int) -> None:
        if self.listener is not None:
            self.listener.stop()
            self.listener = None
        super().done(result)


class EditApplicationDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        language: str,
        label: str,
        command: str,
        icon_path: str,
    ) -> None:
        super().__init__(parent)
        text = TEXT[language]
        self.setWindowTitle(text["edit_app"])
        self.setMinimumWidth(460)
        self.name_edit = QLineEdit(label)
        self.location_edit = QLineEdit(command)
        self.icon_edit = QLineEdit(icon_path)

        location_browse = QPushButton(text["browse"])
        location_browse.clicked.connect(self._browse_location)
        icon_browse = QPushButton(text["browse"])
        icon_browse.clicked.connect(self._browse_icon)
        icon_clear = QPushButton(text["clear"])
        icon_clear.clicked.connect(self.icon_edit.clear)

        form = QFormLayout()
        form.addRow(text["app_name"], self.name_edit)
        form.addRow(text["location"], self._path_row(self.location_edit, location_browse))
        form.addRow(
            text["icon"],
            self._path_row(self.icon_edit, icon_browse, icon_clear),
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(text["save"])
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(text["cancel"])
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _path_row(self, field: QLineEdit, *buttons: QPushButton) -> QWidget:
        row_widget = QWidget(self)
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(field, 1)
        for button in buttons:
            row_layout.addWidget(button)
        return row_widget

    def _browse_location(self) -> None:
        text = TEXT[self.parent().settings.language]
        path, _ = QFileDialog.getOpenFileName(
            self,
            text["choose_app"],
            self.location_edit.text(),
            "Applications and shortcuts (*.exe *.com *.lnk);;All files (*.*)",
        )
        if path:
            self.location_edit.setText(path)

    def _browse_icon(self) -> None:
        text = TEXT[self.parent().settings.language]
        path, _ = QFileDialog.getOpenFileName(
            self,
            text["choose_icon"],
            self.icon_edit.text(),
            "Icon and image files (*.ico *.png *.jpg *.jpeg *.bmp);;All files (*.*)",
        )
        if path:
            self.icon_edit.setText(path)

    @property
    def values(self) -> tuple[str, str, str]:
        return (
            self.name_edit.text().strip(),
            self.location_edit.text().strip(),
            self.icon_edit.text().strip(),
        )

    def accept(self) -> None:
        label, command, _icon_path = self.values
        if not label or not command:
            text = TEXT[self.parent().settings.language]
            QMessageBox.warning(self, text["edit_app"], text["required_fields"])
            return
        super().accept()


class SettingsDialog(QDialog):
    def __init__(self, settings: AppSettings, store: SettingsStore, mouse_service: object) -> None:
        super().__init__()
        self.settings = settings
        self.store = store
        self.mouse_service = mouse_service
        self.file_icon_provider = QFileIconProvider()
        self.setWindowIcon(app_icon())
        self.setMinimumWidth(380)
        self._build_ui()
        self._populate_menu_tree()
        self._refresh_text()

    def _build_ui(self) -> None:
        self.language_label = QLabel()
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Polski", "pl")
        self.language_combo.setCurrentIndex(0 if self.settings.language == "en" else 1)
        self.language_combo.currentIndexChanged.connect(self._language_changed)
        self.language_combo.setMinimumWidth(90)
        self.language_combo.setMaximumWidth(120)

        self.startup_checkbox = QCheckBox()
        self.startup_checkbox.setChecked(self.settings.run_at_startup)
        self.startup_checkbox.toggled.connect(self._startup_changed)

        top_row = QHBoxLayout()
        top_row.addWidget(self.language_label)
        top_row.addWidget(self.language_combo)
        top_row.addSpacing(20)
        top_row.addWidget(self.startup_checkbox)
        top_row.addStretch(1)

        self.shortcut_label = QLabel()
        self.shortcut_combo = QComboBox()
        self.shortcut_combo.setMinimumWidth(180)
        self.shortcut_combo.setMaximumWidth(220)
        self.shortcut_button = QPushButton()
        self.shortcut_button.clicked.connect(self._record_shortcut)
        shortcut_row = QHBoxLayout()
        shortcut_row.addWidget(self.shortcut_combo)
        shortcut_row.addWidget(self.shortcut_button)
        shortcut_row.addStretch(1)

        self.menu_items_label = QLabel()
        self.show_icons_checkbox = QCheckBox()
        self.show_icons_checkbox.setChecked(self.settings.show_app_icons)
        self.show_icons_checkbox.toggled.connect(self._icons_changed)
        self.show_toolbar_checkbox = QCheckBox()
        self.show_toolbar_checkbox.setChecked(self.settings.show_toolbar)
        self.show_toolbar_checkbox.toggled.connect(self._toolbar_changed)
        
        checkbox_row = QHBoxLayout()
        checkbox_row.addWidget(self.show_icons_checkbox)
        checkbox_row.addSpacing(20)
        checkbox_row.addWidget(self.show_toolbar_checkbox)
        checkbox_row.addStretch(1)

        self.menu_tree = QTreeWidget()
        self.menu_tree.setHeaderHidden(True)
        self.menu_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.menu_tree.customContextMenuRequested.connect(self._show_item_context_menu)
        self.menu_tree.setMinimumHeight(180)
        self.add_app_button = QPushButton()
        self.add_app_button.clicked.connect(self._add_application)
        self.add_submenu_button = QPushButton()
        self.add_submenu_button.clicked.connect(self._add_submenu)
        self.remove_item_button = QPushButton()
        self.remove_item_button.clicked.connect(self._remove_menu_item)
        menu_actions = QHBoxLayout()
        menu_actions.addWidget(self.add_app_button)
        menu_actions.addWidget(self.add_submenu_button)
        menu_actions.addWidget(self.remove_item_button)

        self.close_button = QPushButton()
        self.close_button.clicked.connect(self.accept)
        layout = QVBoxLayout(self)
        layout.addLayout(top_row)
        layout.addSpacing(8)
        layout.addWidget(self.shortcut_label)
        layout.addLayout(shortcut_row)
        layout.addSpacing(8)
        layout.addWidget(self.menu_items_label)
        layout.addLayout(checkbox_row)
        layout.addWidget(self.menu_tree, 1)
        layout.addLayout(menu_actions)
        layout.addStretch(1)
        layout.addWidget(self.close_button, alignment=Qt.AlignmentFlag.AlignRight)
        self._fill_shortcut_options()
        self.shortcut_combo.currentIndexChanged.connect(self._shortcut_changed)

    def _fill_shortcut_options(self) -> None:
        current = self.settings.shortcut
        language = self.settings.language
        self.shortcut_combo.blockSignals(True)
        self.shortcut_combo.clear()
        for option in SHORTCUT_OPTIONS:
            label = option.english if language == "en" else option.polish
            self.shortcut_combo.addItem(label, option.key)
        index = self.shortcut_combo.findData(normalize_shortcut(current))
        self.shortcut_combo.setCurrentIndex(max(index, 0))
        self.shortcut_combo.blockSignals(False)

    def _refresh_text(self) -> None:
        text = TEXT[self.settings.language]
        self.setWindowTitle(text["title"])
        self.language_label.setText(text["language"])
        self.shortcut_label.setText(text["shortcut"])
        self.shortcut_button.setText(text["record"])
        self.menu_items_label.setText(text["menu_items"])
        self.show_icons_checkbox.setText(text["show_icons"])
        self.show_toolbar_checkbox.setText(text["show_toolbar"])
        self.startup_checkbox.setText(text["run_at_startup"])
        self.add_app_button.setText(text["add_app"])
        self.add_submenu_button.setText(text["add_submenu"])
        self.remove_item_button.setText(text["remove_item"])
        self.close_button.setText(text["close"])
        self._fill_shortcut_options()

    def _persist(self) -> None:
        self.settings = AppSettings(
            language=self.settings.language,
            shortcut=self.settings.shortcut,
            menu_entries=self._read_menu_entries(),
            show_app_icons=self.show_icons_checkbox.isChecked(),
            run_at_startup=self.startup_checkbox.isChecked(),
            show_toolbar=self.show_toolbar_checkbox.isChecked(),
        )
        self.store.save(self.settings)
        self.mouse_service.set_shortcut(self.settings.shortcut)

    def _icons_changed(self, _checked: bool) -> None:
        self._persist()

    def _toolbar_changed(self, _checked: bool) -> None:
        self._persist()

    def _startup_changed(self, enabled: bool) -> None:
        try:
            set_run_at_startup(enabled)
        except OSError:
            text = TEXT[self.settings.language]
            QMessageBox.warning(self, text["run_at_startup"], text["startup_failed"])
            self.startup_checkbox.blockSignals(True)
            self.startup_checkbox.setChecked(self.settings.run_at_startup)
            self.startup_checkbox.blockSignals(False)
            return
        self._persist()

    def _read_menu_entries(self) -> tuple[MenuEntry, ...]:
        def read_children(parent: QTreeWidget | QTreeWidgetItem) -> tuple[MenuEntry, ...]:
            entries = []
            for index in range(parent.topLevelItemCount() if isinstance(parent, QTreeWidget) else parent.childCount()):
                item = parent.topLevelItem(index) if isinstance(parent, QTreeWidget) else parent.child(index)
                kind = item.data(0, Qt.ItemDataRole.UserRole)
                command = item.data(0, Qt.ItemDataRole.UserRole + 1) or ""
                icon = item.data(0, Qt.ItemDataRole.UserRole + 2) or ""
                entries.append(
                    MenuEntry(
                        kind=kind,
                        label=item.text(0),
                        command=command,
                        children=read_children(item) if kind == "submenu" else (),
                        icon=icon,
                    )
                )
            return tuple(entries)

        return read_children(self.menu_tree)

    def _populate_menu_tree(self) -> None:
        self.menu_tree.clear()

        def add_entries(parent: QTreeWidget | QTreeWidgetItem, entries: tuple[MenuEntry, ...]) -> None:
            for entry in entries:
                item = QTreeWidgetItem([entry.label])
                item.setData(0, Qt.ItemDataRole.UserRole, entry.kind)
                item.setData(0, Qt.ItemDataRole.UserRole + 1, entry.command)
                item.setData(0, Qt.ItemDataRole.UserRole + 2, entry.icon)
                if entry.kind == "app":
                    self._set_application_icon(item, entry.command, entry.icon)
                if isinstance(parent, QTreeWidget):
                    parent.addTopLevelItem(item)
                else:
                    parent.addChild(item)
                if entry.kind == "submenu":
                    add_entries(item, entry.children)

        add_entries(self.menu_tree, self.settings.menu_entries)

    def _set_application_icon(
        self,
        item: QTreeWidgetItem,
        command: str,
        icon_path: str = "",
    ) -> None:
        icon = QIcon(icon_path) if icon_path else QIcon()
        if icon.isNull():
            icon = self.file_icon_provider.icon(QFileInfo(command))
        item.setIcon(0, icon)

    def _target_parent(self) -> QTreeWidget | QTreeWidgetItem:
        selected = self.menu_tree.currentItem()
        if selected is not None and selected.data(0, Qt.ItemDataRole.UserRole) == "submenu":
            return selected
        return self.menu_tree

    def _show_item_context_menu(self, position: QPoint) -> None:
        item = self.menu_tree.itemAt(position)
        if item is None or item.data(0, Qt.ItemDataRole.UserRole) != "app":
            return
        menu = QMenu(self)
        edit_action = menu.addAction(TEXT[self.settings.language]["edit_app"])
        edit_action.triggered.connect(
            lambda _checked=False, target=item: self._edit_application(target)
        )
        menu.exec(self.menu_tree.viewport().mapToGlobal(position))

    def _edit_application(self, item: QTreeWidgetItem) -> None:
        dialog = EditApplicationDialog(
            self,
            self.settings.language,
            item.text(0),
            item.data(0, Qt.ItemDataRole.UserRole + 1) or "",
            item.data(0, Qt.ItemDataRole.UserRole + 2) or "",
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        label, command, icon_path = dialog.values
        item.setText(0, label)
        item.setData(0, Qt.ItemDataRole.UserRole + 1, command)
        item.setData(0, Qt.ItemDataRole.UserRole + 2, icon_path)
        self._set_application_icon(item, command, icon_path)
        self._persist()

    def _add_application(self) -> None:
        text = TEXT[self.settings.language]
        path, _ = QFileDialog.getOpenFileName(
            self,
            text["choose_app"],
            "",
            "Applications and shortcuts (*.exe *.com *.lnk);;All files (*.*)",
        )
        if not path:
            return
        app_name, accepted = QInputDialog.getText(
            self,
            text["app_name"],
            text["name_prompt"],
            text=Path(path).stem,
        )
        if not accepted or not app_name.strip():
            return
        item = QTreeWidgetItem([app_name.strip()])
        item.setData(0, Qt.ItemDataRole.UserRole, "app")
        item.setData(0, Qt.ItemDataRole.UserRole + 1, path)
        item.setData(0, Qt.ItemDataRole.UserRole + 2, "")
        self._set_application_icon(item, path)
        parent = self._target_parent()
        if isinstance(parent, QTreeWidget):
            parent.addTopLevelItem(item)
        else:
            parent.addChild(item)
        self._persist()

    def _add_submenu(self) -> None:
        text = TEXT[self.settings.language]
        name, accepted = QInputDialog.getText(self, text["submenu_name"], text["name_prompt"])
        if not accepted or not name.strip():
            return
        item = QTreeWidgetItem([name.strip()])
        item.setData(0, Qt.ItemDataRole.UserRole, "submenu")
        parent = self._target_parent()
        if isinstance(parent, QTreeWidget):
            parent.addTopLevelItem(item)
        else:
            parent.addChild(item)
        self._persist()

    def _remove_menu_item(self) -> None:
        item = self.menu_tree.currentItem()
        if item is None:
            return
        parent = item.parent()
        if parent is None:
            self.menu_tree.takeTopLevelItem(self.menu_tree.indexOfTopLevelItem(item))
        else:
            parent.removeChild(item)
        self._persist()

    def _language_changed(self, index: int) -> None:
        language = self.language_combo.itemData(index)
        if language in TEXT:
            self.settings = AppSettings(
                language=language,
                shortcut=self.settings.shortcut,
                menu_entries=self.settings.menu_entries,
                show_app_icons=self.settings.show_app_icons,
                run_at_startup=self.settings.run_at_startup,
                show_toolbar=self.settings.show_toolbar,
            )
            self._persist()
            self._refresh_text()

    def _shortcut_changed(self, index: int) -> None:
        shortcut = self.shortcut_combo.itemData(index)
        if shortcut:
            self.settings = AppSettings(
                language=self.settings.language,
                shortcut=shortcut,
                menu_entries=self.settings.menu_entries,
                show_app_icons=self.settings.show_app_icons,
                run_at_startup=self.settings.run_at_startup,
                show_toolbar=self.settings.show_toolbar,
            )
            self._persist()

    def _record_shortcut(self) -> None:
        self.mouse_service.set_enabled(False)
        try:
            recorder = ShortcutRecorder(self.settings.language, self)
            if recorder.exec() == QDialog.DialogCode.Accepted and recorder.result_key:
                self.settings = AppSettings(
                    language=self.settings.language,
                    shortcut=recorder.result_key,
                    menu_entries=self.settings.menu_entries,
                    show_app_icons=self.settings.show_app_icons,
                    run_at_startup=self.settings.run_at_startup,
                    show_toolbar=self.settings.show_toolbar,
                )
                self._refresh_text()
                self._persist()
        finally:
            self.mouse_service.set_enabled(True)
