import unittest

from shortcut import event_matches, normalize_shortcut


class ShortcutTests(unittest.TestCase):
    def test_all_mouse_buttons_are_supported(self) -> None:
        for button in ("left", "middle", "right"):
            with self.subTest(button=button):
                self.assertTrue(event_matches(button, "click", button=button))
                self.assertFalse(event_matches(button, "click", button="left" if button != "left" else "right"))

    def test_scroll_directions_are_supported(self) -> None:
        self.assertTrue(event_matches("wheel_up", "scroll", dy=1))
        self.assertTrue(event_matches("wheel_down", "scroll", dy=-1))
        self.assertFalse(event_matches("wheel_up", "scroll", dy=-1))

    def test_unknown_shortcut_falls_back_to_middle_click(self) -> None:
        self.assertEqual(normalize_shortcut("unknown"), "middle")
        self.assertTrue(event_matches("unknown", "click", button="middle"))


if __name__ == "__main__":
    unittest.main()