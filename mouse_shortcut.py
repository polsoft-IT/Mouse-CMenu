from __future__ import annotations

import time

from PySide6.QtCore import QObject, Signal

from shortcut import event_matches


class MouseShortcutService(QObject):
    menu_requested = Signal()
    mouse_pressed = Signal(int, int, bool)

    def __init__(self, shortcut: str) -> None:
        super().__init__()
        self.shortcut = shortcut
        self.enabled = True
        self.listener = None
        self._last_trigger = 0.0

    def start(self) -> None:
        try:
            from pynput import mouse
        except ImportError as error:
            raise RuntimeError("Install the application dependencies from requirements.txt.") from error

        self.listener = mouse.Listener(on_click=self._on_click, on_scroll=self._on_scroll)
        self.listener.start()

    def stop(self) -> None:
        if self.listener is not None:
            self.listener.stop()
            self.listener = None

    def set_shortcut(self, shortcut: str) -> None:
        self.shortcut = shortcut

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def _on_click(self, x: int, y: int, button: object, pressed: bool) -> None:
        if not pressed:
            return
        triggered = self._should_trigger("click", button=button)
        if self.enabled:
            self.mouse_pressed.emit(x, y, triggered)
        if triggered:
            self.menu_requested.emit()

    def _on_scroll(self, _x: int, _y: int, _dx: int, dy: int) -> None:
        if self._should_trigger("scroll", dy=dy):
            self.menu_requested.emit()

    def _should_trigger(self, event_type: str, button: object | None = None, dy: int = 0) -> bool:
        if not self.enabled or not event_matches(self.shortcut, event_type, button, dy):
            return False

        now = time.monotonic()
        if now - self._last_trigger < 0.45:
            return False
        self._last_trigger = now
        return True