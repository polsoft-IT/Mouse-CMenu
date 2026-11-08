from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ShortcutOption:
    key: str
    english: str
    polish: str


SHORTCUT_OPTIONS = (
    ShortcutOption("left", "Left mouse button", "Lewy przycisk myszy"),
    ShortcutOption("middle", "Middle mouse button", "Środkowy przycisk myszy"),
    ShortcutOption("right", "Right mouse button", "Prawy przycisk myszy"),
    ShortcutOption("wheel_up", "Scroll up", "Przewijanie w górę"),
    ShortcutOption("wheel_down", "Scroll down", "Przewijanie w dół"),
)

SHORTCUT_KEYS = {option.key for option in SHORTCUT_OPTIONS}


def normalize_shortcut(value: object) -> str:
    return value if isinstance(value, str) and value in SHORTCUT_KEYS else "middle"


def event_matches(shortcut: str, event_type: str, button: object | None = None, dy: int = 0) -> bool:
    shortcut = normalize_shortcut(shortcut)
    if event_type == "click" and button is not None:
        button_name = str(button).split(".")[-1].lower()
        return shortcut == button_name and shortcut in {"left", "middle", "right"}
    if event_type == "scroll":
        return (shortcut == "wheel_up" and dy > 0) or (shortcut == "wheel_down" and dy < 0)
    return False